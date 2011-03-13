#!/usr/bin/env python

import os, sys
import pickle
import socket
import hashlib
from ConfigParser import ConfigParser

from lib.vmCommand import *

class SenderError:
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg
    def __str__(self):
        return "Sender Error " + repr(self.value) + ": " + self.msg

class Sender:
    def __init__(self, hostname = "localhost", hostport = 57305):
        self._remoteAddress = socket.gethostbyname(hostname)
        self._remotePort = hostport

    def send(self, packet):

        # Apply for a socket
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            self._sock = None
            raise SenderError(-1, "Failed to create socket")

        try:
            self._sock.connect((self._remoteAddress, int(self._remotePort)))
        except socket.error, msg:
            self._sock.close()
            self._sock = None
            raise SenderError(-2, "Fail to connect to the remote server on %s:%s"\
                    % (self._remoteAddress, self._remotePort))

        try:
            self._sock.send(packet)
            dataSeg = self._sock.recv(4096)
            data = dataSeg

            while(len(dataSeg) == 4096):
                dataSeg = self._sock.recv(4096)
                data.extend(dataSeg)

        except socket.error, msg:
            self._sock.close()
            self._sock = None
            raise SenderError(-3, "Fail to send & receive message from the server")

        return data


class confAnalyzer:

    def __init__(self, filename):

        self._VM_NR = ""
        self._mem_size = ""
        self._public_ip = ""
        self._start_ip = ""
        
        self._keywords = ["VM_NR", "MEM_SIZE", "PUBLIC_IP",
                "START_IP"]

        try:
            fin = open(filename)

            rawConfigs = fin.read();
            fin.close()

            # Read configs
            rawConfigs = rawConfigs.split("\n")
            for line in rawConfigs:
                items = line.split("=")
                if(len(items) != 2):
                    continue
                
                for index in range(len(self._keywords)):
                    if(items[0] == self._keywords[index]):
                        if(index == 0):
                            self._VM_NR = items[1]
                        elif(index == 1):
                            self._mem_size = items[1]
                        elif(index == 2):
                            self._public_ip = items[1]
                        elif(index == 3):
                            self._start_ip = items[1]

                        break

            # Print out configs
            self._print()

            command = vmCommand() 
            command.commID = 0
            command.cluster.vmNR = self._VM_NR
            command.cluster.networks["pubnet"] = ("public", self._public_ip)
            command.cluster.networks["privnet"] = ("private", self._start_ip)

            vdisk = vDisks()
            vdisk.diskName = "1"
            vdisk.diskTarget = "sda1"
            vdisk.isRoot = 1

            privTemplate = vmTemplate()
            privTemplate.name = "vClusterPrivVM"
            privTemplate.memory = self._mem_size
            privTemplate.networkNames = ["privnet"]
            privTemplate.disks = [vdisk]

            pubTemplate = vmTemplate()
            pubTemplate.name =  "vClusterGateVM"
            pubTemplate.memory = self._mem_size
            pubTemplate.networkNames = ["privnet", "pubnet"]
            pubTemplate.disks = [vdisk]

            for i in range(int(self._VM_NR) - 1):
                command.cluster.vmTemplates.append(privTemplate)
            command.cluster.vmTemplates.append(pubTemplate)
            
            self.command = command
            
        except IOError:
            print "Fail to read the configuration file"
    
    def _print(self):
        print "Number of VM: %s\nMemory size: %s\nPublic IP: %s\nStart IP: %s\n" \
                % (self._VM_NR, self._mem_size, self._public_ip, self._start_ip)

class vCluster:

    def __init__(self, templateFilename, configFilename):
        self._templateFilename = templateFilename
        self._configFilename = configFilename

    def run(self):
        config = ConfigParser()
        config.read(self._configFilename)
        self._hostname = config.get("server", "hostname")
        self._hostport = config.get("server", "port")
        self._passwd = config.get("server", "passwd")

        analyzer = confAnalyzer(self._templateFilename)
        package = pickle.dumps(analyzer.command, 2)

        sender = Sender(self._hostname, self._hostport)
        
        try:
           retMsg = sender.send(package)
           print retMsg
        except SenderError as error:
            print error

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        print "Usage: ./vcluster.py filename"
    else:

        vcluster = vCluster(sys.argv[1], "vcluster.conf")
        vcluster.run()

