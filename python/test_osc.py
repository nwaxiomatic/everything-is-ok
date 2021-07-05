from OSC import OSCServer, OSCClient, OSCMessage
import sys
from time import sleep

server = OSCServer( ("192.168.1.138", 9991) )
server.timeout = 0
run = True

client = OSCClient()
client.connect( ("localhost", 9999) )


m = OSCMessage("/test")
m.append("mp3")
client.send( m )

server.close()
client.close()