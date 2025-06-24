


instruction_text = """
**************************************
Go to Sugoi_Toolkit/Code/backendServer/Program-Backend/Sugoi-Audio-Video-Translator
You'll find "INPUT" "OUTPUT" folder
If this is your first time, look inside the default input folders and run the program with the default content
If it worked, great! 
Now you can put in your own content
Remember, everytime you run the output folder will be reset so remember to move all files out
After everything is done, remember to close all cmd windows
"""

print(instruction_text)
input("Press Enter to continue...")

import srt 
import shutil
import requests
import os
import base64
import json
from pathlib import Path
import sys 
import time

from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip

user_settings_file = open("../../../User-Settings.json", encoding="utf-8")
user_settings_data = json.load(user_settings_file)

current_translator = user_settings_data["Translation_API_Server"]["current_translator"]
translation_server_port_number = user_settings_data["Translation_API_Server"][current_translator]["HTTP_port_number"]

# translation_server_port_number = user_settings_data["Sugoi_Japanese_Translator"]["Offline"]["pythonFlaskServerPortNumber"]
transcription_server_port_number = user_settings_data["Sugoi_Audio_Video_Translator"]["transcription_server_port_number"]

class SubtitleProcessor:
    def __init__(self):
        self.progressStatus = ""
        self.listOfOriginalSubtitle = ""
        self.listOfTranslatedSubtitle = self.listOfOriginalSubtitle
        self.translationServerURL = f"http://localhost:{translation_server_port_number}/"
        self.transcriptionServerURL = f"http://localhost:{transcription_server_port_number}/"
        self.outputFolderName = 'OUTPUT'

    def readAndSaveSRTcontent(self, srtFilePath):
        fileContent = Path(srtFilePath).read_text(encoding="utf-8")
        self.listOfOriginalSubtitle = list(srt.parse(fileContent))
        self.listOfTranslatedSubtitle = self.listOfOriginalSubtitle

    def printListToTextFile(self, listToPrint, name):
        print(*listToPrint, sep='\n', file=open(name, "w", encoding="utf8"))
        return "print list to txt file"
    
    def getTrascriptionFromServer(self, audioFilePath):
        response = requests.post(self.transcriptionServerURL, json={
            "content": audioFilePath,
            "message": "get srt transcription"
        })
        return response.json()

    def printString(self):
        print("Hello World")

    def getListOfSubtitleText(self):
        listOfText = []
        for subtitle in self.listOfOriginalSubtitle:
            listOfText.append(subtitle.content)
        return listOfText

    def getTranslationFromServer(self, inputSentence):
        response = requests.post(self.translationServerURL, json={
            "content": inputSentence,
            "message": "translate sentences"
        })
        return response.json()

    def replaceSubtitleText(self, listOfNewSubtitleText):
        for index, subtitle in enumerate(self.listOfOriginalSubtitle):
            self.listOfTranslatedSubtitle[index].content = listOfNewSubtitleText[index]
        return self.listOfTranslatedSubtitle

    def convertListOfSubtitleToString(self, listOfSubtitles):
        subtitleString = srt.compose(listOfSubtitles)
        return subtitleString
    
    def convertListOfTranslatedSubtitleToString(self):
        result = self.convertListOfSubtitleToString(self.listOfTranslatedSubtitle)
        return result

    def translateListOfSubtitleText(self):
        listOfOriginalText = self.getListOfSubtitleText()
        listOfTranslationText = []
        for index, text in enumerate(listOfOriginalText):
            print(index+1, len(listOfOriginalText))
            translation = self.getTranslationFromServer(text)
            listOfTranslationText.append(translation)
        self.replaceSubtitleText(listOfTranslationText)
        translatedSubtitleString = self.convertListOfTranslatedSubtitleToString()
        # print(translatedSubtitleString)
        return translatedSubtitleString
    
    def printSubtitleStringToFile(self, subtitleString, outputFilePath):
        with open(outputFilePath, "w", encoding="utf-8") as text_file:
            print(subtitleString, file=text_file)

    def generateVideoFromImageAndAudio(self, outputFileName, audioFilePath, imageFilePath):
        audio_clip = AudioFileClip(audioFilePath)
        image_clip = ImageClip(imageFilePath)
        
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        
        video_clip.fps = 1
        video_clip.write_videofile(outputFileName)

    def embedSubtitleIntoVideo(self, ffmpegPath, videoFile, subtitleFile, outputPath):
        os.system(f'{ffmpegPath} -i {videoFile} -vf "subtitles={subtitleFile}" {outputPath} -y')

    def setProgressStatus(self, status):
        self.progressStatus = status
        print(self.progressStatus)

    def reset_output_folder(self):
        dirpath = Path(self.outputFolderName)
        if dirpath.exists() and dirpath.is_dir():
            print("folder existed")
            shutil.rmtree(dirpath)
            os.makedirs(self.outputFolderName)
        else:
            os.makedirs(self.outputFolderName)

    def extract_and_save_audio_file_from_video_file(self, input_video_path, output_audio_path):
        video = VideoFileClip(input_video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)

    def process(self, input_file_path, output_folder_path, file_type="audio"):
        # input_file_path = "INPUT/short_video_clip.mp4"
        file_type_extension = input_file_path[-3:]

        if (file_type_extension == "mp4"):
            file_type = "video"


        inputAudioFilePath = input_file_path

        if (file_type == "video"):
            self.setProgressStatus("Step 0.5: reset output folder")
            extracted_audio_path = f"{output_folder_path}/extracted_audio.mp3"
            self.extract_and_save_audio_file_from_video_file(input_file_path, extracted_audio_path)
            inputAudioFilePath = extracted_audio_path
            self.setProgressStatus("Step 0.5: Done")



        self.setProgressStatus("Step 1: transcribe audio file and save as srt")
        def convertFileToBase64string(fileName):
            fileInBytes = open(fileName, "rb")
            base64File = base64.b64encode(fileInBytes.read())
            result = str(base64File)
            return result

        listOfTranscription = self.getTrascriptionFromServer(convertFileToBase64string(inputAudioFilePath))
        self.printListToTextFile(listOfTranscription, f"{output_folder_path}/srtOutput.srt")
        self.setProgressStatus("Step 1: Done")

        if (user_settings_data["Sugoi_Audio_Video_Translator"]["only_transcribe"] == True):
            return "Done"
        else:
            self.setProgressStatus("Step 2: translate and save subtitle/srt file")
            self.readAndSaveSRTcontent(f"{output_folder_path}/srtOutput.srt")
            translatedSubtitleString = self.translateListOfSubtitleText()
            self.printSubtitleStringToFile(translatedSubtitleString, f"{output_folder_path}/translation.srt")
            self.setProgressStatus("Step 2: Done")

            if (user_settings_data["Sugoi_Audio_Video_Translator"]["only_transcribe_and_translate"] == True):
                return "Done"
            else:
                input_video_path = f"{output_folder_path}/videoOutput.mp4"

                if (file_type == "audio"):
                    self.setProgressStatus("Step 3: generate video from audio and image files")
                    self.generateVideoFromImageAndAudio(input_video_path, inputAudioFilePath, "japan.jpg")
                    self.setProgressStatus("Step 3: Done")
                else:
                    input_video_path = input_file_path


                self.setProgressStatus("Step 4: embed subtitle file into video")
                inputSubtitleFilePath = f"{output_folder_path}/translation.srt"
                outputVideoPath = f"{output_folder_path}/videoWithSub.mp4"
                self.embedSubtitleIntoVideo(ffmpegPath="ffmpeg.exe", videoFile=input_video_path, subtitleFile=inputSubtitleFilePath, outputPath=outputVideoPath)
                self.setProgressStatus("Step 4: Done")
    
    def getAllAbsoluteFilePathInFolder(self, directory):
        listOfImages = []
        for dirpath,_,filenames in os.walk(directory):
            for f in filenames:
                listOfImages.append(os.path.abspath(os.path.join(dirpath, f)))
        return listOfImages

    def batch_process(self):
        list_of_input_file_paths = self.getAllAbsoluteFilePathInFolder("INPUT")
        print(list_of_input_file_paths)

        self.setProgressStatus("Step 0: reset output folder")
        self.reset_output_folder()
        self.setProgressStatus("Step 0: Done")

        for index, input_file_path in enumerate(list_of_input_file_paths):
            output_folder = f"{self.outputFolderName}/{index}"
            os.makedirs(output_folder)
            self.process(input_file_path, output_folder)

        self.setProgressStatus("Step 5: all files are done")



# reset output folder (common)
# extract and save audio file from mp4 (video only)
# transcribe audio file and save as srt (common)
# translate and save subtitle/srt file (common)
# generate video from audio and image files (audio only)
# embed subtitle file into video (common)


#10 seconds
for i in range(10,0,-1):
    print(f"THE TRANSLATION PROGRAM WILL RUN AFTER {i} SECONDS")
    sys.stdout.write(str(i)+' ')
    sys.stdout.flush()
    time.sleep(1)


subtitleProcessor = SubtitleProcessor()
subtitleProcessor.batch_process()





