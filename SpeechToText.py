class SpeechToText:
    speech=[]
    text=[]
    time=[]

    def update_speech_to_text_data(self,speech,text,time):
        self.speech.append(speech)
        self.text.append(text)
        self.time.append(time)