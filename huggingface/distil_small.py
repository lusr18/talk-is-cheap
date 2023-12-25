'''
Title:          Speech to Text using Huggingface Distil-Whisper
Description:    Huggingface distil-whisper/distil-small.en for speech recognition
Website:        https://huggingface.co/distil-whisper/distil-small.en
'''

import os
import torch
import requests
from dotenv import load_dotenv
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from utils import get_torch_device

# os.environ['REQUESTS_CA_BUNDLE'] = '''
# os.environ['CURL_CA_BUNDLE'] = ''
# os.environ['HTTP_PROXY'] = "http://127.0.0.1:7890"
# os.environ['HTTPS_PROXY'] = "http://127.0.0.1:7890"
# os.environ['ALL_PROXY'] = "socks5://127.0.0.1:7890"

# Pretrained
def speech_to_text(audio_file):
    color = '\033[32m'
    # print(f"{color}Speech to Text")
    print("Speech to Text")
    device      = get_torch_device()
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    # model_id    = "distil-whisper/distil-small.en"
    # model_id    = "./models/distil-small.en"
    model_id = os.path.expanduser("/home/ftpuser/distil-small.en")
    model       = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, 
        torch_dtype=torch_dtype, 
        low_cpu_mem_usage=True, 
        use_safetensors=True
    )
    model.to(device)
    model.eval()
    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=64,
        torch_dtype=torch_dtype,
        device=device,
    )
    result = pipe(audio_file)
    return result["text"]


if __name__ == "__main__":
    speech_to_text("../temp/audio.wav")
