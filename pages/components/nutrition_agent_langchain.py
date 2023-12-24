'''



'''

import os
import sys
import requests
import json
from typing import Optional, List, Sequence, Dict, Any
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
open_api_key = os.getenv("OPENAI_API_KEY")

from langchain.agents import create_sql_agent, initialize_agent
from langchain.agents.agent import AgentExecutor, BaseSingleActionAgent
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS


from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.llms.openai import OpenAI
from langchain.utilities.sql_database import SQLDatabase
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.chains import LLMMathChain
from langchain.chains.llm import LLMChain
from langchain_experimental.sql import SQLDatabaseChain
from langchain.memory import ConversationBufferMemory

from langchain_core.language_models import BaseLanguageModel
from langchain_core.memory import BaseMemory
from langchain_core.pydantic_v1 import Field

# Custom
from trainer_prompts import TrainerPrompts



# # Database
# db = SQLDatabase.from_uri("sqlite:///personal.sqlite3")
# toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# agent_executer = create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
# )

# with get_openai_callback() as cb:
#     agent_executer.run("Describe the food table")
    
# print(cb)

NUTRITION_PREFIX = """You are an agent designed to be a helpful personal nutritionist. Agent has access to the following tools {tools}. Don't use more tools than you need to answer the question. 

Agent should use the database tool to answer questions related to the database. Agent should use the Ninja API tool to answer questions related to nutrition. Agent should use the BMI tool to answer questions related to BMI.

If none of the tools are needed.

If the question does not seem related to nutrition, just return "I don't know" as the answer.
"""
NUTRITION_SUFFIX = """Begin!

{chat_history}
Question: {input}
Thought: I should think about what tools I need to use to answer this question.  Then I should use the tools to answer the question.
{agent_scratchpad}"""

def create_nutrition_agent(
    llm: BaseLanguageModel,
    memory: BaseMemory,
    toolkit: BaseToolkit,
    agent_type: AgentType = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = NUTRITION_PREFIX, # Prompt prefix for the agent
    suffix: Optional[str] = None, # Prompt suffix for the agent
    format_instructions: str = FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10, # Top k results to return from sql database
    max_iterations: Optional[int] = 3,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    verbose: bool = False,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    extra_tools: Sequence[BaseTool] = (),
    **kwargs: Any
) -> AgentExecutor:
    """ Construct a nutrition agent from an LLM and tools. """
    
    tools =  toolkit.get_tools() + list(extra_tools)
    # prefix = prefix.format(dialect=toolkit.dialect, top_k=top_k)
    prefix = prefix.format(tools=", ".join([tool.name for tool in tools]))
    agent: BaseSingleActionAgent
    
    if agent_type == AgentType.ZERO_SHOT_REACT_DESCRIPTION:
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix or NUTRITION_SUFFIX,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
        
    else:
        raise ValueError("Agent type {} not supported".format(agent_type))
    
    return AgentExecutor(
        agent=agent,
        memory=memory,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        **(agent_executor_kwargs or {}),
    )


'''
Tools
'''
class NutritionBaseTool(BaseTool):
    """ Base tool for interacting with nutrition data. """
    
    nut_api_key: str = None
 
    class Config(BaseTool.Config):
        pass

class NinjaAPINutritionTool(NutritionBaseTool, BaseTool):
    """ Tool for interacting with the Ninja API to get nutrition data. """
    
    name: str = "nutrition_ninja_api"
    description: str = """
    Input is the name of the food item. Use this tool to get nutrient information about a food item. Return only nutrition data for calories, carbohydrates, fat, protein, sodium and sugar.
    """
    
    def _run(self, query, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
        response = requests.get(api_url, timeout=100, headers={'X-Api-Key': self.nut_api_key})
                
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code, "Message": response.text}
        
        
class CalculateBMITool(BaseTool):
    """ Tool for calculating BMI. """
    
    name: str = "calculate_bmi"
    description: str = """
    Only use this tool for calculating body max index of a person. Input to this tool is a json object of height in centimeters and weight in kilograms. The tool will then calculate the BMI.
    """
    
    def _run(self, query, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        query = json.loads(query)
        height = query["height"]
        weight = query["weight"]
        height_meters = height / 100            # Convert height from cm to m
        bmi = weight / (height_meters ** 2)
        return round(bmi, 2)                    # Round to 2 decimal places

class NutritionSQLDatabaseTool(BaseTool):
    llm: BaseLanguageModel
    db: SQLDatabase
    name: str = "nutrition_sql_db"
    description: str = """
    Input to this tool is a query to a database. The tool will then use the SQL database to get the data. Only use this tools for questions that want to access the database. The query is simply the question you want to ask the database, don't change the query.
    """
    
    def _run(self, query, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=TrainerPrompts().default_sqldatabase_prompt(),
        )
        db_chain = SQLDatabaseChain(
            llm_chain=llm_chain,
            database=self.db,
        )
        response = db_chain.run(query)
        return response
    
'''
Toolkit
'''
class NutritionsToolkit(BaseToolkit):
    """ Toolkit for interacting with nutrition data. """
    
    # db: SQLDatabase = Field(exclude=True)
    nut_api_key: str = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)
    db: SQLDatabase = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_tools(self) -> List[BaseTool]:
        """ Get the tools in the toolkit. """
        
        ninja_api_nutrition_tool = NinjaAPINutritionTool(nut_api_key=self.nut_api_key)
        calculate_bmi_tool = CalculateBMITool()
        nutrition_sql_db_tool = NutritionSQLDatabaseTool(llm=self.llm, db=self.db)
    
        return [
            ninja_api_nutrition_tool,
            calculate_bmi_tool,
            nutrition_sql_db_tool 
        ]
        
if __name__ == "__main__":
    llm     = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=1000)
    db      = SQLDatabase.from_uri("sqlite:///database/personal_db.sqlite3")
    memory  = ConversationBufferMemory(memory_key="chat_history")
    
    toolkit = NutritionsToolkit(
        nut_api_key=os.getenv("NINJA_API_KEY"),
        llm=llm,
        db=db
    )
    agent_executer = create_nutrition_agent(
        llm=llm,
        memory=memory,
        toolkit=toolkit,
        verbose=True,
        input_variables=["input", "chat_history", "agent_scratchpad"],
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
    
    with get_openai_callback() as cb:
        agent_executer.run("Give me a list of every food in the database")
        
    print(cb)
    
    # print("Memory: ", memory)
    
    # with get_openai_callback() as cb:
    #     agent_executer.run("How many calories?")
        
    # print(cb)
    
    # print("Memory: ", memory)
    
    # with get_openai_callback() as cb:
    #     agent_executer.run("What did I just ask?")