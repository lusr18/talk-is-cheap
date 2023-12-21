'''
Title:          Speech to Text using Huggingface Distil-Whisper
Description:    Huggingface distil-whisper/distil-small.en for speech recognition
Website:        https://huggingface.co/distil-whisper/distil-small.en
'''
import requests
import os
import torch
from dotenv import load_dotenv
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Pretrained
def speech_to_text(audio_file):
    device      = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id    = "distil-whisper/distil-small.en"
    model       = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
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

