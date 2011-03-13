#!/usr/bin/env python

import os, sys
import pickle
import ConfigParser
import socket
import hashlib
import subprocess
import random
import time

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
    def run(self, sleepCycle = 0):
        if self._command is None:
            return [400, "No command found"]
        
        if(self._command.commID == 0):
            networkNameMap = {}
            vnetFilename = ""
            networkNames = self._command.cluster.networks.keys()
            numberOfNames = len(networkNames)
            # First add virtual networks
            for networkIndex in range(numberOfNames):
                networkName = networkNames[networkIndex]
                networkSetting = self._command.cluster.networks[networkName]
                if(networkSetting[0] == "private"):
                    bridge = "eth1"

                    networkTemplate = "NAME = \"%s\"\nTYPE = FIXED\nBRIDGE = %s\n"

                    hash = hashlib.sha1(networkName + "-" + str(random.random()))
                    UID = networkName + "-" + str(hash.hexdigest());
                    networkNameMap[networkName] = UID

                    networkTemplate = networkTemplate % (UID, bridge) 

                    # add the LEASES = [IP=X.X.X.X] part
                    for i in range(int(self._command.cluster.vmNR)):
                        lease = "LEASES = [IP=%s]\n"

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
                        proc = subprocess.Popen(["onevnet", "create", vnetFilename])
                        proc.wait()
                    except:
                        raise commandEngineError(420, "Fail to create vnet using"\
                                " command onevnet and vnet template file %s" % vnetFilename)

                    # delete the vnet template file after we create the vnet
                    os.remove(vnetFilename)
                else:
                    # we do not need to care generating the vnetwork template for the public network
                    continue

            # Second create virtual machines
            headerTemplate = """
NAME = "%s"
MEMORY = %s
OS = [
        bootloader = "/usr/bin/pygrub",
        root = "%s"]
"""
            footerTemplate = "REQUIREMENTS = \"FREEMEMORY > %s\"\nRANK = \"- RUNNING_VMS\"\n"

            nicWithoutIPTemplate = "NIC = [NETWORK = \"%s\"]\n"
            nicWithIPTemplate = "NIC = [NETWORK = \"%s\", IP=%s]\n"

            diskTemplate = """
DISK = [
            source = "/srv/cloud/images/%s",
            target = "%s",
            readonly = "no",
            clone = "no"]
"""
                
            for vmIndex in range(int(self._command.cluster.vmNR)):
                template = self._command.cluster.vmTemplates[vmIndex]
                
                rootDevice = ""

                diskList = ""
                for diskInfo in template.disks:
                    diskDesc = diskTemplate % (diskInfo.diskName, diskInfo.diskTarget) 
                    if int(diskInfo.isRoot) != 0:
                        rootDevice = diskInfo.diskTarget
                    diskList += diskDesc

                if rootDevice == "":
                    return [501, "Cannot find the root device"]

                header = headerTemplate % (template.name, template.memory, rootDevice) 
                footer = footerTemplate % (str(int(template.memory) * 1024), )

                nicList = ""
                for nic in template.networkNames:
                    (networkType, networkAddress) = self._command.cluster.networks[nic]

                    if networkType == "Public":
                        nicDesc = nicWithIPTemplate % (networkNameMap[nic], networkAddress)
                    else:
                        nicDesc = nicWithoutIPTemplate % (networkNameMap[nic], )                     
                    nicList += nicDesc

                content = header + diskList + nicList + footer

                # write the template to the file
                hash = hashlib.sha1(str(random.random()))
                vmFilename = "/tmp/" + hash.hexdigest() + ".vm"

                fout = open(vmFilename, "w")
                fout.write(content)
                fout.close()

                # create the vnet
                try:
                    proc = subprocess.Popen(["onevm", "create", vmFilename])
                    proc.wait()
                except:
                    raise commandEngineError(420, "Fail to create vm using"\
                            " command onevm and vm template file %s" % vmFilename)

                os.remove(vmFilename)
                
                time.sleep(sleepCycle)

            return [0, "successful"]
        elif(self._command.commID == 1):
            return [401, "Undefined command"]
        else:
            return [401, "Undefined command"]

class Listener:
    _bindAddress = None
    _bindPort = 57305

    _sock = None

    # Constructor
    def __init__(self, hostname = 'localhost', hostport = 57305):

        self._bindAddress = socket.gethostbyname(hostname)
        self._bindPort = hostport

    # Running the Listner, which will listen for the incoming events
    def run(self, sleepCycle = 0):

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

            rawData = self._readMessages(conn)
            if len(rawData) > 0:
                try:
                    vmCommand = pickle.loads(rawData)
                    engine = commandEngine(vmCommand)
                    [ret, msg] = engine.run(sleepCycle)
                except commandEngineError as e:
                    msg = str(e)
                    print msg
                except:
                    msg = "Unknown Error"
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

        return rawData

    # send the execution result back
    def _sendMessage(self, conn, msg):
        conn.send(msg)

    def close(self):
        if(self._sock is not None):
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
            self._vmCreateCycle = config.get('server', 'vmCreateCycle')

            print "Hostname is %s, port is %s" % (self._hostname, self._hostport)

            # Run the listener
            self._listener = Listener(self._hostname, self._hostport)
            ret = self._listener.run(int(self._vmCreateCycle))

        except ConfigParser.Error:
            print "Failed to read the configuration" 
        except IOError:
            if(self._listener is not None):
                self._listener.close()
            print "Failed to open the configuration File"
        except commandEngineError as e:
            if(self._listener is not None):
                self._listener.close()
            print e
        except KeyboardInterrupt as ki:
            if(self._listener is not None):
                self._listener.close()
            print ki
        except:
            if(self._listener is not None):
                self._listener.close()
            print "Unknown problem happens while reading configs"

if __name__ == '__main__':

    #TODO: We can add some command line config supporting here
    booter = vClusterBooterd()
