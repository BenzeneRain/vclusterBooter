# Use this class to return the command
# execution results
class vmCommandResult:

    def __init__(self):
        self.retCode = 0
        self.msg = ""
        self.clusters = []

class vClusterInstance:
    
    def __init__(self):
        self.id = 0
        self.vmNR = 0
        # network format (public/private, name, ip, id)
        
        self.networks = []
        self.vmInstances = []

    def __str__(self):
        str = ""
        str += "===============================================================\n"
        str += "vClusterID\t# of VM\t\n"
        str += "---------------------------------------------------------------\n"
        str += "%d\t\t%d\n" % (int(self.id), int(self.vmNR))
        str += "---------------------------------------------------------------\n"
        str += "Networks:                                                      \n"
        str += "---------------------------------------------------------------\n"
        str += "ID\t\tName\t\tType\tMode\tIP                                     \n"
        
        for network in self.networks:
            str += "%d\t%s\t%s\t%s\t%s\n" % \
                    (int(network.id), network.name[:12], network.type,\
                    network.mode, network.IP)
            str += "\n"

        str += "---------------------------------------------------------------\n"
        str += "Virtual Machines:\n"
        str += "---------------------------------------------------------------\n"
        str += "ID\t\tName\t\tMemory(MB)\t\tNetworks\t\t\tIP\t\t\tDisks\t\tStatus  \n"
        str += "---------------------------------------------------------------\n"

        for vminst in self.vmInstances:
            str += "%d\t%s\t%d\t" % (int(vminst.id), vminst.name[:12], int(vminst.memSize))

            spaceShift = " " * len(str)
            
            maxLoop = max(len(vminst.networkName), len(vminst.disks), len(vminst.ips))
            
            for i in range(maxLoop):
                if i < 0:
                    str += spaceShift

                if i < len(vminst.networkName):
                    network = vminst.networkName[i]
                    str += "%s\t" % (network[:16], )
                else:
                    str += "\t" * 5

                if i < len(vminst.ips):
                    ip = vminst.ips[i]
                    str += "%s\t" % (ip,)
                else:
                    str += "\t" * 5
                    
                if i < len(vminst.disks):
                    disk = vminst.disks[i]
                    str += "%s\t" % (disk, )
                else:
                    str += "\t" * 5

        str += "===============================================================\n"

        return str

class vmInstance:

    def __init__(self):
        self.name = ""
        self.status = "N/A"
        self.id = 0
        self.memSize = 0
        self.networkName = []
        self.ips = []
        self.disks = []

class vNetInstance:
    
    def __init__(self):
        self.id = 0
        self.name = ""
        self.type = ""
        self.mode = ""
        self.IP = ""

# Prohabit it from running itself
if __name__ == '__main__':
    pass
