class fieldSector(object):
    #
    # defines a 5 by 5 section of the field
    #
    def __init__(self,
                 terrain='Normal',  # Normal, Difficult
                 lighting='Normal'  # Bright, Normal, Dim, Dark
                 ):
        self.terrain = terrain
        self.lighting = lighting
        self.occupied = False
        self.occupiedBy = None
        self.occupiedByIndex = None

    def occupySector(self,
                     identifierName=None,
                     identifierIndex=None):
        self.occupied = True
        self.occupiedBy = identifierName
        self.occupiedByIndex = identifierIndex

    def leaveSector(self):
        self.occupied = False
        self.occupiedBy = None
        self.occupiedByIndex = None
