# import requests
# from PIL import Image
# from transformers import BlipProcessor, BlipForConditionalGeneration

# processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
# model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# img_url = '../temp/shutterstock_99954842.jpg' 
# raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

# # conditional image captioning
# text = "a photography of"
# inputs = processor(raw_image, text, return_tensors="pt")

# out = model.generate(**inputs)
# print(processor.decode(out[0], skip_special_tokens=True))

# # unconditional image captioning
# inputs = processor(raw_image, return_tensors="pt")

# out = model.generate(**inputs)
# print(processor.decode(out[0], skip_special_tokens=True))

from dotenv import load_dotenv
import os
import requests

load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# https://huggingface.co/Salesforce/blip-image-captioning-large
def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

def blip_api(filename):
    output = query(filename)
    print(output)
    return query(filename)[0]["generated_text"]

