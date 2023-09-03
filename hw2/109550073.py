from setting import get_hosts, get_switches, get_links, get_ip, get_mac

#typedef
ICMP_REQ = 0
ICMP_REP = 1
ARP_REQ = 2
ARP_REP = 3

class host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac 
        self.port_to = None 
        self.arp_table = dict() # maps IP addresses to MAC addresses
    def add(self, node):
        self.port_to = node
    def show_table(self):
        # display ARP table entries for this host
        print("---------------", self.name)
        for key, value in self.arp_table.items():
            print(key, ":", value)

    def clear(self):
        # clear ARP table entries for this host
        self.arp_table.clear()

    def update_arp(self, ip, mac):
        # update ARP table with a new entry
        #print(self.name, ip, mac)
        self.arp_table[ip] = mac

    def handle_packet(self, src_name, src_ip, dst_ip, src_mac, dst_mac, msg_type): # handle incoming packets
        # ...
        if dst_ip != self.ip:
            return
        if msg_type == ARP_REP:
            self.update_arp(src_ip, src_mac)
            self.send(dst_ip, src_ip, self.mac, src_mac, ICMP_REQ)
        elif msg_type == ARP_REQ:
            if dst_ip == self.ip:
                self.update_arp(src_ip, src_mac)
                self.send(dst_ip, src_ip, self.mac, src_mac, ARP_REP)
        elif msg_type == ICMP_REQ:
            if dst_ip == self.ip:
                self.send(dst_ip, src_ip, self.mac, src_mac, ICMP_REP)
        
    def ping(self, dst_ip): # handle a ping request
        # ...
        msg_type = -1
        if dst_ip in self.arp_table.values():
            dst_mac = self.arp_table[dst_ip]
            msg_type = ICMP_REQ
        else:
            dst_mac = "ffff"
            msg_type = ARP_REQ
        self.send(self.ip, dst_ip, self.mac, dst_mac, msg_type)

    def send(self, src_ip, dst_ip, src_mac, dst_mac, msg_type):
        node = self.port_to # get node connected to this host
        node.handle_packet(self.name, src_ip, dst_ip, src_mac, dst_mac, msg_type) # send packet to the connected node

class switch:
    def __init__(self, name, port_n):
        self.name = name
        self.mac_table = dict() # maps MAC addresses to port numbers
        self.port_n = port_n # number of ports on this switch
        self.port_to = list() 
    def add(self, node): # link with other hosts or switches
        self.port_to.append(node)
        self.port_n += 1
    def show_table(self):
        # display MAC table entries for this switch
        print("---------------", self.name)
        for key, value in self.mac_table.items():
            print(key, ":", value)
        
    def clear(self):
        # clear MAC table entries for this switch
        self.mac_table.clear()

    def update_mac(self, mac, port):
        # update MAC table with a new entry
        #print(self.name, mac, port)
        self.mac_table[mac] = port

    def send(self, idx, src_ip, dst_ip, src_mac, dst_mac, msg_type): # send to the specified port
        node = self.port_to[idx] 
        node.handle_packet(self.name, src_ip, dst_ip, src_mac, dst_mac, msg_type) 
    
    def handle_packet(self, src_name, src_ip, dst_ip, src_mac, dst_mac, msg_type): # handle incoming packets
        # ...
        for idx in range(0, self.port_n):
            if src_name == self.port_to[idx].name:
                self.update_mac(src_mac, idx)
                break

        if dst_mac == "ffff":
            for idx in range(0, self.port_n):
                if src_name != self.port_to[idx].name:
                    self.send(idx, src_ip, dst_ip, src_mac, dst_mac, msg_type)
        else:
            if dst_mac in self.mac_table:
                self.send(self.mac_table[dst_mac], src_ip, dst_ip, src_mac, dst_mac, msg_type)
            else:
                for idx in range(0, self.port_n):
                    if src_name != self.port_to[idx].name:
                        self.send(idx, src_ip, dst_ip, src_mac, dst_mac, msg_type)



def add_link(tmp1, tmp2): # create a link between two nodes
    # ...
    # print(tmp1, tmp2)
    if tmp1 in hostlist:
        if tmp2 in switchlist:
            host_dict[tmp1].add(switch_dict[tmp2])
        elif tmp2 in hostlist:
            host_dict[tmp1].add(host_dict[tmp2])
    elif tmp1 in switchlist:
        if tmp2 in hostlist:
            switch_dict[tmp1].add(host_dict[tmp2])
        elif tmp2 in switchlist:
            switch_dict[tmp1].add(switch_dict[tmp2])

    if tmp2 in hostlist:
        if tmp1 in switchlist:
            host_dict[tmp2].add(switch_dict[tmp1])
        elif tmp1 in hostlist:
            host_dict[tmp2].add(host_dict[tmp1])
    elif tmp2 in switchlist:
        if tmp1 in hostlist:
            switch_dict[tmp2].add(host_dict[tmp1])
        elif tmp1 in switchlist:
            switch_dict[tmp2].add(switch_dict[tmp1])

def set_topology():
    global host_dict, switch_dict, hostlist, switchlist
    hostlist = get_hosts().split(' ')
    switchlist = get_switches().split(' ')
    link_command = get_links().split(' ')
    ip_dic = get_ip()
    mac_dic = get_mac()
    
    host_dict = dict() # maps host names to host objects
    switch_dict = dict() # maps switch names to switch objects
    
    # ... create nodes and links
    for each_host in hostlist:
        #print(each_host)
        host_dict[each_host] = host(each_host, ip_dic[each_host], mac_dic[each_host])
    for each_switch in switchlist:
        switch_dict[each_switch] = switch(each_switch, 0)
    for each_link in link_command:
        nodes = each_link.split(',')
        add_link(nodes[0], nodes[1]) 
     

def ping(tmp1, tmp2): # initiate a ping between two hosts
    global host_dict, switch_dict
    #print(tmp1 in host_dict, tmp2 in host_dict)
    if tmp1 in host_dict and tmp2 in host_dict : 
        node1 = host_dict[tmp1]
        node2 = host_dict[tmp2]
        node1.ping(node2.ip)
    else : 
        # invalid command
        print("a wrong command")


def show_table(tmp): # display the ARP or MAC table of a node
    # ...
    if tmp == "all_hosts":
        #print(host_dict)
        print("ip : mac")
        for each_host in host_dict:
            host_dict[each_host].show_table()
    elif tmp == "all_switches":
        #print(switch_dict)
        print("mac : port")
        for each_switch in switch_dict:
            switch_dict[each_switch].show_table()
    elif tmp in hostlist:
        print("ip : mac")
        host_dict[tmp].show_table()
    elif tmp in switchlist:
        print("mac : port")
        switch_dict[tmp].show_table()
    else:
        print("a wrong command")



def clear(node):
    # ...
    if node in hostlist: 
        host_dict[node].clear()
    elif node in switchlist:
        switch_dict[node].clear()
    else:
        print("a wrong command")

def run_net():
    while(1):
        command_line = input(">> ")
        input_split = command_line.split(" ")
        if input_split[0] == "show_table" and len(input_split) == 2:
            show_table(input_split[1])
        elif input_split[0] == "clear" and len(input_split) == 2:
            clear(input_split[1])
        elif len(input_split) == 3 and input_split[1] == "ping":
            ping(input_split[0], input_split[2])
        else:
            print("a wrong command")
        # ... handle user commands

    
def main():
    set_topology()
    run_net()


if __name__ == '__main__':
    main()
