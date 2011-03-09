# define the vmCommand, which will be constructed from the JSON request
# Let's define the commands
#   _commID     Function
#       0       Create vClusters
#       1       Destroy vClusters 
class vmCommand:
    _commID = None
    _commGeneralArgs = None
    _vmTemplates = None

    def __init__(self):
        pass

class vmTemplate:
    _name = None
    _memory = None
    _privateIPs = None
    _publicIPs = None
    def __init__(self):
        pass

class vDisks:
    _diskName = None
    _diskTarget = None
    _isRoot = None

    def __init__(self):
        pass

# The template cannot run by itself
if __name__ == '__main__':
    pass
