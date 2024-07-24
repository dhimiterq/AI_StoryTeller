from piper.voice import PiperVoice as piper #Backbone of text to speech
import wave #Writing text to speech to wave files
from sys import platform
from os import remove
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #Stop pygame from saying hello in the console

from pygame import mixer

mixer.init()

model = None #Set the model to none at the start
voice = None #Set the voice to none at the start

#Function to load and set the voice model to be used
def load(model_set):
    global model
    global voice
    
    if '.onnx' in model_set: #Is the extension .onnx in the filename, if not add it below.
        model = model_set #Set model variable as is.
    else:
        model = model_set + '.onnx' #Set model variable and append .onnx.
    
    #Try to load the model
    try:
        voice = piper.load(model) #Load the model
    except:
        print("Something went wrong, did you type the correct name for the model?")
        exit()

#Function to save a text to speech file to disk
def save(text, file_name, model_set=model):
    global model
    global voice
    
    if model_set == None and model == None: #Check if a model has been set, if not then exit.
        print("No model was set! Please set a model using the load function: load(\"your_model_here\")")
        exit()
    elif model_set != None: #Is there a voice that should be used only once?
        temp_voice = piper.load(model_set)
        with wave.open(file_name, "wb") as wav_file:
            temp_voice.synthesize(text, wav_file)
    else: #If not, use the voice that was set eariler.
        with wave.open(file_name, "wb") as wav_file:
            voice.synthesize(text, wav_file)

#Function to save the file to disk, play it on the speakers, then delete the file.
def say(text, model_set=model):
    global model
    global voice
    
    if model_set == None and model == None: #Check if a model has been set, if not then exit.
        print("No model was set! Please set a model using the load function:  load(\"your_model_here\")")
        exit()
    elif model_set != None: #Is there a voice that should only be used once?
        temp_voice = piper.load(model_set)
        with wave.open('tmp_piper_text_2_speech.wav', "wb") as wav_file:
            temp_voice.synthesize(text, wav_file)
    else: #If not, use the voice that was set earlier.
        with wave.open('tmp_piper_text_2_speech.wav', "wb") as wav_file:
            voice.synthesize(text, wav_file)
    
    #Play the file
    mixer.music.load('tmp_piper_text_2_speech.wav')
    mixer.music.set_volume(1)
    mixer.music.play()

    while mixer.music.get_busy():
        pass
    
    remove("tmp_piper_text_2_speech.wav") #Remove the temporary file
