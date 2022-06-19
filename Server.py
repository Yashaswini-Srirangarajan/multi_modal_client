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
    CALIBERATE_CAM_TWO = False
    CALIBERATE_CAM_ONE = False
    cam_rate = 1
    sensor_rate = 1000
    camera_one = Camera(1, cam_rate)
    camera_two = Camera(1, cam_rate)


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
    fig, axs = plt.subplots()
    CONNECTIONS = set()
    CONNECTIONS_port_two = set()


    socket_thread = None


    def __init__(self):
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
                    #print("Sensor : GSR and Pulse streaming")
                    self.process_pulse_data(msg_json)
                elif(sensor_type == 1):
                    #print("Sensor : FSR streaming")
                    self.process_fsr_data(msg_json)
                elif(sensor_type == 2):
                    #print('EMG channels streaming')
                    self.process_emg_data(msg_json)
                elif (sensor_type == 3):
                    #print("Force mat streaming")
                    self.process_force_mat_data(msg_json)
                elif (sensor_type == 4):
                    print("Converting Text to speech")
                    self.process_speech_text_data(msg_json)
                    print("Speech : ",msg_json["speech"])
                    print("Text : ",msg_json["text"])
                elif (sensor_type == 5):
                    #print("camera 1 streaming")
                    if not self.CALIBERATE_CAM_ONE:
                        print('caliberating cam 1')
                        self.CALIBERATE_CAM_ONE = True
                        num_ppl = len(numpy.asarray(msg_json['data']))

                        self.camera_one = Camera(num_ppl,self.cam_rate)
                    else:
                        print('Cam data')
                        self.process_cam_one_data(msg_json,self.camera_one)
                elif (sensor_type == 6):
                    if not self.CALIBERATE_CAM_TWO:
                        print('camera 2 streaming')
                        self.CALIBERATE_CAM_TWO = True
                        num_ppl = len(numpy.asarray(msg_json['data']))
                        self.camera_two = Camera(num_ppl,self.cam_rate)
                    else:
                        print('Cam data')
                        self.process_cam_one_data(msg_json,self.camera_two)

                # Send a response to all connected client except the server
                #for conn in self.CONNECTIONS:
                    #if conn != websocket:
                        #await conn.send('success')
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
        #print('fsr', self.FSR.fsr_data)

    def process_emg_data(self, msg_json):
        #print('in func emg data')
        self.EMG.update_emg_data(msg_json['emg'],msg_json['time'])

    def process_force_mat_data(self,msg_json):
        #print('in force mat data')
        self.force_mat.update_force_mat_data(msg_json["data"], msg_json["time"])


    def process_speech_text_data(self,msg_json):
        #print('in speech 2 text')
        #print(msg_json['speech'],msg_json['text'],msg_json['time'])
        self.speechToText.update_speech_to_text_data(msg_json['speech'],msg_json['text'],msg_json['time'])

    def process_cam_one_data(self,msg_json,cam):

        data=msg_json
        self.frame_count+=1
        #decodedArrays = json.loads(data)
        #finalNumpyArray = numpy.asarray(decodedArrays["array"])
        cam.setup_people(data, msg_json['time'])


    async def send_dummy_data(self,websocket):
        print('in dummy data transfer')
        self.CONNECTIONS_port_two.add(websocket)
        while True:
            try:
                #print('going to send a message')
                #await websocket.send('hi')
                await websocket.send(json.loads(self.prep_data()))
                #print('sent')
            except websockets.exceptions.ConnectionClosedError as error1:
                print(f'Server Error: {error1}')
                self.CONNECTIONS_port_two.remove(websocket)
                #self.stop()

    #def connect_socket_two(self):
        #start_server = websockets.serve(self.send_dummy_data, "localhost", 7892)
        #asyncio.get_event_loop().run_until_complete(start_server)
        #asyncio.get_event_loop().run_forever()

    async def send_to_sockettwo(self):
        print('in send to socket two')
        async with websockets.serve(self.send_dummy_data,'', 7892,ping_interval=None,ping_timeout=None):
            await asyncio.Future()  # run forever

    def dummy_run(self):
        print('sending data to mobile app')
        asyncio.run(self.send_to_sockettwo())

    def collect_data(self):
        self.t.start()

    def get_last_n_data(self,data):
        if(len(data)<self.sensor_rate):
            return data
        else:
            #print('sending last 1000 data',len(data[-self.sensor_rate:]))
            return data[-self.sensor_rate:]


    def prep_data(self):
        print('sending data to mobile app')
        data_to_app = {
                        0: {"gsr":self.get_last_n_data(self.GSR.gsr_data),
                            "pulse":self.get_last_n_data(self.GSR.pulse),
                            "time": self.get_last_n_data(self.GSR.time)},
                        1: {"fsr":self.get_last_n_data(self.FSR.fsr_data),
                            "time":self.get_last_n_data(self.FSR.time)},
                        2: {"emg":self.get_last_n_data(self.EMG.all_channel_data),
                            1: self.get_last_n_data(self.EMG.channel_one),
                            2: self.get_last_n_data(self.EMG.channel_two),
                            3: self.get_last_n_data(self.EMG.channel_three),
                            4: self.get_last_n_data(self.EMG.channel_four),
                            5: self.get_last_n_data(self.EMG.channel_five),
                            6: self.get_last_n_data(self.EMG.channel_six),
                            7: self.get_last_n_data(self.EMG.channel_seven),
                            8: self.get_last_n_data(self.EMG.channel_eight),
                            9: self.get_last_n_data(self.EMG.channel_nine),
                            10: self.get_last_n_data(self.EMG.channel_ten),
                            11: self.get_last_n_data(self.EMG.channel_eleven),
                            12: self.get_last_n_data(self.EMG.channel_twelve),
                            13: self.get_last_n_data(self.EMG.channel_thirteen),
                            14: self.get_last_n_data(self.EMG.channel_fourteen),
                            15: self.get_last_n_data(self.EMG.channel_fifteen),
                            16: self.get_last_n_data(self.EMG.channel_sixteen),
                            "time":self.get_last_n_data(self.EMG.time)},

                        3: {
                            "data":self.get_last_n_data(self.force_mat.data),
                            "time":self.get_last_n_data(self.force_mat.time)
                        },

                        4: {"speech" : self.speechToText.speech,
                            "text": self.speechToText.text,
                            "time": self.speechToText.time },
                        5: {
                            "data" : self.camera_one.get_latest_data(),
                        },
                        6 : {
                            "data": self.camera_two.get_latest_data()
                        }

        }
        data_to_app = json.dumps(data_to_app)
        #print(data_to_app)
        #print(json.dumps(data_to_app))
        return json.dumps(data_to_app)



    def animate_plot(self,i):
        # Render plots as a matplotlib animation'
        self.axs.cla()
        #self.axs[1].cla()
        #self.axs[2].cla()

        self.axs.title.set_text('FSR data')
        #self.axs[1].title.set_text('GSR data')
        #self.axs[2].title.set_text('Pulse data')
        self.axs.plot(self.FSR.time[-self.sensor_rate:], self.FSR.fsr_data[-self.sensor_rate:])
        #self.axs[1].plot(self.GSR.time[-20:], self.GSR.gsr_data[-20:])
        #self.axs[2].plot(self.GSR.time[-20:], self.GSR.pulse[-20:])

        #self.axs[0].plot(self.get_last_n_data(self.FSR.time),self.get_last_n_data(self.FSR.fsr_data))
        #self.axs[1].plot(self.get_last_n_data(self.GSR.time),self.get_last_n_data(self.GSR.gsr_data))
        #self.axs[2].plot(self.get_last_n_data(GSR.time),self.get_last_n_data(self.GSR.pulse))
        # self.axs[0][3].plot(self.EMG.channel_one, self.EMG.time)
        # self.axs[0][4].plot(self.EMG.channel_two, self.EMG.time)
        # self.axs[1][0].plot(self.EMG.channel_three, self.EMG.time)
        # self.axs[1][1].plot(self.EMG.channel_four, self.EMG.time)
        # self.axs[1][2].plot(self.EMG.channel_five, self.EMG.time)
        # self.axs[1][3].plot(self.EMG.channel_six, self.EMG.time)
        # self.axs[1][4].plot(self.EMG.channel_seven, self.EMG.time)
        # self.axs[2][0].plot(self.EMG.channel_eight, self.EMG.time)
        # self.axs[2][1].plot(self.EMG.channel_nine, self.EMG.time)
        # self.axs[2][2].plot(self.EMG.channel_ten, self.EMG.time)
        # self.axs[2][3].plot(self.EMG.channel_eleven, self.EMG.time)
        # self.axs[2][4].plot(self.EMG.channel_twelve, self.EMG.time)
        # self.axs[3][0].plot(self.EMG.channel_thirteen, self.EMG.time)
        # self.axs[3][1].plot(self.EMG.channel_fourteen, self.EMG.time)
        # self.axs[3][2].plot(self.EMG.channel_fifteen, self.EMG.time)
        # self.axs[3][3].plot(self.EMG.channel_sixteen, self.EMG.time)
        # #self.axs[19].plot(self.EMG.channel_sixteen, self.EMG.time)

    def plot(self):
        anim = FuncAnimation(
            self.fig, self.animate_plot, interval=1000
        )
        plt.show()

if __name__ == "__main__":
    listener = MultiServer()
    listener.collect_data()
    #listener.prep_data()
    #S = threading.Timer(2.0, listener.prep_data())
    #S.start()
    #listener.plot()
    listener.dummy_run()



