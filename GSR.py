class GSR:

    gsr_data = []
    pulse = []
    time = []

    def update_gsr_data(self,gsr_data,pulse,time):
        self.gsr_data.append(gsr_data)
        self.pulse.append(pulse)
        self.time.append(time)

