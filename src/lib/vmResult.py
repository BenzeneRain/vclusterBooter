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
        str += "==============================================================="
        str += "vClusterID\t# of VM\t"
        str += "---------------------------------------------------------------"
        str += "Networks:                                                      "
        str += "---------------------------------------------------------------"
        str += "Name\t\t\t\tType\tMode\tIP                                     "
        
        for network in self.networks:
            if network[0] == "private":
                str += "%s\t%s\tRANGE\t%s" % (network[1], network[0], network[2])
            elif network[0] == "public":
                str += "%s\t%s\tFIXED\t%s" % (network[1], network[0], network[2])
            else:
                str += "N/A"
            str += "\n"

        str += "---------------------------------------------------------------"
        str += "Virtual Machines:"
        str += "---------------------------------------------------------------"
        str += "ID\tName\tMemory(MB)\tNetworks\t\t\tDisks\t\t\t"

        for vminst in self.vmInstances:
            str += "%s\t%d\t%d\t" % (vminst.id, vminst.name, vminst.memSize)

            for network in vminst.networkName:
                str += "%s\t" % (network, )

            for disk in vminst.disks:
                str += "%s\t" % (disk, )
            str += "\n"
        str += "==============================================================="

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
