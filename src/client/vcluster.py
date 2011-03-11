#!/usr/bin/env python

import os, sys
import socket

class messageSender:
    pass

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

            self._print()
        except IOError:
            print "Fail to read the configuration file"
    
    def _print(self):
        print self._VM_NR, self._mem_size, self._public_ip, self._start_ip

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        print "Usage: ./vcluster.py filename"
    else:
        analyzer = confAnalyzer(sys.argv[1])
