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
        str += "%d\t\tself.vmNR\n"
        str += "---------------------------------------------------------------\n"
        str += "Networks:                                                      \n"
        str += "---------------------------------------------------------------\n"
        str += "Name\t\t\t\tType\tMode\tIP                                     \n"
        
        for network in self.networks:
            if network[0] == "private":
                str += "%s\t%s\tRANGE\t%s" % (network[1], network[0], network[2])
            elif network[0] == "public":
                str += "%s\t%s\tFIXED\t%s" % (network[1], network[0], network[2])
            else:
                str += "N/A"
            str += "\n"

        str += "---------------------------------------------------------------\n"
        str += "Virtual Machines:\n"
        str += "---------------------------------------------------------------\n"
        str += "ID\tName\tMemory(MB)\tNetworks\t\t\t\tDisks\t\t\t\n"

        for vminst in self.vmInstances:
            str += "%d\t%s\t%d\t" % (int(vminst.id), vminst.name, int(vminst.memSize))

            for network in vminst.networkName:
                str += "%s\t" % (network, )

            str += "\t"
            for disk in vminst.disks:
                str += "%s\t" % (disk, )
            str += "\n"
        str += "===============================================================\n"

        return str

class vmInstance:

    def __init__(self):
        self.name = ""
        self.id = 0
        self.memSize = 0
        self.networkName = []
        self.disks = []


# Prohabit it from running itself
if __name__ == '__main__':
    pass
