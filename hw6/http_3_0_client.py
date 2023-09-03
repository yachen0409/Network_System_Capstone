import socket
import time
import threading
from QUIC import quic_client
from collections import deque
        
class HTTPClient(): #? For HTTP/3
    def __init__(self) -> None:
        self.first = True
        self.socket = None
        self.recv_thread = None
        self.response_headers = dict()
        self.recv_buffer = dict()
        self.stream_id = 1
    def get(self, url, headers=None):
        # Send the request and return the response (Object)
        # url = "http://127.0.0.1:8080/static/xxx.txt"
        stream_id = self.stream_id
        self.stream_id += 2
        resource = ''
        if len(url.split('/')) <= 1:
            resource = '/'
        else:
            resource = '/' + url.split('/', 1)[1]
        ip_port = url.split('/', 1)[0]
        ip = ip_port.split(':')[0]
        port = int(ip_port.split(':')[1])
        if(self.first):
            self.socket = quic_client.QUICClient()
            # self.socket.drop(5)
            try:
                self.socket.connect((ip, port))
                self.first = False
                self.recv_thread = threading.Thread(target=self.recv_loop)
                self.recv_thread.start()
                print('connect 1!')
            except:
                self.socket.close()
                print('connect failed!')
                return None
        header_payload = f'method: GET\r\npath: {resource}'
        request = {
            'type': 1,
            'length': len(header_payload),
            'payload': header_payload,
        }
        self.recv_buffer[stream_id] = {
            'length': 0,
            'header_in': False,
            'header_complete': False, 
            'data_complete': False, 
            'data': b'',
        }
        self.send_request(stream_id, request, True)
        # time.sleep(10)
        if stream_id == 1:
            while not self.recv_buffer[stream_id]['header_complete']:
                time.sleep(0.01)
        # print('stream', stream_id, 'get data (', len(self.recv_buffer[stream_id]['data']), 'bytes) complete!')
        response = Response(stream_id, self.response_headers, self.recv_buffer, self.recv_thread)
        # response.recv_loop(self.socket)
        return response
    def recv_loop(self):
        while True:
            try:
                stream_id, recv_bytes, flag = self.socket.recv()
                if stream_id is None:
                    print('stream_id is None!!!')
                    self.socket.close()
                    break
                # print('recv from server:', stream_id, len(recv_bytes), flag)
                if not self.recv_buffer[stream_id]['header_in']:
                    parsed_packet = self.parse_packet(recv_bytes)
                    # print('stream_id', stream_id, ' parsed_packet: ', parsed_packet)
                    self.recv_buffer[stream_id]['length'] = parsed_packet['length']
                    if parsed_packet['type'] == 1:
                        self.response_headers[stream_id] = self.parse_payload(parsed_packet['payload'])
                        self.recv_buffer[stream_id]['header_complete'] = True
                    else:
                        self.recv_buffer[stream_id]['data'] += parsed_packet['payload']
                        # print(f"stream {stream_id} length {len(self.recv_buffer[stream_id]['data'])}")
                        self.recv_buffer[stream_id]['header_in'] = True
                        if flag:
                            self.recv_buffer[stream_id]['data_complete'] = True
                else:
                    # print(f'stream {stream_id} receive {len(recv_bytes)} bytes')
                    self.recv_buffer[stream_id]['data'] += recv_bytes
                    # print(f"stream {stream_id} length {len(self.recv_buffer[stream_id]['data'])}")
                    # print(f"stream {stream_id} {len(self.recv_buffer[stream_id]['data'])} {self.recv_buffer[stream_id]['length']}")
                    if self.recv_buffer[stream_id]['length'] <= len(self.recv_buffer[stream_id]['data']):
                        self.recv_buffer[stream_id]['data_complete'] = True
            except:
                self.socket.close()
                break
        return
    def parse_packet(self, origin_response):
        # print('inside function parse_packet...')
        response = {
            'type': None, 
            'length': None,
            'payload': None, 
        }
        response['type'] = origin_response[0]
        response['length'] = int.from_bytes(origin_response[1:5], byteorder='big')
        response['payload'] = origin_response[5:]
        return response
    def parse_payload(self, origin_payload):
        item_list = origin_payload.decode('utf-8').split('\r\n')
        payload = {key: val for item in item_list for key, val in [item.split(': ')]}
        
        return payload
    def send_request(self, stream_id, request, flag):
        frame_type = request['type'].to_bytes(1, byteorder='big') 
        length = request['length'].to_bytes(4, byteorder='big')
        payload = request['payload'].encode('utf-8')
        byte_request = frame_type + length + payload
        self.socket.send(stream_id, byte_request, flag)
        time.sleep(0.005)
        # print('stream_id', stream_id, 'request sent!')
        return

class Response():
    def __init__(self, stream_id, header, recv_buffer, client_recv_thread) -> None:
        self.stream_id = stream_id
        self.header = header
        self.recv_buffer = recv_buffer
        self.client_recv_thread = client_recv_thread
        self.timeout = 120

    def get_headers(self):
        return self.header[self.stream_id]
    def get_full_body(self): # used for handling short body
        # begin_time = time.time()
        while not self.recv_buffer[self.stream_id]['data_complete']:
            # if time.time()-begin_time > self.timeout: # if response is complete or timeout
            #     print(f'stream {self.stream_id} get_full_body timeout! (> {self.timeout} secs)')
            #     return None
            time.sleep(0.01)
        # self.client_recv_thread.join()
        return self.recv_buffer[self.stream_id]['data']
    def get_stream_content(self): # used for handling long body
        # begin_time = time.time()
        while not self.recv_buffer[self.stream_id]['data_complete']:
            # if time.time()-begin_time > self.timeout: # if response is complete or timeout
            #     print(f'stream {self.stream_id} get_stream_content timeout! (> {self.timeout} secs)')
            #     # self.client_recv_thread.join()
            #     return None
            time.sleep(0.01)
        # print(f'stream {self.stream_id} spend {time.time()-begin_time} secs')
        content = self.recv_buffer[self.stream_id]['data']
        self.recv_buffer[self.stream_id]['data'] = None
        # self.client_recv_thread.join()
        return content
