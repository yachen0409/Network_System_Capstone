import socket
import threading
import time
import os
from datetime import datetime
import json
import base64
from QUIC import quic_server
class ClientHandler():
    def __init__(self, client, address, static_path) -> None:
        self.client = client
        # self.client.settimeout(5)
        self.address = address
        self.alive = True
        self.static_path = static_path
        self.filenames = os.listdir(self.static_path)
        self.client_threads = []
        self.__recv_loop()
    def __recv_loop(self):
        while True:
            try:
                stream_id, recv_bytes, flag = self.client.recv()
                client_thread = threading.Thread(target=self.handle_request, args=(stream_id, recv_bytes,))
                self.client_threads.append(client_thread)
                client_thread.start()
            except:
                for thread in self.client_threads:
                    thread.join()
                self.alive = False 
                self.client.close()
                print('catch socket close 1!')
                break
    
    def parse_request(self, origin_request):
        request = {
            'type': None, 
            'length': None,
            'payload': None, 
        }
        request['type'] = origin_request[0]
        request['length'] = int.from_bytes(origin_request[1:5], byteorder='big')
        request['payload'] = origin_request[5:]
        return request
    def parse_payload(self, origin_payload):
        item_list = origin_payload.split('\r\n')
        payload = {key: val for item in item_list for key, val in [item.split(': ')]}
        return payload
    def parse_get(self, stream_id, payload):
        path = payload['path']
        if path == "/":
            # print(self.static_path)
            status = '200 OK'
            content_type = 'text/html'
            header_payload = f'status: {status}\r\ncontent-type: {content_type}' #\r\ncontent-length: {content_length}
            header_response = {
                'type': 1,
                'length': len(header_payload),
                'payload': header_payload,
            }
            self.send_response(stream_id, header_response, False)
            filenames = self.filenames
            html_content = f"""<html><header></header>
                                <body>
                                    <a href=\"/static/{filenames[0]}\">{filenames[0]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[1]}\">{filenames[1]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[2]}\">{filenames[2]}</a>
                                </body></html>"""
            data_response = {
                'type': 0,
                'length': len(html_content),
                'payload': html_content,
            }
            self.send_response(stream_id, data_response, True)
        else:
            sub_filename = (path.split('/', 1)[1]).split('/')
            # print(sub_filename)
            if(sub_filename[0] == 'static' and sub_filename[1] in self.filenames):
                # print('send back', sub_filename[1])
                print(f"{self.address[0]} - - {datetime.now().strftime('%H:%M:%S')} \"GET {sub_filename[1]}\"")
                with open(f"{self.static_path}/{sub_filename[1]}", "rb") as file:
                    file_data = file.read().decode('utf-8')
                    #? header
                    status = '200 OK'
                    content_type = 'text/plain'
                    header_payload = f'status: {status}\r\ncontent-type: {content_type}' #\r\ncontent-length: {content_length}
                    header_response = {
                        'type': 1,
                        'length': len(header_payload),
                        'payload': header_payload,
                    }
                    self.send_response(stream_id, header_response, False)
                    #? data
                    data_response = {
                        'type': 0,
                        'length': len(file_data),
                        'payload': file_data,
                    }
                    self.send_response(stream_id, data_response, True)
            else:
                status = '404 Not Found'
                header_payload = f'status: {status}' #\r\ncontent-length: {content_length}
                header_response = {
                    'type': 1,
                    'length': len(header_payload),
                    'payload': header_payload,
                }
                print('file', sub_filename[1], 'does not exist!')
                self.send_response(stream_id, header_response, True)

    def send_response(self, stream_id, response, flag):
        frame_type = response['type'].to_bytes(1, byteorder='big') 
        length = response['length'].to_bytes(4, byteorder='big')
        payload = response['payload'].encode('utf-8')
        byte_response = frame_type + length + payload
        self.client.send(stream_id, byte_response, flag)
        time.sleep(0.05)
        # print('server sent response!')
    def handle_request(self, stream_id, request):
        parsed_request = self.parse_request(request)
        # print('received client msg!')
        # print('request:', parsed_request)
        # print('payload:', parsed_payload)
        # data frame
        # if parsed_request['type'] == 0:
        #     pass
        # # header frame
        if parsed_request['type'] == 1:
            parsed_payload = self.parse_payload(parsed_request['payload'].decode('utf-8'))
            if parsed_payload['method'] == 'GET':
                self.parse_get(stream_id, parsed_payload)
            else:
                status = '400 Bad Request'
                header_payload = f'status: {status}' #\r\ncontent-length: {content_length}
                header_response = {
                    'type': 1,
                    'length': len(header_payload),
                    'payload': header_payload,
                }
                print('Bad Request!')
                self.send_response(stream_id, header_response, True)
                
class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.socket = None
        self.host = host
        self.port = port
        self.static_path = ''
        self.alive = False
    def run(self):
        if not self.alive:
            self.alive = True
            self.socket = quic_server.QUICServer()
            self.socket.listen((self.host, self.port))
            self.socket.accept()
            client_handler = ClientHandler(self.socket, self.socket.client_addr, self.static_path)
    def set_static(self, path):
        #! make sure the path for static directory is correctly set.
        #! list the file in static for 'GET /' uses
        self.static_path = os.path.realpath(path)
        pass
    def close(self):
        self.alive = False
        self.socket.close()