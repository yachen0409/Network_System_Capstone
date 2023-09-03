import socket
import time
import threading
from collections import deque
        
class HTTPClient(): #? For HTTP/2
    def __init__(self) -> None:
        self.first = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_id = 1
    def get(self, url, headers=None):
        # Send the request and return the response (Object)
        # url = "http://127.0.0.1:8080/static/xxx.txt"
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
        request = {
            'type': 1,
            'flag': 0,
            'payload': f'method: GET\r\npath: {resource}',
        }
        self.send_request(request)
        # time.sleep(10)
        response = Response(self.socket, self.stream_id)
        response.recv_loop(self.socket)
        self.stream_id += 2
        return response

    def send_request(self, request):
        frame_type = request['type'].to_bytes(1, byteorder='big') 
        flag = request['flag'].to_bytes(1, byteorder='big')
        stream_id = self.stream_id.to_bytes(4, byteorder='big')
        payload = request['payload'].encode('utf-8')
        length = len(payload).to_bytes(3, byteorder='big')
        byte_response = length + frame_type + flag + stream_id + payload
        self.socket.sendall(byte_response)
        # print('sent!')
        return

class Response():
    def __init__(self, stream_id, headers = {}, status = "Not yet") -> None:
        self.stream_id = stream_id
        self.headers = headers
        self.status = status
        self.body = b""
        self.total_length = 0
        self.contents = deque()
        self.complete = False
    def recv_loop(self, client_socket):
        while True:
            try:
                response_header = client_socket.recv(9)
                parsed_header = self.parse_header(response_header)
                self.stream_id = parsed_header['stream_id']
                # print(parsed_header['length'])
                response_payload = client_socket.recv(parsed_header['length'])
                while(len(response_payload) < parsed_header['length']):
                    packet = client_socket.recv(parsed_header['length'] - len(response_payload))
                    response_payload += packet
                # print(response_payload)
                if parsed_header['type'] == 1: #?header
                    self.headers = self.parse_payload(response_payload.decode('utf-8'))
                    self.status = self.headers['status']
                else:
                    if self.headers['content-type'] == 'text/html':
                        self.body += response_payload
                        if parsed_header['flag'] == 1: #?parsed_header['flag'] == 1
                            self.complete = True
                            break
                    else:
                        self.contents.append(response_payload)
                        self.total_length += parsed_header['length']
                        if parsed_header['flag'] == 1: #?parsed_header['flag'] == 1
                            self.complete = True
                            # print('complete!')
                            break
            except socket.timeout:
                print('No reponse from server (Timeout)!')
                break
            except:
                print ("Cannot receive data (catch socket close)")
                break
    def parse_header(self, origin_response):
        header = {
            'length': None,
            'type': None, 
            'flag': None, 
            'stream_id': None,
        }
        # print(origin_response)
        header['length'] = int.from_bytes(origin_response[:3], byteorder='big')
        header['type'] = origin_response[3]
        header['flag'] = origin_response[4]
        header['stream_id'] = int.from_bytes(origin_response[5:9], byteorder='big')
        return header
    def parse_payload(self, origin_payload):
        item_list = origin_payload.split('\r\n')
        payload = {key: val for item in item_list for key, val in [item.split(': ')]}
        return payload
    def get_headers(self):
        begin_time = time.time()
        while self.status == "Not yet":
            if time.time() - begin_time > 5:
                return None
        return self.headers
    def get_full_body(self): # used for handling short body
        begin_time = time.time()
        while not self.complete:
            if time.time() - begin_time > 5:
                return None
        if len(self.body) > 0:
            return self.body
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        return self.body # the full content of HTTP response body
    def get_stream_content(self): # used for handling long body
        begin_time = time.time()
        while len(self.contents) == 0: # contents is a buffer, busy waiting for new content
          if self.complete or time.time()-begin_time > 5: # if response is complete or timeout
              return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body