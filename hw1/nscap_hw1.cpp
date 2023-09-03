#include <stdio.h>
#include <iostream>
#include <getopt.h>
#include <stdlib.h>
#include <string>
#include <string.h>
#include <climits>
#include <pcap.h> /* if this gives you an error try pcap/pcap.h */
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>
#include <netinet/if_ether.h> /* includes net/ethernet.h */
#include <ctime>
using namespace std;

int main(int argc, char **argv)
{
    char *optstring = ":i:c:f:";
    int c;
    char *target_dev = "";
    int target_count = 0;
    char *target_filter = "";
    struct option opts[] = {	
        {"interface", 1, NULL, 'i'},
        {"count", 1, NULL, 'c'},
        {"filter", 1, NULL, 'f'},
    };
    while((c = getopt_long(argc, argv, optstring, opts, NULL)) != -1){
        switch(c){
			case 'i':
				target_dev = optarg;
				//cout << "interface " << target_dev << endl;
				break;
			case 'c':
				target_count = stoi(optarg);
				//cout << "count " << target_count << endl;
					break;
			case 'f':
				target_filter = optarg;
				//cout << "filter " << target_filter << endl;
				break;
				case '?':
				cout << "wrong command (unknown option) \n";
				exit(1);
				break;
			case ':':
				cout << "wrong command (missing argument) \n";
				exit(1);
				break;
			default:
				cout << "default\n";
				break;
		}
    }
    if (strlen(target_dev) == 0){
        cout << "wrong command \n";
		exit(1);
    }
    if(strcmp(target_filter, "") == 0 || strcmp(target_filter, "all") == 0){
        target_filter = "";
    }
    //cout << "here now" << endl;
    bool dev_match = false;
    pcap_if_t *alldevs;
    pcap_if_t *dev; 
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t* descr;

    const u_char *packet;
    struct pcap_pkthdr hdr;     /* pcap.h */
    struct ether_header *eptr;  /* net/ethernet.h */
    struct ip *ipptr;
    struct icmphdr *icmpptr;
    struct tcphdr *tcpptr;
    struct udphdr *udpptr;

    if(pcap_findalldevs(&alldevs, errbuf) == -1){
        printf("%s\n",errbuf);
        exit(1);
    }
    for(dev = alldevs; dev != NULL; dev = dev->next){
        //cout << "dev->name: " <<  dev->name << endl;
		//cout << "dev->addr: " <<dev->addresses << endl;
        if(strcmp(dev->name, target_dev) == 0){
	    	dev_match = true;
		} 
    }
    if(!dev_match){
    	cout << "No interface named "<< target_dev <<endl;
		exit(1);
    }
    if(target_count == 0){
    	target_count = INT_MAX;
    }
    
    descr = pcap_open_live(target_dev, 65535, 1, 1, errbuf);
    if(descr == NULL){
        printf("pcap_open_live(): %s\n",errbuf);
        exit(1);
    }
    
    struct bpf_program fcode;
    if(pcap_compile(descr, &fcode, target_filter, 1, 0) < 0){
    	printf("can't compile filter: %s", pcap_geterr(descr));
    }
    if (pcap_setfilter(descr, &fcode) < 0){
        printf("can't set filter: %s", pcap_geterr(descr));
    }

    for(int times = 0; times < target_count; ++times){
		packet = pcap_next(descr,&hdr);
		if(packet == NULL){
			printf("Didn't grab packet\n");
			exit(1);
		}
		
		eptr = (struct ether_header *) packet;
		if (ntohs (eptr->ether_type) == ETHERTYPE_IP){
			ipptr = (struct ip *)(packet + ETHER_HDR_LEN);
			int ip_type = ipptr->ip_p;
			//int ip_len = sizeof(ipptr);
			cout << "Transport type: ";
			if(ip_type == 1){
				cout << "ICMP\n";
			}
			else if(ip_type == 6){
				cout << "TCP\n";
			}
			else if(ip_type == 17){
				cout << "UDP\n";
			}
			else{
				cout << "IPPROTO NUMBER: " << ip_type << endl;
			}
			//cout << ip_len << endl;
			cout << "Source IP: " << inet_ntoa(ipptr->ip_src) << endl;
			cout <<	"Destination IP: " << inet_ntoa(ipptr->ip_dst) << endl;
			if(ip_type == 1){
				icmpptr = (struct icmphdr*)(packet + ETHER_HDR_LEN + 20);
				cout << "ICMP type value: " << to_string(icmpptr->type) << endl;
			}
			else if(ip_type == 6){
				tcpptr = (struct tcphdr*)(packet + ETHER_HDR_LEN + 20);
				cout << "Source port: " << ntohs(tcpptr->th_sport) << endl;
				cout << "Destination port: " << ntohs(tcpptr->th_dport) << endl;
				int offset = tcpptr->th_off << 2;
				int datalen = hdr.len - (ETHER_HDR_LEN+20+offset);
				//cout << "datalen: " << datalen << endl;
				cout << "Payload: ";
				if(datalen > 0){
					if(datalen > 16){
						datalen = 16;
					}
					const u_char *payload = packet+ETHER_HDR_LEN+20+offset;
					int byte_count = 0;
					while(byte_count++ < datalen){
						printf("%02hhX ", *payload);
						payload++;
					}
				}
				cout << endl;
			}
			else if(ip_type == 17){
				udpptr = (struct udphdr*)(packet + ETHER_HDR_LEN + 20);
				cout << "Source port: " << ntohs(udpptr->uh_sport) << endl;
				cout << "Destination port: " << ntohs(udpptr->uh_dport) << endl;
				int datalen = ntohs(udpptr->uh_ulen) - 8;
				//int datalen = (int)udpptr->uh_ulen;	
				//cout << "datalen: " << datalen << endl;
				cout << "Payload: ";
				if(datalen > 0){
					if(datalen > 16){
							datalen = 16;
					}
					const u_char *payload = packet+ETHER_HDR_LEN+20+8;
					int byte_count = 0;
					while(byte_count++ < datalen){
						printf("%02hhX ", *payload);
						payload++;
					}
				}
				cout << endl;	
			}
			cout << endl;
		}	
		else{
			//printf("Ethernet type %x not IP", ntohs(eptr->ether_type));
			times--;
		}
    }
    return 0;
}
