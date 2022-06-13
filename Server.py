import json
import threading
import websocket
import websockets
import asyncio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class MultiServer:

    #TODO configure arudino to send GSR and Pulse data separately
    #TODO put data in a list or dict
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

    fig, axs = plt.subplots(2)
    CONNECTIONS = set()

    async def handler(self,websocket):
        print('in handler')
        self.CONNECTIONS.add(websocket)

        count = 0
        while True:
            try:
                message = await websocket.recv()
                count+=1
                print(count)
                print(message)

                msg_json = json.loads(message)
                sensor_type = msg_json['sensor_type']

                if(sensor_type == 0):
                    self.process_pulse_data(msg_json)
                elif(sensor_type == 1):
                    self.process_fsr_data(msg_json)
                elif(sensor_type == 2):
                    self.process_emg_data(msg_json)
                elif (sensor_type == 3):
                    self.process_force_mat_data(msg_json)
                elif (sensor_type == 4):
                    self.process_speech_text_data(msg_json)
                elif (sensor_type == 5):
                    self.process_cam_one_data(msg_json)
                elif (sensor_type == 6):
                    self.process_cam_two_data(msg_json)

                # Send a response to all connected client except the server
                for conn in self.CONNECTIONS:
                    if conn != websocket:
                        await conn.send(message)
            except websockets.exceptions.ConnectionClosedError as error1:
                print(f'Server Error: {error1}')
                self.CONNECTIONS.remove(websocket)


    async def main(self):
        async with websockets.serve(self.handler, self.HOST, self.PORT):
            await asyncio.Future()  # run forever

    def run(self):
        asyncio.run(self.main())

    def process_pulse_data(self,msg_json):
        self.PULSE_DATA.append(msg_json['pulse'])
        self.PULSE_TIME.append(msg_json['time'])

    def process_fsr_data(self, msg_json):
        self.FSR_DATA.append(msg_json['Fsr'])
        self.FSR_TIME.append(msg_json['time'])

    def process_emg_data(self, msg_json):
        print('in func emg data')
        print(msg_json)
        #self.PULSE_DATA.append(msg_json['Fsr'])
        #self.PULSE_TIME.append(msg_json['time'])


    def collect_data(self):
        print('in collect data')
        t = threading.Thread(target=self.run)
        print('thread starting')
        t.start()

    def animate_plot(self,i):
        # Render plots as a matplotlib animation

        self.axs[0].plot(self.FSR_DATA)
        self.axs[1].plot(self.FSR_TIME)

    def plot(self):
        anim = FuncAnimation(
            self.fig, self.animate_plot, interval=1000
        )

        plt.show()

if __name__ == "__main__":
    listener = MultiServer()
    listener.collect_data()
    #listener.plot()



