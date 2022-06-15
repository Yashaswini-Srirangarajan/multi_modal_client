import json
import threading

import websockets
import asyncio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy
from AppConnector import AppConnector
import time

import sys
from FSR import FSR
from GSR import GSR
from EMG import EMG
from SpeechToText import SpeechToText
from Camera import Camera
from ForceMat import ForceMat

class MultiServer:

    #TODO configure arudino to send GSR and Pulse data separately
    #TODO put data in a list or dict

    FSR = FSR()
    GSR = GSR()
    EMG = EMG()
    force_mat = ForceMat()
    speechToText = SpeechToText()
    CALIBERATE_CAM_TWO =False
    CALIBERATE_CAM_ONE =False

    camera_one=Camera(1)
    camera_two=Camera(1)


    GSR_DATA = []
    PULSE_DATA = []
    FSR_DATA = []
    FSR_TIME = []
    CAMERA_ONE_DATA = []
    CAMERA_TWO_DATA = []
    SPEECH_DATA = []
    FORCE_MAT_DATA = []
    EMG_DATA = []


    HOST = ""  # Empty denotes a localhost.
    PORT = 7891

    time1 =0
    time2 =0
    frame_count =0
    fig, axs = plt.subplots(nrows=5, ncols=5)
    CONNECTIONS = set()


    socket_thread = None


    def __init__(self):
        self.exit_thread = threading.Timer(2.0,self.time_and_exit) #exit after 30 seconds
        self.t = threading.Thread(target=self.run)
        #self.plotter_thread = threading.Thread(target=self.plot)

    async def handler(self,websocket):

        self.time1 = time.time()
        self.CONNECTIONS.add(websocket)

        count = 0
        while True:
            try:
                message = await websocket.recv()
                count+=1


                msg_json = json.loads(message)
                sensor_type = msg_json['sensor_type']

                print(sensor_type)
                if(sensor_type == 0):
                    self.process_pulse_data(msg_json)
                elif(sensor_type == 1):
                    self.process_fsr_data(msg_json)
                elif(sensor_type == 2):
                    print('in sensor two')
                    self.process_emg_data(msg_json)
                elif (sensor_type == 3):
                    self.process_force_mat_data(msg_json)
                elif (sensor_type == 4):
                    print(sensor_type)
                    self.process_speech_text_data(msg_json)
                elif (sensor_type == 5):
                    if not self.CALIBERATE_CAM_ONE:
                        print('caliberating cam 1')
                        self.CALIBERATE_CAM_ONE = True
                        num_ppl = len(numpy.asarray(json.loads(msg_json['data'])['array']))

                        self.camera_one = Camera(num_ppl)
                    else:
                        self.process_cam_one_data(msg_json,self.camera_one)
                elif (sensor_type == 6):
                    if not self.CALIBERATE_CAM_TWO:
                        print('caliberating cam 2')
                        self.CALIBERATE_CAM_TWO = True
                        num_ppl = len(numpy.asarray(json.loads(msg_json['data'])['array']))
                        self.camera_two = Camera(num_ppl)
                    else:
                        self.process_cam_one_data(msg_json,self.camera_two)

                # Send a response to all connected client except the server
                #for conn in self.CONNECTIONS:
                    #if conn != websocket:
                        #await conn.send(message)
            except websockets.exceptions.ConnectionClosedError as error1:
                print(f'Server Error: {error1}')
                self.CONNECTIONS.remove(websocket)


    async def main(self):
        async with websockets.serve(self.handler, self.HOST, self.PORT,ping_interval=None,ping_timeout=None):
            await asyncio.Future()  # run forever

    def run(self):
        asyncio.run(self.main())

    def process_pulse_data(self,msg_json):
        #print('in gsr data')
        self.GSR.update_gsr_data(msg_json['gsr'],msg_json['pulse'],msg_json['time'])

    def process_fsr_data(self, msg_json):
        #print('inside fsr data')
        self.FSR.update_fsr_data(msg_json['fsr'],msg_json['time'])

    def process_emg_data(self, msg_json):
        #print('in func emg data')
        self.EMG.update_emg_data(msg_json['emg'],msg_json['time'])

    def process_force_mat_data(self,msg_json):
        #print('in force mat data')
        self.force_mat.update_force_mat_data(msg_json["data"], msg_json["time"])



    def process_speech_text_data(self,msg_json):
        print('in speech 2 text')
        print(msg_json['speech'],msg_json['text'],msg_json['time'])
        self.speechToText.update_speech_to_text_data(msg_json['speech'],msg_json['text'],msg_json['time'])

    def process_cam_one_data(self,msg_json):

        data=msg_json['data']
        self.frame_count+=1
        decodedArrays = json.loads(data)
        finalNumpyArray = numpy.asarray(decodedArrays["array"])
        self.camera_one.setup_people(finalNumpyArray, msg_json['time'])

    def process_cam_two_data(self,msg_json):
        print('in func cam 2 data')
        #print(msg_json)

    async def send_dummy_data(self,websocket):
        print('in dummy data transfer')
        while True:
            try:
                print('going to send a message')
                #await websocket.send('hi')
                await websocket.send(json.dumps(self.prep_data()))
                print('sent')
            except websockets.exceptions.ConnectionClosedError as error1:
                print(f'Server Error: {error1}')


    #def connect_socket_two(self):
        #start_server = websockets.serve(self.send_dummy_data, "localhost", 7892)
        #asyncio.get_event_loop().run_until_complete(start_server)
        #asyncio.get_event_loop().run_forever()

    async def send_to_sockettwo(self):
        print('in send to socket two')
        async with websockets.serve(self.send_dummy_data,'', 7892,ping_interval=None,ping_timeout=None):
            await asyncio.Future()  # run forever

    def dummy_run(self):
        print('sending data to port 7892')
        asyncio.run(self.send_to_sockettwo())

    def collect_data(self):
        self.t.start()


    def prep_data(self):


        data_to_app = {
                        0: {"gsr":self.GSR.gsr_data,
                            "pulse":self.GSR.pulse,
                            "time": self.GSR.time},
                        1: {"fsr":self.FSR.fsr_data,
                            "time":self.FSR.time},
                        2: {"emg":self.EMG.all_channel_data,
                            "time":self.EMG.time},

                        #TODO check data from mat

                        3: {
                            "data":self.force_mat.data,
                            "time":self.force_mat.time
                        },

                        4: {"speech" : self.speechToText.speech,
                            "text": self.speechToText.text,
                            "time": self.speechToText.time },
                        5: {
                            "data" : self.camera_one.people,
                            "time" : self.camera_one.time
                        },
                        6 : {
                            "data": self.camera_two.people,
                            "time": self.camera_two.time
                        }

        }
        print('inside prep_data')
        print(data_to_app)
        return data_to_app



    def animate_plot(self,i):
        # Render plots as a matplotlib animation
        self.axs[0][0].plot(self.FSR.fsr_data,self.FSR.time)
        self.axs[0][1].plot(self.GSR.gsr_data,self.GSR.time)
        self.axs[0][2].plot(self.GSR.pulse, self.GSR.time)
        self.axs[0][3].plot(self.EMG.channel_one, self.EMG.time)
        self.axs[0][4].plot(self.EMG.channel_two, self.EMG.time)
        self.axs[1][0].plot(self.EMG.channel_three, self.EMG.time)
        self.axs[1][1].plot(self.EMG.channel_four, self.EMG.time)
        self.axs[1][2].plot(self.EMG.channel_five, self.EMG.time)
        self.axs[1][3].plot(self.EMG.channel_six, self.EMG.time)
        self.axs[1][4].plot(self.EMG.channel_seven, self.EMG.time)
        self.axs[2][0].plot(self.EMG.channel_eight, self.EMG.time)
        self.axs[2][1].plot(self.EMG.channel_nine, self.EMG.time)
        self.axs[2][2].plot(self.EMG.channel_ten, self.EMG.time)
        self.axs[2][3].plot(self.EMG.channel_eleven, self.EMG.time)
        self.axs[2][4].plot(self.EMG.channel_twelve, self.EMG.time)
        self.axs[3][0].plot(self.EMG.channel_thirteen, self.EMG.time)
        self.axs[3][1].plot(self.EMG.channel_fourteen, self.EMG.time)
        self.axs[3][2].plot(self.EMG.channel_fifteen, self.EMG.time)
        self.axs[3][3].plot(self.EMG.channel_sixteen, self.EMG.time)
        #self.axs[19].plot(self.EMG.channel_sixteen, self.EMG.time)




    def plot(self):
        anim = FuncAnimation(
            self.fig, self.animate_plot, interval=1000
        )
        plt.show()


    def send_to_app(self):
        print('in send to app')
        self.app_socket = AppConnector()
        self.socket_thread=threading.Thread(target=self.app_socket.run())
        #print('socket thread starting')
        self.socket_thread.start()


    def time_and_exit(self):
        print('in time and exit')
        for thread in threading.enumerate():
            print(thread.name)

        self.time2 = time.time()
        time_diff=self.time2 - self.time1
        print('time taken and fps',time_diff,self.frame_count/time_diff)
        #self.exit_thread.join()
        #self.t.join()
        sys.exit()
        print(self.t, self.exit_thread)


    def exit(self):
        #TODO cancel async functions on exit()
        self.exit_thread.start()


if __name__ == "__main__":
    listener = MultiServer()
    listener.collect_data()
    #listener.prep_data()
    #S = threading.Timer(2.0, listener.prep_data())
    #S.start()
    #listener.plot()
    listener.dummy_run()



