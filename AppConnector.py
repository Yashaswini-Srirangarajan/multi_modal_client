import websockets
import asyncio
import websocket
import threading

class AppConnector:
    CONNECTIONS =set()

    SOCKET = "ws://0.0.0.0:7892/"
    #HOST = ""  # Empty denotes a localhost.
    #PORT = 7892

    def on_message(self,ws, message):
        print('in on message')
        print(message)
    def on_open(self,ws):
        print("Opened connection")
        ws.send("Message from Client !")
    def on_error(self,ws, error):
        print(error)

    def on_close(self,ws, close_status_code, close_msg):
        print("### closed ###")


    def wsthread(self):
        print('in ws thread')
        ws = websocket.WebSocketApp(self.SOCKET, on_message=self.on_message,on_close=self.on_close,on_open=self.on_open,on_error=self.on_error)
        print('socket connected')
        ws.run_forever()


if __name__ == '__main__':
    appConnector = AppConnector()
    appConnector.wsthread()