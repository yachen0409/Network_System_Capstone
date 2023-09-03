from mininet.topo import Topo
from mininet.link import TCLink
import os

class Topology(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
	
	# Add hosts into topology
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')

        # Add switches into topology
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links into topology
        self.addLink(s1, h1, port1=1)
        self.addLink(s1, h2, port1=2)
        self.addLink(s1, h3, port1=3)
        self.addLink(s1, h4, port1=4)
        self.addLink(s2, h5, port1=1)
        self.addLink(s2, h6, port1=2)
        self.addLink(s2, h7, port1=3)
        self.addLink(s2, h8, port1=4)

topos = {
    'topo': (lambda: Topology())
}