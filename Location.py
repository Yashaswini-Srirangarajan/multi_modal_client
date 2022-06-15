class Location:
    X=[]
    Y=[]
    time=[]

    def update_location_data(self,x,y,t):

        self.X.append(x)
        self.Y.append(y)
        self.time.append(t)