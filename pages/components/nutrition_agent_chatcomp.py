'''
Title: 
Description:

'''

import os
import json
import requests
import logging
from typing import Optional

from openai import OpenAI
# import gradio as gr

from dotenv import load_dotenv
load_dotenv()

# Custom
from pages.components.utils import func_to_json

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

sys_msg = """The Assistant is specifically designed to assist with tasks related to health and nutrition. It provides valuable calculations related to health metrics such as Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) using recognized equations like Harris-Benedict and Mifflin-St Jeor. Additionally, it can fetch nutritional information of various food items using an external API.

Its capabilities allow it to engage in meaningful conversations and provide helpful responses related to health and nutrition. Based on the input it receives, the Assistant can calculate and provide critical health metric values, allowing users to better understand their energy expenditure and nutritional intake.

This Assistant is constantly evolving and improving its abilities to provide more accurate and informative responses. Its capabilities include understanding and processing large amounts of text, generating human-like responses, and providing detailed explanations about complex health metrics.

Whether you are looking to understand more about your daily energy expenditure, need help calculating your BMR, or want to fetch nutritional information about your meals, our Assistant is here to assist you. The ultimate goal is to support and contribute to a healthier lifestyle by making nutritional and metabolic information more accessible.
"""

class Agent:
    def __init__(self, 
        openai_api_key: str, 
        model_name: str = 'gpt-3.5-turbo', 
        functions: Optional[list] = None,
        verbose: bool = False):
        
        self.openai_client = OpenAI()
        self.openai_client.api_key = openai_api_key
        self.model_name = model_name
        self.functions = self._parse_functions(functions)       
        self.func_mapping = self._create_func_mapping(functions)
        self.chat_history = [{'role': 'system', 'content': sys_msg}]
        self.logger = logging.getLogger(__name__)
        self.verbose = verbose
        
    def _parse_functions(self, functions: Optional[list]) -> Optional[list]:
        if functions is None:
            return None
        return [func_to_json(func) for func in functions]
    
    def _create_func_mapping(self, functions: Optional[list]) -> dict:
        if functions is None:
            return None
        return {func.__name__: func for func in functions}
    
    def _create_chat_completion(self, 
                                messages: list,
                                use_functions: bool = True
        ) -> OpenAI().chat.completions:
        
        print("Creating chat...")
        if use_functions and self.functions:
            res = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.functions,
                tool_choice='auto'
            )

        else :
            res =self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
              
        print("Done creating chat...")
        print("Chat: ", res)
        return res
        
    def _generate_response(self) -> OpenAI().chat.completions:
        print("Generate response...")
        while True:
            res = self._create_chat_completion(self.chat_history + self.internal_thoughts)
            finish_reason = res.choices[0].finish_reason
            
            print("Finish reason...", finish_reason)
            if finish_reason == 'stop' or len(self.internal_thoughts) >= 3:
                print("Creating final answer...")
                final_thought = self._final_thought_answer()
                final_res = self._create_chat_completion(
                    self.chat_history + [final_thought],
                    use_functions=False
                )
                return final_res
            elif finish_reason == 'tool_calls':
                print("Use a tool...")
                self._handle_tool_calls(res)
            else:
                raise ValueError("Unexpected finish reason: {}".format(finish_reason))
                
    def _handle_tool_calls(self, res: OpenAI().chat.completions):
        """ Handle the function call response from OpenAI """
        print("Handling function call...")
        res_prev = res.choices[0].message.model_dump()
        # Remove function_call key from the previous response
        del res_prev['function_call']
        self.internal_thoughts.append(res_prev)
    
        func_name   = res.choices[0].message.tool_calls[0].function.name
        func_id     = res.choices[0].message.tool_calls[0].id
        args_str    = res.choices[0].message.tool_calls[0].function.arguments
        print("Call function: {}".format(func_name))
        result      = self._call_function(func_name, args_str)
        res_msg     = {'role': 'assistant', 'content': (f"The answer is {str(result)}.")}
        
        # Append tool call to chat history
        tool_message = {
            "tool_call_id": func_id,
            "role": "tool",
            "name": func_name,
            "content": (f"The answer is {str(result)}.")
        }
        self.internal_thoughts.append(tool_message)
        
        print("Result: {}".format(res_msg))
        self.internal_thoughts.append(res_msg)
        print("Done handling function call...")
             
    def _call_function(self, func_name: str, args_str: dict):
        """ Call the function specified by func_name with the arguments specified by args """
        args = json.loads(args_str)
        func = self.func_mapping[func_name]
        
        if self.verbose:
            self.logger.info("Calling function: {}".format(func_name))
            self.logger.info("Arguments: {}".format(args))
            self.logger.info(f"Function object: {func}")
        res = func(**args)
        return res
   
    def _final_thought_answer(self):
        """ Generate the final thought answer """
        thoughts = ("To answer the question I will use these step by step instructions.\n\n")
        for thought in self.internal_thoughts:
            print(thought)
            if 'tool_calls' in thought.keys():
                thoughts += (f"I will use the {thought['tool_calls'][0]['function']['name']} "
                             "function to calculate the answer with arguments "
                             + thought['tool_calls'][0]['function']['arguments'] + ".\n\n")
                
            else:
                thoughts += thought["content"] + "\n\n"
                
        self.final_thought = {
            'role'      : 'assistant',
            'content': (f"{thoughts} Based on the above, I will now answer the "
                        "question, this message will only be seen by me so answer with "
                        "the assumption with that the user has not seen this message.")
        }
        
        return self.final_thought

    def ask(self, query: str) -> OpenAI().chat.completions:
        self.internal_thoughts = []
        self.chat_history.append({'role': 'user', 'content': query})
        res = self._generate_response()
        res_history = res.choices[0].message.model_dump()
        del res_history["function_call"]
        del res_history["tool_calls"]
        self.chat_history.append(res_history)
        return res

class NutritionAgent:
    """
    NutritionBot combines OpenAI's GPT capabilities with ReAct's dynamic processing to understand dietary queries, suggest suitable alterantives, and deliver personalized advice. It does this while maintaining a conversational tone, making nutritional advice accessible and engaging
    
    NutritionBot has the ability to interface with an existing nturitional database. This allows FitBot to provide precise and update information to the users, ensuring the advice given is reliable and based on accurate data.
    """
    
    def __init__(self, openai_api_key: str, nut_api_key: str):
        self.openai_api_key = openai_api_key
        self.nut_api_key    = nut_api_key
        
        self.agent = Agent(
            openai_api_key=self.openai_api_key,
            functions=[
                self.get_nutritional_info,
                self.calculate_bmr,
                self.calculate_tdee,
                self.calculate_ibw,
                self.calculate_bmi,
                self.calculate_calories_to_lose_weight
            ]
        )    
        
    def get_nutritional_info(self, query: str) -> dict:
        """ Use Nutrition endpoint from API Ninjas to get nutritional information about various food items 
        
        :param query: The food item to get nutritional info for
        :return: A dictionary containing the nutritional information
        """
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
        response = requests.get(api_url, timeout=100, headers={'X-Api-Key': self.nut_api_key})
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code, "Message": response.text}
        
    def calculate_bmi(self, weight: float, height: float) -> float:
        """ Calculate the Body Mass Index (BMI) of a person.
        
        :param weight: The weight of the person in kilograms (kg)
        :param height: The height of the person in centimeters (cm)
        :return: The BMI of the person
        """
        
        height_meters = height / 100            # Convert height from cm to m
        bmi = weight / (height_meters ** 2)
        return round(bmi, 2)                    # Round to 2 decimal places
    
    def calculate_calories_to_lose_weight(self, desired_weight_loss_kg: float) -> float:
        """ Calculate the number of calories required to lose a certain amount of weight.
        
        :param desired_weight_loss_kg: The amount of weight the person wants to lose, in kilograms
        :return: The number of calories required to lose the amount of weight
        """
        
        calories_per_kg_fat = 7700              # Number of calories in 1 kg of fat
        return desired_weight_loss_kg * calories_per_kg_fat
    
    def calculate_bmr(self, 
                      weight: float, 
                      height: float, 
                      age: int,
                      gender: str,
                      equation: str = 'mifflin_st_jeor'
                      ) -> float:
        """ Calculate the Basal Metabolic Rate (BMR) of a person.
        
        :param weight:      The weight of the person in kilograms (kg)
        :param height:      The height of the person in centimeters (cm)
        :param age:         The age of the person in years
        :param gender:      The gender of the person ('male' or 'female')
        :param equation:    The equation to use for calculating BMR. Can be 'harris_benedict' or 'mifflin_st_jeor'
        :return:            The BMR of the person
        """
        
        if equation.lower() == 'mifflin_st_jeor':
            if gender.lower() == 'male':
                return (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:  # 'female'
                return (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:  # 'harris_benedict'
            if gender.lower() == 'male':
                return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:  # 'female'
                return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    def calculate_tdee(self,
                       bmr: float,
                       activity_level: str
                       ) -> float:
        
        """ Calculate the Total Daily Energy Expenditure (TDEE) of a person.
        
        :param bmr:             The Basal Metabolic Rate (BMR) of the person
        :param activity_level:  The activity level of the person. Can be 'sedentary', 'lightly_active', 'moderately_active', 'very_active', or 'super_active'
        
        :return:                The TDEE of the person
        """
        
        activity_factors = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'super_active': 1.9
        }
        
        return bmr * activity_factors[activity_level.lower()]
    
    def calculate_ibw(self,
                      height: float,
                      gender: str) -> float:
        """ Calculate the Ideal Body Weight (IBW) of a person.
        :param height:  The height of the person in inches
        :param gender:  The gender of the person ("male" or "female")
        :return:        The Ideal Body Weight in kg
        
        """
    
        if gender.lower() == 'male':
            if height <= 60:  # 5 feet = 60 inches
                return 50
            else:
                return 50 + 2.3 * (height - 60)
        elif gender.lower() == 'female':
            if height <= 60:
                return 45.5
            else:
                return 45.5 + 2.3 * (height - 60)
        else:
            raise ValueError("Invalid gender. Expected 'male' or 'female'.")
     
    def ask(self, question: str):
        response = self.agent.ask(question)
        response = response.choices[0].message.content
        return response

    def view_functions(self):
        return self.agent.functions

    def view_chat_history(self):
        return self.agent.chat_history

openai_api_key = os.getenv("OPENAI_API_KEY")
nut_api_key    = os.getenv("NINJA_API_KEY")

# fitness_agent = NutritionAgent(openai_api_key=openai_api_key, nut_api_key=nut_api_key)

# def get_response(message, history):
#     formatted_chat_history = [
#         {
#             'role': 'system',
#             'content': 'Assistant is a large language model trained by OpenAI.\n\nAssistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussion on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.\n\nAssistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.\n\nOverall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.\n'
#         }
#     ]

#     if history:
#         for i, chat in enumerate(history[0]):
#             formatted_chat_history.append({
#                 'role': 'user' if i % 2 == 0 else 'assistant',
#                 'content': chat
#             })
            
#         fitness_agent.chat_history = formatted_chat_history

#         print("Chat history: ")
#         logger.info(fitness_agent.chat_history)

#     # Get raw chat response
#     print("^" * 150)
#     print("Asking....")
#     res = fitness_agent.ask(message)

#     chat_response = res.choices[0].message.content
#     print("Chat response: ", chat_response)
#     print("Done asking... \n\n\n")
#     print("^" * 150)

#     return chat_response

def create_nutrition_agent_chatcomp():
    return  NutritionAgent(openai_api_key=openai_api_key, nut_api_key=nut_api_key)
        
# if __name__ == "__main__":
#     chat_interface = gr.ChatInterface(
#         fn=get_response,
#         title="Fitness Agent",
#         description="A simple chatbot using a Fitness Agent and Gradio with conversation history",
#     )

#     chat_interface.launch()
