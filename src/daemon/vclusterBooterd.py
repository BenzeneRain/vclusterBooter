#!/usr/bin/env python

import os, sys
import pickle
import ConfigParser
import socket
import hashlib
import subprocess
import random

from lib.vmCommand import *

#WARNING: This program is written in Python 2.6

class commandEngineError:
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg
    def __str__(self):
        return "Command Engine Execute Error %d: %s" % (self.value, self.msg)

class commandEngine:

    _command = None

    def __init__(self, command):
        self._command = command

    # execute the command
    # return: [ret, msg]
    # ret is the return code
    # msg is the message that explains the code
    def run(self):
        if(self._command != None):

            if(self._command.commID == 0):

                networkNameMap = {}
                vnetFilename = ""
                # First add virtual networks
                for networkName in self._command.cluster.networks:
                    networkSetting = self._command.cluster.networks[networkName]
                    if(networkSetting[0] == "private"):
                        bridge = "eth1"

                        networkTemplate = "NAME = %s\nTYPE = FIXED\nBRIDGE = %s\n"

                        hash = hashlib.sha1(networkName + " - " + str(random.random()))
                        UID = networkName + " - " + str(hash.hexdigest());
                        networkNameMap[networkName] = UID

                        networkTemplate = networkTemplate % (UID, bridge) 

                        # add the LEASE = [IP=X.X.X.X] part
                        for i in range(int(self._command.cluster.vmNR)):
                            lease = "LEASE = [IP=%s]\n"

                            # We need to do the check here
                            ipaddr = networkSetting[1]
                            addrParts = ipaddr.split(".");
                            addrParts[3] = str(int(addrParts[3]) + i)
                            ipaddr = ".".join(addrParts)

                            lease = lease % (ipaddr, )
                            networkTemplate += lease

                        # write the template to the file
                        hash = hashlib.sha1(str(random.random()))
                        vnetFilename = "/tmp/" + hash.hexdigest() + ".vnet"

                        fout = open(vnetFilename, "w")
                        fout.write(networkTemplate)
                        fout.close()

                        # create the vnet
                        try:
                            proc = subprocess.Popen(["onevnet", "create", "vnetFilename"])
                            proc.wait()
                        except:
                            raise commandEngineError(420, "Fail to create vnet using"\
                                    " command onevnet and vnet template file %s" % vnetFilename)

                        # delete the vnet template file after we create the vnet
                        os.remove(vnetFilename)
                    else:
                        # we do not need to care generating the vnetwork template for the public network
                        pass


                # Second create virtual machines

            elif(self._command.commID == 1):
                pass
            else:
                return [401, "Undefined command"]

        else:
            return [400, "No command found"]

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

        # Apply for a socket
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

            vmCommand = self._readMessages(conn)
            if vmCommand != None:
                try:
                    engine = commandEngine(vmCommand)
                    [ret, msg] = engine.run()
                except commandEngineError as e:
                    msg = str(e)
                    print msg
            else:
                ret = 404 
                msg = "ERROR 404, failed to extract the vmCommand packets"

            self._sendMessage(conn, msg)
            conn.close()

    # read and extract messages
    def _readMessages(self, conn):
        rawDataSeg = conn.recv(4096)
        rawData = rawDataSeg

        while(len(rawData) == 4096):
            rawDataSeg = conn.recv(4096)
            rawData.extend(rawDataSeg)

        return pickle.loads(rawData)

    # send the execution result back
    def _sendMessage(self, conn, msg):
        conn.send(msg)

    def close(self):
        if(self._sock != None):
            self._sock.close()
            self._sock = None


# handling events 
class vClusterBooterd:

    _hostname = None
    _hostport = None
    _listener = None

    def __init__(self, configFilename = 'vclusterBooterd.conf'):
        try:
            random.seed()

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
            if(self._listener != None):
                self._listener.close()
            print "Failed to open the configuration File"
        except commandEngineError as e:
            if(self._listener != None):
                self._listener.close()
            print e
        except KeyboardInterrupt as ki:
            if(self._listener != None):
                self._listener.close()
            print ki
        except:
            if(self._listener != None):
                self._listener.close()
            print "Unknown problem happens while reading configs"

if __name__ == '__main__':

    #TODO: We can add some command line config supporting here
    booter = vClusterBooterd()
