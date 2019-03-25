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

    def occupySector(self):
        self.occupied = True

    def leaveSector(self):
        self.occupied = False
