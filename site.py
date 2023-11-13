
class Site:
    def __init__(self,
                 temperatures,
                 capacity,
                 init_biomass,
                 growth_data_frame
                 ):

        self.temp_array = temperatures
        self.capacity = capacity
        self.init_biomass = init_biomass
        self.growth_data_frame = self.calculate_growth_frame()

    def calculate_growth_frame(self):
        return None

