import socket
import threading
import os
from datetime import datetime
import json
import base64


class ClientHandler():
    def __init__(self, client, address, static_path) -> None:
        self.client = client
        self.client.settimeout(5)
        self.address = address
        self.alive = True
        self.static_path = static_path
        self.filenames = os.listdir(self.static_path)
        self.recv_loop()
    def parse_reqeust(self, origin_request):
        request = {
            'method': "",
            'path': "",
            'params': {},
            'version': "",
            'headers': {},
            'body': "",
        }
        lines = origin_request.split('\r\n')
        request_list = lines[0].split()
        if len(request_list) != 3:
            return None
        request['method'] = request_list[0]
        request['path'] = request_list[1]
        request['version'] = request_list[2]
        # print(request['method'], request['path'], request['version'])
        headers = {}
        for line in lines[1:]:
            if line == '':
                break
            index = line.find(":",1)
            if index != -1 and index+2<len(line):
                key, value = line[:index].strip(), line[index+1:].strip()
                headers[key.lower()] = value
        request['headers'] = headers
        body = ""
        if "\r\n\r\n" in origin_request:
            body = origin_request.split("\r\n\r\n")[1]
        request['body'] = body
        return request
    def bad_request_response(self):
        response = {
            'version': "HTTP/1.0", 
            'status': "400 Bad Request", 
            'headers': {'Content-Type': 'text/html'},
            'body': "<html><body><h1>400 Bad Request</h1></body></html>"
        }
        return response
        
    def not_found_response(self):
        response = {
            'version': "HTTP/1.0", 
            'status': "404 Not Found", 
            'headers': {'Content-Type': 'text/html'}, 
            'body': "<html><body><h1>404 Not Found</h1></body></html>"
        }
        return response

    def parse_get(self, request):
        path = request['path']
        params = request['params']
        response = self.not_found_response()
        # print('inside parse_get...')
        if path == "/":
            filenames = self.filenames
            response['body'] = f"""<html><header></header>
                                <body>
                                    <a href=\"/static/{filenames[0]}\">{filenames[0]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[1]}\">{filenames[1]}</a>
                                    <br/>
                                    <a href=\"/static/{filenames[2]}\">{filenames[2]}</a>
                                </body></html>"""
            response['body'] = response['body'].encode()
            length = len(response['body'])
            response['status'] = "200 OK"
            response["headers"] = {
                'Content-Type': 'text/html',
                'Content-Length': length
            }
            self.send_response(request, response)
        else:
            sub_filename = (path.split('/', 1)[1]).split('/')
            if(sub_filename[0] == 'static' and sub_filename[1] in self.filenames):
                with open(f"{self.static_path}/{sub_filename[1]}", "rb") as file:
                    file_data = file.read()
                length = len(file_data)
                sliced_data = []
                if length > 3000:
                    for i in range(0, length, 3000):
                        sliced_data.append(file_data[i: i+3000])
                else:
                    sliced_data.append(file_data)
                response['body'] = sliced_data[0]
                response['status'] = "200 OK"
                response["headers"] = {
                    'Content-Type': 'text/plain',
                    'Content-Length': length
                }
                self.send_response(request, response)
                if len(sliced_data) > 1:
                    for i in range(1, len(sliced_data)):
                        self.client.sendall(sliced_data[i])
            else:
                print('file', sub_filename[1], 'does not exist!')
                self.send_response(request, response)

    def send_response(self, request, response):
        response_str = f"{response['version']} {response['status']}\r\n"
        for key in response['headers']:
            response_str += f"{key}: {response['headers'][key]}\r\n"
        response_str += "\r\n"
        response_str = response_str.encode()
        response_str += response['body']
        self.client.sendall(response_str)
        # print('sent', len(response_str), 'bytes')
        print(f"{self.address[0]} - {datetime.now().strftime('%H:%M:%S')} \"{request['method']} {request['path']} {request['version']}\" {response['status']}")

    def recv_loop(self):
        while True:
            try:
                recv_bytes = self.client.recv(4096)
                request = self.parse_reqeust(recv_bytes.decode())
                if request == None:
                    method = ""
                else:
                    method = request['method']
                if method == "GET":
                    self.parse_get(request)
                else:
                    self.send_response(request, self.bad_request_response())
            except:
                self.alive = False 
                # print('catch socket close 1!')
                break
        return
class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        # self.socket.settimeout(5)
        self.thread = threading.Thread(target=self.accept_loop)
        self.static_path = ''
        self.alive = False
    def accept_loop(self):
        while self.alive:
            try:
                client, address = self.socket.accept()
                client_handler = ClientHandler(client, address, self.static_path)
            except:
                # catch socket closed
                self.alive = False
                # print('catch socket close 2!')
    def run(self):
        if not self.alive:
            self.alive = True
            self.thread.start()
    def set_static(self, path):
        #! make sure the path for static directory is correctly set.
        #! list the file in static for 'GET /' uses
        self.static_path = os.path.realpath(path)
    def close(self):
        self.alive = False
        self.socket.close()
        self.thread.join()
