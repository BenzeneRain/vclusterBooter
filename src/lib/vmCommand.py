# define the vmCommand, which will be constructed from the pickle request
# Let's define the commands
#   _commID     Function
#       0       Create vClusters
#       1       Destroy vClusters 
class vmCommand:
    def __init__(self):
        self.commID = -1
        self.commGeneralArgs = {}
        self.cluster = vCluster()
        self.passwdHash = ""

class vCluster:
    def __init__(self):
        self.vmNR = 0
        self.vmTemplates = []
        # networks in formats of {network name: (public/private, networkAddress)}
        self.networks = {}

class vmTemplate:

    def __init__(self):
        self.name = ""
        self.memory = 0
        self.networkNames = []
        self.disks = []

class vDisks:

    def __init__(self):
        self.diskName = ""
        self.diskTarget = ""
        # Whether the disk is the root of the machine 
        self.isRoot = 0


# The template cannot run by itself
if __name__ == '__main__':
    pass
