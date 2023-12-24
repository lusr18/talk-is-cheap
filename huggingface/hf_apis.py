'''
Title:          Using Huggingface Inference APIs
'''

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# TODO Whisper Large API
def speech_to_text_api(audio_file):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(filename):
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()

    output = query("sample1.flac")
    return output
    

# Blip Image Captioning API
def image_to_caption(image_file):
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    def query(filename):
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()

    def blip_api(filename):
        output = query(filename)
        print(output)
        return query(filename)[0]["generated_text"]
    
    return blip_api(image_file)



