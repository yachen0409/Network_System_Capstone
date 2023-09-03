import socket, struct, threading, time
# import socket.timeout from socket
# init->(type, num, buf, optional)
# msg, msgack->(type, num, total_packet_num, packet_index, buf)
# type0->init
# type1->msg
# type2->msgack
class QUICClient:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.server_addr = tuple()
        self.client_addr = tuple()
        #! ERROR control
        #? Resend timeout
        self.time_resend = 2
        self.init_time_resend = self.time_resend
        #! CONGESTION control
        #? socket.recvfrom size for both server and client 
        self.recvsize = 30
        #? expect received_ack rate[0:1]
        self.expect_ackrate = 0.5
        #? Sliding window size
        self.windowsize = 3
        #! FLOW control
        #? recv_buffer max size 
        self.max_recvbuffersize = 500
        #? overflow flags for my and receiver's recv_buffer
        self.my_recv_overflow = False
        self.recv_overflow = False
        #? {stream_id:send_thread, ...}
        self.send_threads = {}
        self.mutex_buffer = threading.Lock()
        #? { stream_id:[[ack_recv:bool, ...]:list, [each_packet_timer, ... ]:list]:list, ... }
        self.recv_info = {} 
        self.mutex_info = threading.Lock()
        #? [(stream_id, total_packet_num, data), ...]
        self.recv_buffer = [] 
    def send_socket(self, stream_id, data):
        #! Packet Structure INFO
        #? msg, msgack->(type, stream_id, total_packet_num, packet_index, buf)
        #? type0->init, type1->msg, type2->msgack
        #? Slice data
        datas = []
        max_datasize = self.recvsize - 16
        if len(data) > max_datasize:
            i = 0
            while len(data) >= max_datasize*(i):
                datas.append(data[max_datasize*i : max_datasize*(i+1)])
                i+=1
        else:
            datas.append(data)
        packet_num = len(datas)
        # print("stream_id", stream_id, "total packet num", packet_num)
        # print("packets", datas)
        #? INIT and Send first window data
        window_head = 0
        window_end = min(packet_num, self.windowsize)
        self.recv_info[stream_id][0] = [False for x in range(packet_num)]
        self.recv_info[stream_id][1] = [0 for x in range(packet_num)]
        for i in range(window_end):
            send_packet = struct.pack("@iiii", 1, stream_id, packet_num, i)
            send_packet += datas[i]
            self.sock.sendto(send_packet, self.client_addr)
            self.recv_info[stream_id][1][i] = time.time() + self.time_resend
        # print("init send stream_id", stream_id, "window", window_head, "to", window_end)
        while True:
            #? Check whether receiver's buffer is overflow
            if self.recv_overflow == True:
                # print("receiver overflow!!!!!!!")
                continue
            #? INIT and Check ACKs of the window
            ack_num = 0
            min_noack_index = float('inf')
            all_in_time = True
            self.mutex_info.acquire()
            for i in range(window_head, window_end):
                if(self.recv_info[stream_id][0][i] == True):
                    ack_num+=1
                else:
                    min_noack_index = min(i, min_noack_index)
                if(self.recv_info[stream_id][1][i] < time.time()):
                    all_in_time = False
            self.mutex_info.release()
            #? Get ALL ACK and complete in time -> OVER
            if all(self.recv_info[stream_id][0]) and all_in_time:
                break
            #? Get window's ACK and complete in time -> SLIDE WINDOW
            elif ack_num == self.windowsize and all_in_time:
                window_head = window_end
                self.windowsize*=2
                window_end = min(window_end + self.windowsize, packet_num)
                #? Send the window data
                for i in range(window_head, window_end):
                    send_packet = struct.pack("@iiii", 1, stream_id, packet_num, i)
                    send_packet += datas[i]
                    self.sock.sendto(send_packet, self.client_addr)
                    self.recv_info[stream_id][1][i] = time.time() + self.time_resend
                # print("Next window! stream_id", stream_id, "window", window_head, "to", window_end)
            #? Did NOT get all ACK and Time is up for any one packet -> SLIDE WINDOW
            elif not all_in_time:
                if min_noack_index != float('inf'):
                    window_head = min_noack_index
                if((ack_num/self.windowsize) < self.expect_ackrate):
                    self.windowsize = int(self.windowsize/2)
                    if self.windowsize == 0:
                        self.windowsize = 1
                    # print("windowsize/2 because of actual ack_rate is lower than self.expect_ackrate!")
                window_end = min(packet_num, window_head + self.windowsize)
                #? Send the window data
                for i in range(window_head, window_end):
                    send_packet = struct.pack("@iiii", 1, stream_id, packet_num, i)
                    send_packet += datas[i]
                    self.sock.sendto(send_packet, self.client_addr)
                    self.recv_info[stream_id][1][i] = time.time() + self.time_resend
                # print("Times up! resend stream_id", stream_id, "window", window_head, "to", window_end)
        # print("stream_id", stream_id, "ALL SENT!")

    def recv_socket(self):
        t = threading.current_thread()
        #? {stream_id: {{index:data}, ...}}
        tmp_recv_buffer = {} 
        while getattr(t, "do_run", True):
            #? non-blocking socket recvfrom
            try:
                recv_packet, address = self.sock.recvfrom(self.recvsize)
            except BlockingIOError as e:
                recv_packet = None
            if recv_packet != None:
                recv_type, recv_stream_id= struct.unpack("@ii", recv_packet[0:8])
                if recv_type == 1:
                    recv_packet_size, recv_packet_index = struct.unpack("@ii", recv_packet[8:16])
                    recv_buf = recv_packet[16:]
                    #? stream_id = -1 -> receiver recv_buffer overflow
                    if recv_stream_id == -1 and self.recv_overflow == False:
                        # print("!!! recvbuffer overflow  !!!")
                        self.recv_overflow = True
                    #? stream_id = -2 -> receiver recv_buffer available
                    elif recv_stream_id == -2 and self.recv_overflow == True:
                        # print("!!! recvbuffer available  !!!")
                        self.recv_overflow = False
                    else:
                        # print("Get Server MSG! stream_id =", recv_stream_id, "BUF =", recv_buf)
                        if not tmp_recv_buffer.get(recv_stream_id):
                            tmp_recv_buffer[recv_stream_id] = {}
                        tmp_recv_buffer[recv_stream_id][recv_packet_index] = recv_buf
                        #? if received all stream data -> concate them and send recv_buffer, waitting to be retrieved by self.recv() 
                        if len(tmp_recv_buffer[recv_stream_id]) == recv_packet_size:
                            # print("stream_id", recv_stream_id, "get all data", len(tmp_recv_buffer[recv_stream_id]), recv_packet_size)
                            tmp_data = bytearray()
                            for i in range(len(tmp_recv_buffer[recv_stream_id])):
                                tmp_data += tmp_recv_buffer[recv_stream_id][i]
                            self.mutex_buffer.acquire()
                            self.recv_buffer.append((recv_stream_id, recv_packet_size, tmp_data))
                            self.mutex_buffer.release()
                            del tmp_recv_buffer[recv_stream_id]
                            #? Calculate self.recv_buffer size
                            cur_recvbuffersize = 0
                            if len(self.recv_buffer) > 0:
                                for recv_tuple in self.recv_buffer:
                                    #? 16 -> header size of each packet
                                    cur_recvbuffersize += (len(recv_tuple[2]) + 16*recv_tuple[1])
                            # print("cur recvbuffer size", cur_recvbuffersize)
                            #? check if my recv_buffer overflow
                            if cur_recvbuffersize >= self.max_recvbuffersize and self.my_recv_overflow == False:
                                # print("my recv buffer overflow!")
                                self.send(-1, b'overflow')
                                self.my_recv_overflow = True
                    #? send back ACK
                    send_packet = struct.pack("@iiii", 2, recv_stream_id, recv_packet_size, recv_packet_index)
                    send_packet += recv_buf
                    self.sock.sendto(send_packet, self.client_addr)
                #? type2->msgack, update self.recv_info 
                elif recv_type == 2:
                    recv_packet_size, recv_packet_index = struct.unpack("@ii", recv_packet[8:16])
                    # print("Get Server ACK!")
                    self.mutex_info.acquire()
                    self.recv_info[recv_stream_id][0][recv_packet_index] = True
                    self.mutex_info.release()
                # #? Calculate tmp_recv_buffer size
                # cur_recvbuffersize = 0
                # # print(tmp_recv_buffer)
                # if len(self.recv_buffer) > 0:
                #     for recv_tuple in self.recv_buffer.values():
                #         #? 16 -> header size of each packet
                #         cur_recvbuffersize += (len(recv_tuple[1])+16)
                # # print("cur recvbuffer size", cur_recvbuffersize)
                # #? check if my recv_buffer overflow
                # if cur_recvbuffersize >= self.max_recvbuffersize and self.my_recv_overflow == False:
                #     # print("my recv buffer overflow!")
                #     self.send(-1, b'overflow')
                #     self.my_recv_overflow = True
    def connect(self, socket_addr: tuple[str, int]):
        """connect to the specific server"""
        # print("bind", socket_addr)
        cur_num = 0
        self.server_addr = socket_addr
        data = struct.pack("@ii11si", 0, 0, b"ClientHello", self.recvsize)
        self.sock.sendto(data, self.server_addr)
        self.sock.settimeout(self.init_time_resend)
        while True:
            try:
                buf, addr = self.sock.recvfrom(1000)
                if buf is not None:
                    type, num, buf, optional = struct.unpack("@ii11si", buf)
                    # print("from server:", addr, type, num, buf, optional)
                    if type == 0:
                        if num == 1 and buf == b"ServerHello":
                            # print("Get server hello!")
                            self.client_addr = addr
                            cur_num += 2
                            # self.sock.bind(addr)
                            data = struct.pack("@ii11si", 0, 2, b"ClientHello", 0)
                            self.sock.sendto(data, self.server_addr)
                            # self.sock.settimeout(2)
                        elif num == 3:
                            self.sock.setblocking(0)
                            break
                        else:
                            print("Not server hello!")
            except socket.timeout:
                print("Timeout! INIT msg Resend~")
                if cur_num == 0:
                    data = struct.pack("@ii11si", 0, cur_num, b"ClientHello", self.recvsize)
                else:
                    data = struct.pack("@ii11si", 0, cur_num, b"ClientHello", 0)
                self.sock.sendto(data, self.server_addr)
        # time.sleep(3)
        print("Connection to Server at", socket_addr, " established!")
        self.recv_thread = threading.Thread(target=self.recv_socket)
        self.send_thread = threading.Thread(target=self.send_socket)
        self.recv_thread.start()
        
    def send(self, stream_id: int, data: bytes):
        """call this method to send data, with non-reputation stream_id"""
        while True:
            if self.recv_overflow == True:
                continue
            else:
                break
        self.recv_info[stream_id] = [[], []]
        self.send_threads[stream_id] = threading.Thread(target=self.send_socket, args=(stream_id, data))
        self.send_threads[stream_id].start()
        
    
    def recv(self) -> tuple[int, bytes]: # stream_id, data
        """receive a stream, with stream_id"""
        stream_id = 0
        data = ""
        while True:   
            if len(self.recv_buffer) > 0:
                self.mutex_buffer.acquire()
                stream_id, total_packet_size, data = self.recv_buffer.pop(0)
                #? Calculate self.recv_buffer size
                cur_recvbuffersize = 0
                if len(self.recv_buffer) > 0:
                    for recv_tuple in self.recv_buffer:
                        #? 16 -> header size of each packet
                        cur_recvbuffersize += (len(recv_tuple[2]) + 16*recv_tuple[1])
                # print("cur recvbuffer size", cur_recvbuffersize)
                #? check if my recv_buffer become available again
                if cur_recvbuffersize < self.max_recvbuffersize and self.my_recv_overflow == True:
                    self.send(-2, b'available')
                    self.my_recv_overflow = False
                self.mutex_buffer.release()
                break
        return stream_id, data
    
    def close(self):
        """close the connection and the socket"""
        for id, each_thread in self.send_threads.items():
            each_thread.join()
        self.recv_thread.do_run = False
        self.recv_thread.join()
        self.sock.close()

# client side
if __name__ == "__main__":
    client = QUICClient()
    client.connect(("127.0.0.1", 30000))
    recv_id, recv_data = client.recv()
    print(recv_data.decode("utf-8")) # SOME DATA, MAY EXCEED 1500 bytes
    client.send(2, b"Hello Server!")
    client.close()