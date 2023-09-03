import socket, struct, threading, time
class QUICServer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.server_addr = tuple()
        self.client_addr = tuple()
        #! ERROR control
        #? Resend timeout
        self.time_resend = 2
        #! CONGESTION control
        #? socket.recvfrom size (from Client)
        self.recvsize = 0
        #? expect received_ack rate[0:1]
        self.expect_ackrate = 0.5
        #? Sliding window size
        self.windowsize = 3
        #! FLOW control
        #? recv_buffer max size 
        self.max_recvbuffersize = 5000
        #? overflow flags for my and receiver's recv_buffer
        self.my_recv_overflow = False
        self.recv_overflow = False
        #? {stream_id:send_thread, ...}
        self.send_threads = {} 
        self.mutex_buffer = threading.Lock()
        #? {stream_id:[[ack_recv:bool, ...]:list, [each_packet_timer, ... ]:list]:list, ... }
        self.recv_info = {}
        self.mutex_info = threading.Lock()
        #? [(stream_id, total_packet_num, data), ...] 
        self.recv_buffer = [] 
    def listen(self, socket_addr):
        """this method is to open the socket"""
        self.server_addr = socket_addr
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_addr)
        # print("bind", socket_addr)
    def send_socket(self, stream_id, data):
        #! Packet Structure INFO
        #? msg, msgack->(type, stream_id, total_packet_num, packet_index, buf)
        #? type0->init, type1->msg, type2->msgack
        #? Slice data
        # print("slicing stream_id", stream_id, " data...")
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
                #? max(24, self.recvsize) -> 24 for handshake packet resend 
                recv_packet, address = self.sock.recvfrom(max(30, self.recvsize))
            except BlockingIOError as e:
                recv_packet = None
            if recv_packet != None:
                recv_type, recv_stream_id= struct.unpack("@ii", recv_packet[0:8])
                #? type0->init, handshake packet resend
                if recv_type == 0:
                    data = struct.pack("@ii11si", 0, 3, b"ServerHello", 0)
                    self.sock.sendto(data, self.client_addr)
                #? type1->msg, send ACK back
                elif recv_type == 1:
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
                        # print("Get Client MSG! stream_id =", recv_stream_id, "BUF =", recv_buf)
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
                    # print("Get Client ACK!")
                    self.mutex_info.acquire()
                    self.recv_info[recv_stream_id][0][recv_packet_index] = True
                    self.mutex_info.release()
            
    def accept(self):
        """this method is to indicate that the client
        can connect to the server now"""
        print("Waiting client to connect......")
        while True:
            # try:
            buf, addr = self.sock.recvfrom(1000)
            # print(addr)
            if buf is not None:
                type, num, buf, optional = struct.unpack("@ii11si", buf)
                # print("from client:", addr, type, num, buf, optional)
                if type == 0:
                    if num == 0 and buf == b'ClientHello':
                        # print("Get client hello!")
                        self.recvsize = optional
                        self.client_addr = addr
                        data = struct.pack("@ii11si", 0, 1, b"ServerHello", 0)
                        self.sock.sendto(data, self.client_addr)
                    elif num == 2:                            
                        # print("Get ServerHello ACK!")
                        data = struct.pack("@ii11si", 0, 3, b"ServerHello", 0)
                        self.sock.sendto(data, self.client_addr)
                        break
            # except socket.timeout:
            #     print("Timeout! INIT msg Resend~")
            #     data = struct.pack("@ii11si", 0, 0, b"ServerHello", 0)
            #     self.sock.sendto(data, self.client_addr)
        self.recv_thread = threading.Thread(target=self.recv_socket)
        print("Connection to Client at", self.client_addr, " established!")
        self.sock.setblocking(0)
        self.recv_thread.start()

    def send(self, stream_id: int, data: bytes):
        """call this method to send data, with non-reputation stream_id"""
        #? 每個send都創一個thread->檢查大小(要不要分多個封包)->傳and等ack->確定ack完不完整->完整就結束，不完整就重傳
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


# server side
if __name__ == "__main__":
    server = QUICServer()
    server.listen(("", 30000))
    server.accept()
    server.send(1, b"SOME DATA, MAY EXCEED 1500 bytes")
    recv_id, recv_data = server.recv()
    print(recv_data.decode("utf-8")) # Hello Server!
    server.close() 