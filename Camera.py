from Location import Location

class Camera:
    num_persons=3
    time=[]
    people = {}

    def __init__(self,num_persons):
        self.num_persons=num_persons
        print('num people= ',num_persons)
        self.caliberate_data()

    def caliberate_data(self):

        for i in range(self.num_persons):
            self.people.update({str(i):{'X':[0],'Y':[0],'time':[0]}})
        print('caliberation done')
        print(self.people)


    def setup_people(self,data,time):
        for i in range(self.num_persons):

            y=data[i][:,0]
            x=data[i][:,1]
            self.people[str(i)]['X'].append(x)
            self.people[str(i)]['Y'].append(y)
            self.people[str(i)]['time'].append(time)




