import pyshark, netifaces
import os, datetime, argparse, time, regex
import verify
import pandas as pd
def step1(filename):
    file1 = pd.read_csv(filename)
    # print(file1.info())
    # print(file1.describe())
    file1.head(10)
    file1.isnull().sum
    #print(file1.isnull().sum)
    # step-1 to replace all null
    update_file = file1.fillna(" ")
    update_file.isnull().sum()
    #print (update_file.isnull().sum())
    update_file.to_csv(filename, index = False)
    # step-2 to remove all rows with null value
    update_file = file1.fillna(0)
    #print (update_file.isnull().sum())

def run_parse(pcap_filename):
    output_file = f'./csv/{pcap_filename.split("/")[-1].replace(".pcap", "")}.csv'
    cmd = (f'tshark -r {pcap_filename} -T fields -E header=y -E separator=, -E quote=d -E occurrence=f -e ip.src -e ip.dst -e ip.len -e ip.flags.df -e ip.flags.mf '
                '-e ip.fragment -e ip.fragment.count -e ip.fragments -e ip.ttl -e ip.proto -e tcp.window_size -e tcp.ack -e tcp.seq -e tcp.len -e tcp.stream -e tcp.urgent_pointer '
                '-e tcp.flags -e tcp.analysis.ack_rtt -e tcp.segments -e tcp.reassembled.length \-e dtls.handshake.extension.len -e dtls.handshake.extension.type -e dtls.handshake.session_id '
                '-e dtls.handshake.session_id_length -e dtls.handshake.session_ticket_length -e dtls.handshake.sig_hash_alg_len -e dtls.handshake.sig_len -e dtls.handshake.version '
                '-e dtls.heartbeat_message.padding -e dtls.heartbeat_message.payload_length -e dtls.heartbeat_message.payload_length.invalid -e dtls.record.content_type -e dtls.record.content_type '
                '-e dtls.record.length -e dtls.record.sequence_number -e dtls.record.version -e dtls.change_cipher_spec -e dtls.fragment.count -e dtls.handshake.cert_type.types_len '
                '-e dtls.handshake.certificate_length -e dtls.handshake.certificates_length -e dtls.handshake.cipher_suites_length -e dtls.handshake.comp_methods_length -e dtls.handshake.exponent_len '
                '-e dtls.handshake.extension.len -e dtls.handshake.extensions_alpn_str -e dtls.handshake.extensions_alpn_str_len -e dtls.handshake.extensions_key_share_client_length '
               f'-e http.request -e udp.port -e frame.time_relative -e frame.time_delta -e tcp.time_relative -e tcp.time_delta > {output_file}')
    os.system(cmd)
    print(output_file)
    step1(output_file)

def extract_header(packet):
    if 'IPv6' in str(packet.layers[0]):
        src_addr = packet.ipv6.src
        dst_addr = packet.ipv6.dst
        # next_header_info = regex.findall(r'(Next Header:)\s(\w.+)\s(\W\d{0,3}\W)', str(packet.layers[1]))
        print(packet.layers)
        if 'ICMPV6' in str(packet.layers):
            icmpv6_type = regex.search(r'(Type:)\s(\w.+)\s(\W\d{0,3}\W)', str(packet.layers[2]))
            msg = f"""Source: {src_addr}\nDestination: {dst_addr}\nType: {icmpv6_type}\nDate and Time: {packet_time}\n"""
        
        elif 'TCP' in str(packet.layers):
            protocol = packet.transport_layer
            src_port = packet[packet.transport_layer].srcport
            dst_port = packet[packet.transport_layer].dstport
            msg = f"""Source: {src_addr}, {src_port}\nDestination: {dst_addr}, {dst_port}\nDate and Time: {packet_time}\n"""
        elif 'UDP' in str(packet.layers):
            protocol = packet.transport_layer
            src_port = packet[packet.transport_layer].srcport
            dst_port = packet[packet.transport_layer].dstport
            msg = f"""Source: {src_addr}, {src_port}\nDestination: {dst_addr}, {dst_port}\nDate and Time: {packet_time}\n"""
    elif 'IPv4' in str(packet.layers[0]):
        src_addr = packet.ip.src
        dst_addr = packet.ip.dst
        if packet.highest_layer == 'ICMP':
            # print(packet['ICMP'].type)
            msg = f"""Source: {src_addr}\nDestination: {dst_addr}\nType: {packet['ICMP'].type}\nDate and Time: {packet_time}\n"""
        else:
            # print(packet[packet.transport_layer])
            src_port = packet[packet.transport_layer].srcport
            dst_port = packet[packet.transport_layer].dstport 
            msg = f"""Source: {src_addr}, {src_port}\nDestination: {dst_addr}, {dst_port}\nDate and Time: {packet_time}\n"""
    elif 'ARP' in str(packet.layers):
        # index = packet['ARP'].find('Sender IP address:')
        pkt = str(packet['ARP'])
        lines = pkt.split('\n')
        src_addr, dst_addr, type = None, None, None
        for line in lines:
            if 'Sender IP address:' in line:
                src_addr = line.split(' ')[3]
            elif 'Target IP address:' in line:
                dst_addr = line.split(' ')[3]
            elif 'Opcode:' in line:
                type = line.split(' ')[1] + line.split(' ')[2]
        # print(index = pkt.find('Sender IP address:'))
        msg = f"""Source: {src_addr}\nDestination: {dst_addr}\nType: {type}\nDate and Time: {packet_time}\n"""
    else:
        msg = 'packet format not support!\n'
    return msg
if __name__ == '__main__':
    interface_name = netifaces.interfaces()
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--time", type=int, default=30, help="capture time(secs), default is 30 secs", required=False)
    ap.add_argument("-i", "--interface", default='lo', help="capture interface, default is lo", required=False)
    ap.add_argument("-f", "--bpf_filter", default=None, help="packet bpf filter, default is None", required=False)
    ap.add_argument("-d", "--detection", help="ddos detection, analyze .pcap file", required=False)
    ap.add_argument("-p", "--parse", help="parse .pcap to .csv file with ddos required arguments", required=False)
    ap.add_argument("--csv", action='store_true', help="also output .csv file with ddos required arguments", required=False)
    args = vars(ap.parse_args())

    if args['detection'] is not None:
        verify.verify(str(args['detection']))
    elif args['parse'] is not None:
        run_parse(args['parse'])
        
    else:
        # print(args['time'], args['interface'])
        date = datetime.datetime.now()
        file = '/home/iammrchen/Desktop/nscap/final/static/' + str(date.time()) + '.pcap'
        output = open(file, 'w')
        os.chmod(file, 0o777)
        # cap_interface = 'lo'
        # capture_time = 30 # in seconds
        # if(args['time'] is not None):
        capture_time = int(args['time'])
        # if(args['interface'] is not None):
        cap_interface = str(args['interface'])
        # if(args['display_filter'] is not None):
        cap_filter = args['bpf_filter']
        # print(cap_filter)
        capture = pyshark.LiveCapture(bpf_filter=cap_filter, interface=cap_interface, output_file=file, )
        capture.set_debug()
        time_start = time.time()
        # sniffing = capture.sniff(timeout=capture_time)
        for packet in capture.sniff_continuously():
            if(time.time()- time_start > capture_time):
                break
            proto = packet.transport_layer
            packet_time = packet.sniff_time
            src_addr, src_port, dst_addr, dst_port = None, None, None, None
            if proto != None:
                print(proto, end=' ')
            print(packet.highest_layer, packet.layers)
            msg = extract_header(packet)
            print(msg)
        print(f'output pcap to {file}')
        if args['csv']:
            run_parse(file)
        output.close()
