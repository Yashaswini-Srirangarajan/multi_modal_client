from Location import Location

class Camera:
    num_persons=3
    time=[]
    people = []

    def __init__(self):
        self.num_persons=3

    def setup_people(self,data,time):
        for i in range(self.num_people):
            print(data[i])
            print(data[i][0])

            person = Location.update_location_data(data[i][0:],data[i][1:],time)
            self.people.append(person)


