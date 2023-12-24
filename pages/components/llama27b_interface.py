'''

Description: Code to interact with llama27b llm running on own server
'''

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

ip_address  = os.getenv("SERVER_HOST")
port        = os.getenv("SERVER_PORT")
username    = os.getenv("FUDAN_USERNAME")
password    = os.getenv("FUDAN_PASSWORD")

# print(f"Using proxy: {username}")
# print(f"Using proxy: {password}")


url = f'http://{ip_address}:{port}/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

# print(f"Using proxy: {username}")
# print(f"Using proxy: {password}")

proxies = {
    "http": f"{username}:{password}@libproxy.fudan.edu.cn:8080",
    "https":f"{username}:{password}@libproxy.fudan.edu.cn:8080",
}

workout_routine = "1. 10 pushups, 2.10 situps, 3.10 squats"
SYSTEM_PROMPT = f"You are a personal trainer and you are talking to a client. The workout routine for the client is: {workout_routine}. Stick to this plan unless asked by the client. You will tell the client what to do next based on the client's input. Be supportive! Start off by introducing the first exercise. When the user is done with all exercises, your final response should be 'finished'"

# Data to be sent in POST request
data = {
    'system_prompt': SYSTEM_PROMPT,
    'history' : [('Hey', "Great, let's get started on your workout routine! For the first exercise, we will do 10 pushups. Can you do pushups on the ground with your hands shoulder-width apart? Please do the pushups and let me know when you are done.")],
    'instruction': 'I finished. What should I do next?',
}

def format_streamlit_chat(chat):
    if len(chat) == 1: # First message
        return []
    
    formatted_chat = []
    for i in range(0, len(chat) - 1, 2):
        formatted_chat += [(chat[i]['content'], chat[i+1]['content'])]
        
    return formatted_chat
        
def send_llama27b_request(data, instruction, system_prompt):
    formatted_data = {}
    formatted_data["history"] = format_streamlit_chat(data)
    formatted_data["instruction"] = instruction
    formatted_data["system_prompt"] = system_prompt
    
    print(formatted_data)

    print(f"Sending request to the {url}")
    try:
        # Sending the POST request
        response = requests.post(url, data=formatted_data, proxies=proxies, headers=headers, timeout=10)
        
        # Printing the response
        print("Response from the server:")
        
        content = response.content.decode('utf-8')
        json_content = json.loads(content)
        
        print("Response:  ", json_content["response"])
        print("Time taken:", json_content["time_taken"])
        return json_content["response"], json_content["time_taken"]

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred", 0
        
# send_request(data)



