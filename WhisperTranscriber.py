from faster_whisper import WhisperModel
import math
import base64
import io
import json
# https://github.com/guillaumekln/faster-whisper/issues/80

user_settings_file = open("../../../User-Settings.json", encoding="utf-8")
user_settings_data = json.load(user_settings_file)

this_device = user_settings_data["Sugoi_Audio_Video_Translator"]["device"]
this_compute_type = user_settings_data["Sugoi_Audio_Video_Translator"]["compute_type"]
this_vad_filter = user_settings_data["Sugoi_Audio_Video_Translator"]["vad_filter"]
this_beam_size = user_settings_data["Sugoi_Audio_Video_Translator"]["beam_size"]
this_language = user_settings_data["Sugoi_Audio_Video_Translator"]["language"]

class AudioTranscriber:
    def __init__(self):
        self.model_path = "whisper_small/"
        # Run on GPU with FP16
        self.model = WhisperModel(self.model_path, device=this_device, compute_type=this_compute_type)
        # or run on GPU with INT8
        # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
        # or run on CPU with INT8
        #model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    def test(self):
        print("hello world")

    def convert_seconds_to_hms(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = math.floor((seconds % 1) * 1000)
        output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"
        return output

    def printListToTextFile(self, listToPrint, name):
        print(*listToPrint, sep='\n', file=open(name, "w", encoding="utf8"))
        return "print list to txt file"
    
    def getTranscription(self, base64audioFile):
        def decodeAndSaveBase64Bytes(audioBytes):
            audioFile = bytearray(audioBytes, encoding="utf-8")
            del audioFile[-1]
            del audioFile[0]
            del audioFile[0]
            audioFile_decoded = base64.b64decode(audioFile)
            return audioFile_decoded

        base64ToBinaryFile = decodeAndSaveBase64Bytes(base64audioFile)

        audioSegments, audioInfo = self.model.transcribe(io.BytesIO(base64ToBinaryFile), vad_filter=this_vad_filter, beam_size=this_beam_size, language=this_language)
        print("Detected language '%s' with probability %f" % (audioInfo.language, audioInfo.language_probability))

        listOfAudioSegments = []

        count = 0
        totalDurationInSeconds = round(audioInfo.duration)

        for segment in audioSegments:
            count +=1
            duration = f"{self.convert_seconds_to_hms(segment.start)} --> {self.convert_seconds_to_hms(segment.end)}\n"
            print(round(round(segment.end)/totalDurationInSeconds*100))
            text = f"{segment.text.lstrip()}\n"
            
            listOfAudioSegments.append(f"{count}\n{duration}{text}")  # Write formatted string to the file
            print(f"{duration}{text}",end='')

        return listOfAudioSegments
    
    def convertOutputToSRT(self):
        listOfAudioSegments = self.getTranscription()
        self.printListToTextFile(listOfAudioSegments, "BinaryOutput.srt")


# audioTranscriber = AudioTranscriber()

# def convertFileToBase64string(fileName):
#     fileInBytes = open(fileName, "rb")
#     base64File = base64.b64encode(fileInBytes.read())
#     result = str(base64File)
#     return result

# base64Input = convertFileToBase64string("original.mp3")

# audioTranscriber.getTranscription()
