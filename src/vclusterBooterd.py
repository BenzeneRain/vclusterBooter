#!/usr/bin/env python

import os, sys
import json
import ConfigParser
import socket

import vmCommand

#WARNING: This program is written in Python 2.6

class commandEngine:

    def __init__(self, command):
        pass

class Listener:
    _bindAddress = None
    _bindPort = 57305

    _sock = None

    # Constructor
    def __init__(self, hostname = 'localhost', hostport = 57305):

        self._bindAddress = socket.gethostbyname(hostname)
        self._bindPort = hostport

    # Running the Listner, which will listen for the incoming events
    def run(self):

        # Apply a socket
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            self._sock = None
            print "Failed to create socket on %s:%s" % (self._bindAddress, self._bindPort)
            return -1

        # bind the address and port on the socket, and listen on it
        try:
            self._sock.bind((self._bindAddress, int(self._bindPort)))
            self._sock.listen(5)
        except socket.error, msg:
            self._sock.close()
            self._sock = None
            print "Failed to create bind and listen on the socket"
            return -1
        except:
            print "Failed to create bind and listen on the socket"
            return -1
        

        # Infinite loop for request handling
        # No need to use multithread here
        while(1):
            conn, addr = self._sock.accept()
            print "Connection from ", addr

            vmCommand = _readMessage(conn)
            if vmCommand != None:
                engine = commandEngine(vmCommand)
                [ret, msg] = engine.run()
            else:
                ret = 404 
                msg = "ERROR 404, failed to extract the vmCommand packets"

            conn.sendall(msg)
            conn.close()

    # read and extract messages
    def _readMessages(conn):
        rawDataSeg = conn.recv(4096)
        rawData = rawDataSeg

        while(len(rawData) == 4096):
            rawDataSeg = conn.recv(4096)
            rawData.extend(rawDataSeg)

        return json.loads(rawData)

    # send the execution result back
    def _sendMessage(conn):
        pass


# handling events 
class vClusterBooterd:

    _hostname = None
    _hostport = None
    _listener = None

    def __init__(self, configFilename = 'vclusterBooterd.conf'):
        try:

            # read the configs from the configuration file
            config = ConfigParser.ConfigParser()
            config.read(configFilename)
    
            self._hostname = config.get('server', 'hostname')
            self._hostport = config.get('server', 'port')

            print "Hostname is %s, port is %s" % (self._hostname, self._hostport)

            # Run the listener
            self._listener = Listener(self._hostname, self._hostport)
            ret = self._listener.run()

        except ConfigParser.Error:
            print "Failed to read the configuration" 
        except IOError:
            print "Failed to open the configuration File"
        except:
            print "Unkown problem happens while reading configs"

if __name__ == '__main__':

    #TODO: We can add some command line config supporting here
    booter = vClusterBooterd()
