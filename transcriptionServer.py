from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

from waitress import serve

import json
import os

from WhisperTranscriber import AudioTranscriber
audioTranscriber = AudioTranscriber()

import time

user_settings_file = open("../../../User-Settings.json", encoding="utf-8")
user_settings_data = json.load(user_settings_file)

server_port = user_settings_data["Sugoi_Audio_Video_Translator"]["transcription_server_port_number"]

print("Server activated, waiting for request")

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods = ['POST'])
@cross_origin()

def Server():
    data = request.get_json()
    message = data.get("message")
    content = data.get("content")

    # print("this content", content)

    if (message == "get srt transcription"):
        start = time.time()

        base64audioInput = content
        transcriptionSRT = audioTranscriber.getTranscription(base64audioInput)

        end = time.time()
        print("total transcription time is", end - start)
        return json.dumps(transcriptionSRT)
    
    if (message == "start server"):
        print("####################")
        moduleName = content
        print(moduleName)
        print(os.path.abspath("."))
        os.system(f'cd .. && cd Modules && cd {moduleName} && start "{moduleName}" cmd /k Server.bat')
        return json.dumps("done")

    if (message == "close server"):
        moduleName = content
        os.system(f'taskkill /F /FI "WINDOWTITLE eq {moduleName} - Server.bat" /T')
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(moduleName)
        print("closing program")
        return json.dumps("done")
    
    if (message == "get current progress"):
        currentProgress = fileDownloader.currentPercentage
        return json.dumps(currentProgress)
    
    if (message == "test server"):
        return json.dumps("test succeeed")
    
    if (message == "unzip file"):
        fileUnzipper.unzipFile("test.zip")
        return json.dumps("file unzipping finished")
    
    if (message == "get unzipping progress"):
        currentProgress = fileUnzipper.currentPercentage
        return json.dumps(currentProgress)
    
    if (message == "send file path"):
        filePath = content
        return json.dumps(f"Hello {filePath}")




if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=15366)
    serve(app, host='0.0.0.0', port=server_port)