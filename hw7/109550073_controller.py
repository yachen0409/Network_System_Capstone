from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import in_proto

DEFAULT_FILTER_TABLE = 0
FILTER_TABLE_ONE = 1
FILTER_TABLE_TWO = 2
FORWARD_TABLE = 3

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.add_default_table(datapath)
        self.add_filter_table_1(datapath)
        self.apply_filter_table_1_rules(datapath)
        self.add_filter_table_2(datapath)
        self.apply_filter_table_2_rules(datapath)
        
        

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, table_id=FORWARD_TABLE,
                                instructions=inst)
        datapath.send_msg(mod)

    def add_default_table(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FILTER_TABLE_ONE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=0, instructions=inst)
        datapath.send_msg(mod)

    # def apply_default_table_rules(self, datapath):
    #     ofproto = datapath.ofproto
    #     parser = datapath.ofproto_parser
    #     match = parser.OFPMatch()
    #     actions = [parser.OFPInstructionGotoTable(FILTER_TABLE_ONE)]
    #     mod = parser.OFPFlowMod(datapath=datapath, table_id=DEFAULT_FILTER_TABLE,
    #                             priority=0, match=match, instructions=actions)
    #     datapath.send_msg(mod)

    def add_filter_table_1(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE_ONE, priority=1, match=match, instructions=inst)
        datapath.send_msg(mod)

    def add_filter_table_2(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE_TWO, priority=1, match=match, instructions=inst)
        datapath.send_msg(mod)

    def apply_filter_table_1_rules(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match_icmp = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_ICMP)
        inst = [parser.OFPInstructionGotoTable(FILTER_TABLE_TWO)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE_ONE,
                                priority=10000, match=match_icmp, instructions=inst)
        datapath.send_msg(mod)
    def apply_filter_table_2_rules(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match3 = parser.OFPMatch(in_port=3)
        actions = []
        mod3 = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE_TWO,
                                priority=10000, match=match3, instructions=actions)
        datapath.send_msg(mod3)

        match4 = parser.OFPMatch(in_port=4)
        mod4 = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE_TWO,
                                priority=10000, match=match4, instructions=actions)
        datapath.send_msg(mod4)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src
        in_port = msg.match['in_port']
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

         # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)