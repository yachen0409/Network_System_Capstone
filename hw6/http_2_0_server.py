import socket
import threading
import time
import os
from datetime import datetime
import json
import base64

class ClientHandler():
    def __init__(self, client, address, static_path) -> None:
        self.client = client
        # self.client.settimeout(5)
        self.address = address
        self.alive = True
        self.static_path = static_path
        self.filenames = os.listdir(self.static_path)
        self.client_threads = []
        self.recv_loop()
    def recv_loop(self):
        while True:
            try:
                recv_bytes = self.client.recv(4096)
                if not recv_bytes:
                    for thread in self.client_threads:
                        thread.join()
                    self.alive = False 
                    self.client.close()
                    print(f'Client {client_address} closed!')
                    break
                # print('recv something!!!', len(recv_bytes))
                client_thread = threading.Thread(target=self.handle_request, args=(recv_bytes,))
                self.client_threads.append(client_thread)
                client_thread.start()
            except:
                for thread in self.client_threads:
                    thread.join()
                self.alive = False 
                self.client.close()
                print('recv_loop error (socket closed)')
                break
    def parse_request(self, origin_request):
        request = {
            'length': None,
            'type': None, 
            'flag': None, 
            'stream_id': None, 
            'payload': None, 
        }
        request['length'] = int.from_bytes(origin_request[:3], byteorder='big')
        request['type'] = origin_request[3]
        request['flag'] = origin_request[4]
        request['stream_id'] = int.from_bytes(origin_request[5:9], byteorder='big')
        request['payload'] = origin_request[9:]
        return request
    def parse_payload(self, origin_payload):
        item_list = origin_payload.split('\r\n')
        payload = {key: val for item in item_list for key, val in [item.split(': ')]}
        return payload
    def parse_get(self, request, payload):
        stream_id = request['stream_id']
        path = payload['path']
        if path == "/":
            # print(self.static_path)
            status = '200 OK'
            content_type = 'text/html'
            filenames = self.filenames
            html_content = f"""<html><header></header>
                                <body>
                                    <a href=\"/static/{filenames[0]}\">{filenames[0]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[1]}\">{filenames[1]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[2]}\">{filenames[2]}</a>
                                </body></html>"""
            content_length = len(html_content)
            header_response = {
                'type': 1,
                'flag': 0,
                'payload': f'status: {status}\r\ncontent-type: {content_type}\r\ncontent-length: {content_length}',
            }
            self.send_response(request, header_response)
            data_response = {
                'type': 0,
                'flag': 1,
                'payload': html_content,
            }
            self.send_response(request, data_response)
        else:
            sub_filename = (path.split('/', 1)[1]).split('/')
            # print(sub_filename)
            if(sub_filename[0] == 'static' and sub_filename[1] in self.filenames):
                print(f"{self.address[0]} - - {datetime.now().strftime('%H:%M:%S')} \"GET {sub_filename[1]}\"")
                with open(f"{self.static_path}/{sub_filename[1]}", "rb") as file:
                    file_data = file.read().decode('utf-8')
                    #? header
                    status = '200 OK'
                    content_type = 'text/plain'
                    content_length = len(file_data)
                    header_response = {
                        'type': 1,
                        'flag': 0,
                        'payload': f'status: {status}\r\ncontent-type: {content_type}\r\ncontent-length: {content_length}',
                    }
                    self.send_response(request, header_response)
                    #? data
                    length = len(file_data)
                    sliced_data = []
                    if length > 3000:
                        for i in range(0, length, 3000):
                            sliced_data.append(file_data[i: i+3000])
                    else:
                        sliced_data.append(file_data)
                    for i in range(len(sliced_data)):
                        if i == (len(sliced_data)-1):
                            data_response = {
                                'type': 0,
                                'flag': 1,
                                'payload': sliced_data[i],
                            }
                            self.send_response(request, data_response)
                        else:
                            data_response = {
                                'type': 0,
                                'flag': 0,
                                'payload': sliced_data[i],
                            }
                            self.send_response(request, data_response)
            else:
                #! 404 NOT FOUND
                status = '404 Not Found'
                header_response = {
                    'type': 1,
                    'flag': 0,
                    'payload': f'status: {status}',
                }
                print('file', sub_filename[1], 'does not exist!')
                self.send_response(request, header_response)
    def send_response(self, request, response):
        frame_type = response['type'].to_bytes(1, byteorder='big') 
        flag = response['flag'].to_bytes(1, byteorder='big')
        stream_id = request['stream_id'].to_bytes(4, byteorder='big')
        payload = response['payload'].encode('utf-8')
        length = len(payload).to_bytes(3, byteorder='big')
        byte_response = length + frame_type + flag + stream_id + payload
        self.client.sendall(byte_response)
        time.sleep(0.005)
        # print('server sent', length, 'to client!')
        
    def handle_request(self, request):
        parsed_request = self.parse_request(request)
        parsed_payload = self.parse_payload(parsed_request['payload'].decode('utf-8'))
        # print('received client msg!')
        # print('request:', parsed_request)
        # print('payload:', parsed_payload)
        # data
        # if parsed_request['type'] == 0:
            # pass
        # header
        if parsed_request['type'] == 1:
            if parsed_payload['method'] == 'GET':
                self.parse_get(parsed_request, parsed_payload)
            else:
                status = '400 Bad Request'
                header_response = {
                    'type': 1,
                    'flag': 0,
                    'payload': f'status: {status}',
                }
                print('Bad Request!')
                self.send_response(request, header_response)

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
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            client, address = self.socket.accept()
            client_handler = ClientHandler(client, address, self.static_path)
    def set_static(self, path):
        #! make sure the path for static directory is correctly set.
        #! list the file in static for 'GET /' uses
        self.static_path = os.path.realpath(path)
        pass
    def close(self):
        self.alive = False
        self.socket.close()
