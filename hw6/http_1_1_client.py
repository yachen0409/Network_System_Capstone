import socket
import json
from Utils import Parser
import os
import glob
import xml.etree.ElementTree as ET

class HTTPClient(): # For HTTP/1.X
    def __init__(self) -> None:
        self.first = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def get(self, url, headers=None, stream=False):
        # Send the request and return the response (Object)
        # url = "http://127.0.0.1:8080/static/xxx.txt"
        # If stream=True, the response should be returned immediately after the full headers have been received.
        resource = ''
        if len(url.split('/')) <= 1:
            resource = '/'
        else:
            resource = '/' + url.split('/', 1)[1]
        ip_port = url.split('/', 1)[0]
        ip = ip_port.split(':')[0]
        port = int(ip_port.split(':')[1])
        if(self.first):
            self.socket.settimeout(5)
            try:
                self.socket.connect((ip, port))
                self.first = False
                # print('connect 1!')
            except:
                print('connect failed!')
                return None
        request = f"GET {resource} HTTP/1.1\r\n\r\n"
        # print('request =', request)
        try:
            self.socket.sendall(request.encode())
            # print('sent!')
        except:
            self.socket.close()
            return None

        response = Response(self.socket, stream)
        return response

class Response():
    def __init__(self, socket, stream) -> None:
        self.socket = socket
        self.stream = stream
        # fieleds
        self.response = ''
        self.version = "" # e.g., "HTTP/1.0"
        self.status = ""  # e.g., "200 OK"
        self.headers = {} # e.g., {content-type: application/json}
        self.body = b""  # e.g. "{'id': '123', 'key':'456'}"
        self.body_length = 0
        self.complete = False
        self.__reamin_bytes = b""
        self.parse_response()
    def parse_response(self):
        self.response = self.socket.recv(4096).decode()
        lines = self.response.split('\r\n')
        index = lines[0].find(" ")
        self.version = lines[0][:index]
        self.status = lines[0][index+1:]
        tmp_headers = {}
        for line in lines[1:]:
            if line == '':
                break
            index = line.find(":",1)
            if index != -1 and index+2<len(line):
                key, value = line[:index].strip(), line[index+1:].strip()
                tmp_headers[key.lower()] = value
        self.headers = tmp_headers
        if "\r\n\r\n" in self.response:
            body = self.response.split("\r\n\r\n")[1]
        self.body = body.encode()
        self.body_length = len(body)
        if self.body_length >= int(self.headers['content-length']):
            self.complete = True
        # print('im here!')
        # print('version:', self.version)
        # print('status:', self.status)
        # print('headers:', self.headers)
        # print('body_length:', self.body_length)
        # print('body:', self.body)
    def get_full_body(self): # used for handling short body
        if self.stream or not self.complete:
            return None
        return self.body # the full content of HTTP response body
    def get_remain_body(self):
        received_body_bytes = self.socket.recv(4096)
        self.body_length += len(received_body_bytes)
        if self.body_length >= int(self.headers['content-length']):
            self.complete = True
        return received_body_bytes
        # }
    def get_stream_content(self): # used for handling long body
        # print('inside get_stream_content......', self.stream, self.complete)
        if not self.stream or self.complete:
            return None
        if self.body != b"":
            content = self.body
            self.body = b""
            return content
        content = self.get_remain_body() # recv remaining body data from socket
        return content # the part content of the HTTP response body