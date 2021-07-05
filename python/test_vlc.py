#! /usr/bin/python

#
# Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

import sys
import os.path
import vlc
from PyQt4 import QtGui, QtCore

from time import sleep

from OSC import OSCServer, OSCClient, OSCMessage, OSCClientError

import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])

print get_ip_address('wlan0')

class OSCPlayer(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, video_file, server, client, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    	self.show()
    	self.resize(500,500)
    	self.videoframe.setWindowState(self.videoframe.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
    	self.videoframe.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    	self.videoframe.showFullScreen()
    	self.videoframe.activateWindow()
    	self.videoframe.raise_()

        #OSC Stuff
        self.server = server
	self.server.addMsgHandler( "/ping", self.pingVideo )
        self.server.addMsgHandler( "/play", self.playVideo )
        self.server.addMsgHandler( "/set", self.setVideo )
        self.server.addMsgHandler( "/stop", self.stopVideo )
        self.server.addMsgHandler( "/pause", self.pauseVideo )
        self.server.addMsgHandler( "/quit", self.quitVideo )
        self.server.addMsgHandler( "/refresh", self.refreshVideo )

        self.client = client

        self.video_file = video_file
        self.OpenFile(self.video_file)
        sleep(.2)
        self.mediaplayer.set_position(0)
        self.PlayPause()


    def pingVideo(self, path, tags, args, source):
        print "/ping"
        self.Play()
        sleep(3)
        self.Pause()

    def playVideo(self, path, tags, args, source):
        print "/play"
        self.setVideo(path, tags, args, source)
        self.Play()
    
    def setVideo(self, path, tags, args, source):
        if len(args) > 0:
            self.setVideoFile(args[0])

    def stopVideo(self, path, tags, args, source):
        print "/stop"
        self.Stop()

    def pauseVideo(self, path, tags, args, source):
        print "/pause"
        self.Pause()

    def quitVideo(self, path, tags, args, source):
        print "/quit"
    	#self.videoframe.setWindowFlags(self.videoframe.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.videoframe.setWindowState(self.videoframe.windowState() & QtCore.Qt.WindowMinimized | ~QtCore.Qt.WindowActive)

    def refreshVideo(self, path, tags, args, source):
        print "/refresh"
    	self.videoframe.setWindowState(self.videoframe.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
    	#self.videoframe.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    	#self.videoframe.showFullScreen()
    	#self.videoframe.activateWindow()
    	#self.videoframe.raise_()
        self.Stop()

    def setVideoFile(self, video_file):
        self.video_file = filePath + '/' + video_file
        self.OpenFile(self.video_file)

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI) 
        self.timer.start()

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            #self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            #self.playbutton.setText("Pause")
            self.isPaused = False

    def Play(self):
        """Toggle play/pause status
        """
        if not self.mediaplayer.is_playing():
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            #self.playbutton.setText("Pause")
            self.isPaused = False

    def Pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            #self.playbutton.setText("Play")
            self.isPaused = True

    def Stop(self):
        """Stop player
        """
        #self.mediaplayer.stop()
        #self.playbutton.setText("Play")
        self.mediaplayer.set_position(0)
        self.Pause()

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()
        #sleep(.03)
        #self.mediaplayer.set_position(0)
        #self.PlayPause()

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):

        m = OSCMessage("/test")
        m.append("video")
        try: 
            self.client.send(m)
        except OSCClientError:
            print "Cannot connect to OSC Server"
        self.server.timed_out = False
        # handle all pending requests then return
        while not self.server.timed_out:
            self.server.handle_request()

        if self.mediaplayer.get_time() > self.mediaplayer.get_length() - 300:
            self.mediaplayer.set_position(0)

ipAddress = get_ip_address('wlan0')
server = OSCServer( (ipAddress, 8888) )
server.timeout = 0

client = OSCClient()
client.connect( ("10.0.1.127", 9999) )

def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

filePath = os.path.abspath(os.path.dirname(sys.argv[0]))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    player = OSCPlayer(filePath + '/video.mp4', server, client)
    sys.exit(app.exec_())
