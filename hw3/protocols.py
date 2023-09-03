import random
import copy
#!status define
#0->idle
#1->send
#2->sending
#3->stop
#4->collide
def aloha(setting, show_history=False):
    packets = setting.gen_packets()
    host_send_time = copy.deepcopy(packets)
    channel_clear = True
    host_status=[[0 for i in range(setting.total_time)] for i in range(setting.host_num)]
    host_send_start=[0 for i in range(setting.host_num)]
    host_send_end=[0 for i in range(setting.host_num)]
    host_is_sending=[False for i in range(setting.host_num)]
    host_packet_index=[0 for i in range(setting.host_num)]
    host_collide=[False for i in range(setting.host_num)]
    success_time = 0
    idle_time = 0
    collision_time = 0
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        for host in range(setting.host_num):
            if (host_packet_index[host] < setting.packet_num) and (t == host_send_time[host][host_packet_index[host]]): 
                if not host_is_sending[host]:
                    host_status[host][t] = 1
                    host_send_start[host] = t
                    host_send_end[host] = t + setting.packet_time - 1
                    host_is_sending[host] = True
                else:
                    host_status[host][t] = 2
                    retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                    host_send_time[host][host_packet_index[host]] = retrans_time
                    
        count = len([i for i in host_is_sending if i == True])
        for host in range(setting.host_num):
            if host_is_sending[host] and count > 1:
                # print("time", t, "host", host, "detect collision")
                # print(host_is_sending)
                host_collide[host] = True
            if (host_packet_index[host] < setting.packet_num) and (t == host_send_time[host][host_packet_index[host]]):
                pass
            elif host_is_sending[host]:
                host_status[host][t] = 2

            if host_send_end[host] == t and t != 0:
                if host_collide[host]:
                    host_status[host][t] = 4
                    host_collide[host] = False
                    retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                    host_send_time[host][host_packet_index[host]] = retrans_time
                else:
                    host_status[host][t] = 3
                    if(host_packet_index[host]+1 < setting.packet_num) and (t >= host_send_time[host][host_packet_index[host]+1]):
                        host_send_time[host][host_packet_index[host]+1] = t+1
                    host_packet_index[host] += 1
                    success_time += setting.packet_time
                host_is_sending[host] = False
    
    if show_history:
        print('aloha')
        # Show the history of each host
        send_record=['    ' for i in range(setting.host_num)]
        for i in range(setting.host_num):
            # print(packets[i])
            for j in range(setting.total_time):
                if j not in packets[i]:
                    send_record[i]+=' '
                else:
                    send_record[i]+='V'
        for i in range(setting.host_num):
            print(send_record[i])
            print('h', end='')
            print(i, end='')
            print(':', end=' ')
            for status in host_status[i]:
                if status == 0:
                    print('.', end='')
                elif status == 1:
                    print('<', end='')
                elif status == 2:
                    print('-', end='')
                elif status == 3:
                    print('>', end='')
                elif status == 4:
                    print('|', end='')
            print(" ")
    for j in range(setting.total_time):
        all_idle=True
        for i in range(setting.host_num):
            if host_status[i][j] != 0:
                all_idle = False
        if all_idle:
            idle_time+=1
    collision_time = setting.total_time-idle_time-success_time   
    # print(success_time, idle_time, collision_time)
    return success_time/setting.total_time, idle_time/setting.total_time, collision_time/setting.total_time

def slotted_aloha(setting, show_history=False):
    packets = setting.gen_packets()
    host_send_time = copy.deepcopy(packets)
    channel_clear = True
    host_status=[[0 for i in range(setting.total_time)] for i in range(setting.host_num)]
    host_is_sending=[False for i in range(setting.host_num)]
    host_is_retrans=[False for i in range(setting.host_num)]
    host_packet_remain=[0 for i in range(setting.host_num)]
    success_time = 0
    idle_time = 0
    collision_time = 0

    for t in range(setting.packet_time,setting.total_time, setting.packet_time):
        # print(t)
        for host in range(setting.host_num):
            packet_count = len([i for i in host_send_time[host] if (i >= t-setting.packet_time and i <= t-1)])
            host_packet_remain[host] += packet_count
            if host_packet_remain[host] > 0: 
                if host_is_retrans[host]:
                    if random.random() < setting.p_resend:
                        # print("t =", t,"host", host, "retransmission")
                        host_status[host][t] = 1
                        for i in range(t+1, t+setting.packet_time-1):
                            if(i < setting.total_time):
                                host_status[host][i] = 2
                        host_is_retrans[host] = False
                        host_is_sending[host] = True
                else:
                    host_status[host][t] = 1
                    for i in range(t+1, t+setting.packet_time-1):
                        if(i < setting.total_time):
                            host_status[host][i] = 2
                    host_is_sending[host] = True
                    
        count = len([i for i in host_is_sending if i == True])
        if count > 1:
            for host in range(setting.host_num):
                if host_is_sending[host]:
                    if t+setting.packet_time-1 < setting.total_time:
                        host_status[host][t+setting.packet_time-1] = 4
                    host_is_retrans[host] = True
                    host_is_sending[host] = False
            collision_time += setting.packet_time
        elif count == 1:
            for host in range(setting.host_num):
                if host_is_sending[host]:
                    if t+setting.packet_time-1 < setting.total_time:
                        host_status[host][t+setting.packet_time-1] = 3
                    host_packet_remain[host] -= 1
                    host_is_sending[host] = False
            success_time += setting.packet_time
    
    if show_history:
        # Show the history of each host
        print('slotted aloha')
        send_record=['    ' for i in range(setting.host_num)]
        for i in range(setting.host_num):
            # print(packets[i])
            for j in range(setting.total_time):
                if j not in packets[i]:
                    send_record[i]+=' '
                else:
                    send_record[i]+='V'
        for i in range(setting.host_num):
            print(send_record[i])
            print('h', end='')
            print(i, end='')
            print(':', end=' ')
            for status in host_status[i]:
                if status == 0:
                    print('.', end='')
                elif status == 1:
                    print('<', end='')
                elif status == 2:
                    print('-', end='')
                elif status == 3:
                    print('>', end='')
                elif status == 4:
                    print('|', end='')
            print(" ")

    idle_time = setting.total_time-collision_time-success_time   
    # print(success_time, idle_time, collision_time)
    return success_time/setting.total_time, idle_time/setting.total_time, collision_time/setting.total_time

def csma(setting, show_history=False):
    packets = setting.gen_packets()
    host_send_time = copy.deepcopy(packets)
    last_success_host = -1
    host_status=[[0 for i in range(setting.total_time)] for i in range(setting.host_num)]
    host_send_start=[0 for i in range(setting.host_num)]
    host_send_end=[0 for i in range(setting.host_num)]
    host_is_sending=[False for i in range(setting.host_num)]
    host_packet_index=[0 for i in range(setting.host_num)]
    host_collide=[False for i in range(setting.host_num)]
    count_list = []
    success_time = 0
    idle_time = 0
    collision_time = 0
    for t in range(setting.total_time):
        count = len([i for i in host_is_sending if i == True])
        count_list.append(count)
        
        for host in range(setting.host_num):
            if (host_packet_index[host] < setting.packet_num) and (t == host_send_time[host][host_packet_index[host]]): 
                # if(t<400):
                    # print(t)
                if (not host_is_sending[host]):
                    busy=False
                    for i in range(setting.host_num):
                        if i != host:
                            if host_status[i][t-setting.link_delay-1] == 1 or host_status[i][t-setting.link_delay-1] == 2:
                                # if(t < 400):
                                    # print("host", host,"is busy!")
                                busy = True
                                break
                    if (busy == False): #or (last_success_host == host and host_status[host][t-1] == 3):
                        # if(t < 400):
                            # print("t =", t, "host", host, "start send new packet")
                        host_status[host][t] = 1
                        host_send_start[host] = t
                        host_send_end[host] = t + setting.packet_time - 1
                            
                        host_is_sending[host] = True
                        # sending = [i for i in host_is_sending if i == True]
                        count = len([i for i in host_is_sending if i == True])
                        if count > 1:
                            for i in range(len(host_is_sending)):
                                if host_is_sending[i]:
                                    host_collide[i] = True
                    else:
                        # if(t < 400):
                        # print("t =", t, "max_collision_time", setting.max_colision_wait_time)
                        retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                        host_send_time[host][host_packet_index[host]] = retrans_time

                else:
                    # print("t =", t, "host", host, "host IS SENDING so cannot send new packet")
                    host_status[host][t] = 2
                    retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                    host_send_time[host][host_packet_index[host]] = retrans_time
            elif host_is_sending[host]:
                host_status[host][t] = 2
        for host in range(setting.host_num):
            if host_send_end[host] == t and host_status[host][t] == 2:
                busy=False
                for i in range(setting.host_num):
                    if i != host:
                        if host_status[i][t-setting.link_delay-1] == 1 or host_status[i][t-setting.link_delay-1] == 2:
                            busy = True
                            break
                if host_collide[host]:
                    host_status[host][t] = 4
                    host_collide[host] = False
                    # print("t =", t, "host", host, "host IS SENDING so cannot send new packet")
                    # print("t =", t, "max_collision_time", setting.max_colision_wait_time)
                    retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                    host_send_time[host][host_packet_index[host]] = retrans_time
                else:
                    host_status[host][t] = 3
                    # if(t < 400):
                        # print("t =", t, "host", host, "SUCCESSSSSSSSSS")
                        # print(host_send_time[host][host_packet_index[host]], host_send_time[host][host_packet_index[host]+1])
                    # print(host_packet_index[host]+1)
                    if (host_packet_index[host]+1 < setting.packet_num) and (t >= host_send_time[host][host_packet_index[host]+1]):
                        host_send_time[host][host_packet_index[host]+1] = t+1
                    host_packet_index[host] += 1
                    # if(t < 400):
                        # print("t =", t, "host", host, "SUCCESSSSSSSSSS")
                        # print(host_packet_index[host])
                        # print(host_send_time[host][host_packet_index[host]])
                    success_time += setting.packet_time
                host_is_sending[host] = False
    
    if show_history:
        # Show the history of each host
        print('csma')
        send_record=['    ' for i in range(setting.host_num)]
        for i in range(setting.host_num):
            # print(packets[i])
            for j in range(setting.total_time):
                if j not in packets[i]:
                    send_record[i]+=' '
                else:
                    send_record[i]+='V'
        for i in range(setting.host_num):
            print(send_record[i])
            print('h', end='')
            print(i, end='')
            print(':', end=' ')
            for status in host_status[i]:
                if status == 0:
                    print('.', end='')
                elif status == 1:
                    print('<', end='')
                elif status == 2:
                    print('-', end='')
                elif status == 3:
                    print('>', end='')
                elif status == 4:
                    print('|', end='')
            print(" ")
    for j in range(setting.total_time):
        all_idle=True
        for i in range(setting.host_num):
            if host_status[i][j] != 0:
                all_idle = False
        if all_idle:
            idle_time+=1
    collision_time = setting.total_time-idle_time-success_time   
    return success_time/setting.total_time, idle_time/setting.total_time, collision_time/setting.total_time

def csma_cd(setting, show_history=False):
    packets = setting.gen_packets()
    host_send_time = copy.deepcopy(packets)
    # print(packets)
    last_success_host = -1
    host_status=[[0 for i in range(setting.total_time)] for i in range(setting.host_num)]
    host_send_start=[0 for i in range(setting.host_num)]
    host_send_end=[0 for i in range(setting.host_num)]
    host_is_sending=[False for i in range(setting.host_num)]
    host_packet_index=[0 for i in range(setting.host_num)]
    host_collide=[False for i in range(setting.host_num)]
    success_time = 0
    idle_time = 0
    collision_time = 0
    nearest_start_host = -1
    for t in range(setting.total_time):  
        for host in range(setting.host_num):
            if host_status[host][t] == 4:
                host_collide[host] = False
                retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                host_send_time[host][host_packet_index[host]] = retrans_time
                host_is_sending[host] = False
            if (host_packet_index[host] < setting.packet_num) and (t == host_send_time[host][host_packet_index[host]]): 
                if (not host_is_sending[host]):
                    busy=False
                    for i in range(setting.host_num):
                        if i != host:
                            if host_status[i][t-setting.link_delay-1] == 1 or host_status[i][t-setting.link_delay-1] == 2:
                                busy = True
                                break
                    if (busy == False) or (last_success_host == host and host_status[host][t-1] == 3):
                        host_status[host][t] = 1
                        host_send_start[host] = t
                        host_send_end[host] = t + setting.packet_time - 1
                            
                        host_is_sending[host] = True
                        # print("t =", t, "nearest_host =", host)
                        nearest_start_host = host
                        count = len([i for i in host_is_sending if i == True])
                        if count > 1:
                            for i in range(len(host_is_sending)):
                                if host_is_sending[i]:
                                    host_collide[i] = True
                    else:
                        retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                        host_send_time[host][host_packet_index[host]] = retrans_time

                else:
                    # print("t =", t, "host", host, "host IS SENDING so cannot send new packet")
                    host_status[host][t] = 2
                    retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                    host_send_time[host][host_packet_index[host]] = retrans_time
            elif host_is_sending[host]:
                host_status[host][t] = 2

        for host in range(setting.host_num):
            if host_status[host][t] == 2:
                busy=False
                for i in range(setting.host_num):
                    if i != host:
                        if host_status[i][t-setting.link_delay-1] == 1 or host_status[i][t-setting.link_delay-1] == 2:
                            busy = True
                            break
                
                if host_collide[host]:
                    # print("t =", t, "host ", host, "detect collision")
                    if host == nearest_start_host:
                        # print('t =', t, "detect", nearest_start_host)
                        # print(host_collide)
                        same_start_time_host = []
                        for k in range(len(host_send_start)):
                            if host_send_start[k] == host_send_start[host]:
                                same_start_time_host.append(k)
                        for same_start_host in same_start_time_host:
                            host_status[same_start_host][t] = 4
                            host_collide[same_start_host] = False
                            retrans_time = random.randint(t+1, t+setting.max_colision_wait_time)
                            host_send_time[same_start_host][host_packet_index[same_start_host]] = retrans_time
                            host_is_sending[same_start_host] = False
                        for i in range(len(host_collide)):
                            if i not in same_start_time_host and host_collide[i]:
                                for j in range(t, min(t+setting.link_delay, setting.total_time)):
                                    host_status[i][j] = 2
                                if t+setting.link_delay < setting.total_time:
                                    host_status[i][t+setting.link_delay] = 4
                                # print('set host', i, 'collide at t', t+setting.link_delay)  
                elif t < host_send_end[host]:
                    host_status[host][t] = 2
                else:
                    host_status[host][t] = 3
                    # print(host_packet_index[host]+1)
                    if (host_packet_index[host]+1 < setting.packet_num) and (t >= host_send_time[host][host_packet_index[host]+1]):
                        host_send_time[host][host_packet_index[host]+1] = t+1
                    host_packet_index[host] += 1
                    last_success_host = host
                    success_time += setting.packet_time
                    host_is_sending[host] = False
    
    if show_history:
        # Show the history of each host
        print('csma cd')
        send_record=['    ' for i in range(setting.host_num)]
        for i in range(setting.host_num):
            # print(packets[i])
            for j in range(setting.total_time):
                if j not in packets[i]:
                    send_record[i]+=' '
                else:
                    send_record[i]+='V'
        for i in range(setting.host_num):
            print(send_record[i])
            print('h', end='')
            print(i, end='')
            print(':', end=' ')
            for status in host_status[i]:
                if status == 0:
                    print('.', end='')
                elif status == 1:
                    print('<', end='')
                elif status == 2:
                    print('-', end='')
                elif status == 3:
                    print('>', end='')
                elif status == 4:
                    print('|', end='')
            print(" ")
    for j in range(setting.total_time):
        all_idle=True
        for i in range(setting.host_num):
            if host_status[i][j] != 0:
                all_idle = False
        if all_idle:
            idle_time+=1
    collision_time = setting.total_time-idle_time-success_time 
    return success_time/setting.total_time, idle_time/setting.total_time, collision_time/setting.total_time