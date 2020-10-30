#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#!/usr/bin/python
# -*- coding: utf-8 -*-


"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient

from google.cloud import texttospeech
from pygame import mixer

import time

import requests
import os
import json

from flask import Flask, request, jsonify,redirect

#databse  mysql 
import pymysql.cursors

#Configure db 
conn = pymysql.connect(host='127.0.0.1',user='pi',password='1234',charset='utf8mb4')


client = texttospeech.TextToSpeechClient()


def get_answer(text, user_key):

    print("get_answer... start")
    data_send = { 
        'query': text,
        'sessionId': user_key,
        'lang': 'en',
    }
    data_header = {
        'Authorization': 'Bearer 4e7da793a9ce4a57b2cd113bd2a7ebf2',
        #'Authorization': 'Bearer 56b4c79017514fb6a27a45ce43bc21a3',  ## jjangphal
        'Content-Type': 'application/json; charset=utf-8'
    }
    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'
    data_receive = res.json()
    print (json.dumps(data_receive,indent=4))

    answer = data_receive['result']['fulfillment']['speech'] 
    parameters = data_receive['result']['parameters']

    if parameters :
       city = data_receive['result']['parameters']['local-city']
       print("local-city:" + city)
    


    return answer

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['POST', 'GET'])
def webhook():

    content = request.args.get('content')
    userid = request.args.get('userid')

    return get_answer(content, userid)





def tts_answer(answer):

    # Set the text input to be synthesize
    synthesis_input = texttospeech.types.SynthesisInput(text = answer)
    count = len(str(synthesis_input))/18   ### english 18
    print ("count" + str(count))


    voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
    # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

    #os.system("omxplayer -o alsa output.mp3")
    mixer.init()
    mixer.music.load('output.mp3')
    mixer.music.play(0)
    time.sleep(count)

    print ("SOUND GOOD~~")


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    language = 'en_US'
    print("start:" +language)
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    
    tts_answer("Now, Tell me please.")
   
    with Board() as board:
       
        while True:


            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)


            if text is None:
                tts_answer('Sorry, I did not hear you.')
                print('Sorry, I did not hear you.')

            else :        
                print("I: "+ text)

                if "good bye" in text or "bye" in text  or 'by' in text :

                    print("Thank you. Bye~")
                    tts_answer('Thank you. Goodbye.')
                    break

            # save db (I text)
                try:
                    with conn.cursor() as cursor:

                        sql = 'INSERT INTO aiy.chat(content) VALUES(%s)'
                        cursor.execute(sql,("I: "+text))
                        conn.commit()
                        print("save:{}".format(cursor.lastrowid))

                except:
                    print("DB1 에러")
          

            #### print answer
            
                answer = get_answer(text,'jp')
                print('Chatbot: "', answer, '"')
            

            #### save db (chatbot text)
                try:
                    with conn.cursor() as cursor:

                        sql = 'INSERT INTO aiy.chat(content) VALUES(%s)'
                        cursor.execute(sql,("Chatbot: "+answer))
                        conn.commit()

                except:
                    print("DB1 error")

                tts_answer(answer)


if __name__ == '__main__':
    main()
