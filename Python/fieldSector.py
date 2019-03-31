class fieldSector(object):
    #
    # defines a 5 by 5 section of the field
    #
    def __init__(self,
                 terrain='Normal',  # Normal, Difficult
                 lighting='Normal'  # Bright, Normal, Dim, Dark
                 ):
        self.terrain_options = ["Normal", "Difficult"]
        self.terrain = self.setTerrain(terrain)
        self.lighting_options = ["Bright", "Normal", "Dim", "Dark"]
        self.lighting = self.setLighting(lighting)
        self.occupied = False
        self.occupiedBy = None
        self.occupiedByIndex = None

    def setTerrain(self, terrain):
        if (terrain in self.terrain_options):
            self.terrain = terrain

    def setLighting(self, lighting):
        if (lighting in self.lighting_options):
            self.lighting = lighting

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
