from NumpyArrayEncoder import NumpyArrayEncoder
import json

class Camera:
    num_persons=3
    time=[]
    people = {}

    def __init__(self,num_persons,n_latest):
        self.num_persons=num_persons
        #print('num people= ',num_persons)
        self.caliberate_data()
        self.n_latest = n_latest

    def caliberate_data(self):

        for i in range(self.num_persons):
            self.people.update({str(i):{'X':[0],'Y':[0],'time':[0]}})
        #print('caliberation done')
        #print(self.people)


    def setup_people(self,data,time):
        for i in range(self.num_persons):
            x,y= zip(* data["data"][i][:])

            x = list(x)
            y = list(y)
            #print(x)
            #print(y)

            self.people[str(i)]['X'].append(x)
            self.people[str(i)]['Y'].append(y)
            self.people[str(i)]['time'].append(time)
        #print('people',self.people)


    def get_latest_data(self):
        last_1000_data = {}
        for i in range(self.num_persons):
            x=self.get_last_n_data(self.people[str(i)]['X'])
            y=self.get_last_n_data(self.people[str(i)]['Y'])
            t=self.get_last_n_data(self.people[str(i)]['time'])
            print(len(x),len(y),len(t))
            last_1000_data.update({str(i): {'X': x, 'Y': y, 'time': t}})

        return last_1000_data


    def get_last_n_data(self,data):

        if(len(data)<self.n_latest):
            return data
        else:
            return data[-self.n_latest:]




