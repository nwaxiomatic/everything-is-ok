from OSC import OSCServer, OSCClient, OSCMessage
import sys
from time import sleep

server = OSCServer( ("10.0.1.4", 9999) )
server.timeout = 0
run = True

client = OSCClient()
client.connect( ("10.0.1.8", 8888) )

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def user_callback(path, tags, args, source):
    print path
    print tags
    print args
    print source
    # which user will be determined by path:
    # we just throw away all slashes and join together what's left
    user = ''.join(path.split("/"))
    # tags will contain 'fff'
    # args is a OSCMessage with data
    # source is where the message came from (in case you need to reply)
    #print ("Now do something with", user,args[0],args[1]) 

def quit_callback(path, tags, args, source):
    # don't do this at home (or it'll quit blender)
    global run
    run = False

server.addMsgHandler( "/test", user_callback )

# user script that's called by the game engine every frame
def each_frame():
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

# simulate a "game engine"
while run:
    # do the game stuff:
    sleep(1)
    # call user script
    each_frame()
    m = OSCMessage("/pump")
    m.append(0)
    client.send( m )
    print "send on"
    sleep(5)
    m = OSCMessage("/pump")
    m.append(1)
    client.send( m )
    print "send off"
    sleep(5)

server.close()
client.close()