class Fieldsector(object):
    #
    # defines a 5 by 5 section of the field
    #
    def __init__(self,
                 terrain='Normal',  # Normal, Difficult
                 lighting='Normal'  # Bright, Normal, Dim, Dark
                 ):
        self.terrain_options = ["Normal", "Difficult"]
        self.set_terrain(terrain)
        self.original_terrain = self.terrain
        self.lighting_options = ["Bright", "Normal", "Dim", "Dark"]
        self.set_lighting(lighting)
        self.original_lighting = self.lighting
        self.occupied = False
        self.occupied_by = None
        self.occupied_by_index = None

    def set_terrain(self, terrain: str):
        if terrain in self.terrain_options:
            self.terrain = terrain

    def set_lighting(self, lighting: str):
        if lighting in self.lighting_options:
            self.lighting = lighting

    def is_occupied(self) -> bool:
        return self.occupied

    def occupy_sector(self,
                      identifier_name=None,
                      identifier_index=None):
        self.occupied = True
        self.occupied_by = identifier_name
        self.occupied_by_index = identifier_index

    def leave_sector(self):
        self.occupied = False
        self.occupied_by = None
        self.occupied_by_index = None
