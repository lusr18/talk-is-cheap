from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from dotenv import load_dotenv
import os
import requests

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model_id = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
model = AutoModelForCausalLM.from_pretrained(model_id, token=token)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=30)
hf = HuggingFacePipeline(pipeline=pipe)

from langchain.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | hf

question = "How many calories in eggs?"

print(chain.invoke({"question": question}))