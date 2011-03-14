#!/usr/bin/env python

import os, sys
import pickle
import socket
import hashlib
from ConfigParser import ConfigParser

from lib.vmCommand import *
from lib.vmResult import *

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
            fin = open(filename, "r")

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
            
        except IOError as e:
            raise e
    
    def _print(self):
        print "Number of VM: %s\nMemory size: %s\nPublic IP: %s\nStart IP: %s\n" \
                % (self._VM_NR, self._mem_size, self._public_ip, self._start_ip)

class vCluster:

    def __init__(self):
        self._configFilename = "vcluster.conf"
        try:
            config = ConfigParser()
            config.read(self._configFilename)
            self._hostname = config.get("server", "hostname")
            self._hostport = config.get("server", "port")
            self._passwd = config.get("server", "passwd")
        except ConfigParser.Error as e:
            print e

    def run(self, args):

        action = args[0]
        if action == "create":
            if len(args) < 2:
                self.printHelp()
            else:
                self._templateFilename = args[1]
                self._actionCreate()
        elif action == "list":
            self._actionList()
        elif action == "destroy":
            if len(args) < 2:
                self.printHelp
            else:
                self._actionDestroy(int(args[1]))
        elif action == "help":
            self.printHelp()
        else:
            self.printHelp()

    @staticmethod
    def printHelp():
            print "Usage: ./vcluster.py <action> [args]\n"
            print "Action list:"
            print "\tcreate\tcreate a cluster according to the given template"
            print "\t\t\te.g.: ./vcluster.py create templateFilename"
            print "\tdestroy\tdestroy the cluster acorrding to the given cluster ID"
            print "\t\t\te.g.: ./vcluster.py destroy 1"
            print "\tlist\tlist all running clusters and their status"
            print "\t\t\te.g.: ./vcluster.py list"
            print "\thelp\tprint this help information"
            print "\t\t\te.g.: ./vcluster.py help"
            print "\n\n"
            print "Notice:\n"
            print "Before running the vcluster.py, please make sure you set the current \n"\
                  "remote server ip, port, and your access password in the ./vcluster.conf file"
            print "Example vcluster.conf:"
            print "[server]"
            print "hostname=cloud.cs.hku.hk"
            print "port=57305"
            print "passwd=1234567"


    def _actionCreate(self):

        try:
            analyzer = confAnalyzer(self._templateFilename)
            package = pickle.dumps(analyzer.command, 2)
        except IOError:
            print "Fail to read the configuration file"
            self.printHelp()
            return
        except Exception as e:
            print e
            self.printHelp()
            return

        sender = Sender(self._hostname, self._hostport)
        
        try:
            retMsg = sender.send(package)
            result = pickle.loads(retMsg)

            if result.retCode == 0:
                print result.msg
                for cluster in result.clusters:
                    print cluster
            else:
                print "ERROR %s: %s" % (result.retCode, result.msg)

        except SenderError as error:
            print error

    def _actionList(self):
        command = vmCommand()
        command.commID = 2

        package = pickle.dumps(command, 2)

        sender = Sender(self._hostname, self._hostport)
        
        try:
            retMsg = sender.send(package)
            result = pickle.loads(retMsg)

            if result.retCode == 0:
                print result.msg
                for cluster in result.clusters:
                    print cluster
            else:
                print "ERROR %s: %s" % (result.retCode, result.msg)

        except SenderError as error:
            print error

    def _actionDestroy(self, id):
        command = vmCommand()
        command.commID = 1
        command.commGeneralArgs.append(id)

        package = pickle.dumps(command, 2)

        sender = Sender(self._hostname, self._hostport)
        
        try:
            retMsg = sender.send(package)
            result = pickle.loads(retMsg)

            if result.retCode == 0:
                print result.msg
            else:
                print "ERROR %s: %s" % (result.retCode, result.msg)

        except SenderError as error:
            print error

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        vCluster.printHelp()
    else:
        vcluster = vCluster()
        vcluster.run(sys.argv[1:])

