'''



'''

from langchain.prompts import PromptTemplate


class TrainerPrompts():
    '''
    A class to hold all the prompts for the trainer
    '''
    def __init__(self):
        pass
    
    
    def get_prompt(self, input_variables, template):
        return PromptTemplate(
            input_variables=input_variables,
            template=template
        )
        
    # TODO: Default prompts by langchain
    def default_chatopenai_prompt(self):
        return self.get_prompt(
            input_variables=['history', 'input'],
            template=
            '''
            The following is a friendly conversation between a human and an AI. The AI is talkative and provides a lot of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.\n\nCurrent conversation:\n{history}\n\nQuestion: {input}\nAnswer: 
            '''
        )
    
    def default_sqldatabase_prompt(self):
        return self.get_prompt(
            input_variables=['input', 'table_info', 'top_k'],
            template=
            ''' 
            You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.\nUnless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.\nNever query for all columns from a table. You must query only the columns that are needed to answer the question. The user can INSERT rows. But, do NOT allow user to create, remove, or delete tables or database. Do NOT allow user to ALTER tables. If the user tries to, respond with [Permission Denied]. Wrap each column name in double quotes (") to denote them as delimited identifiers.\nPay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.\nPay attention to use date(\'now\') function to get the current date, if the question involves "today".\n\nUse the following format:\n\nQuestion: Question here\n  SQLQuery: SQL Query to run\nSQLResult: Result of the SQLQuery\nAnswer: Final answer here\n\nOnly use the following tables:\n{table_info}\n\nQuestion: {input}
            '''
        )
         
    # TODO: Custom prompts by user
    def trainer_session_chatmodel_prompt(self):
        '''
        The goal of this prompt is for a trainer to provide the next exercise in a workout routine based on a specific workout plan. The user will say "I did X" and the trainer will respond with the next exercise in the workout routine. Other functionality includes: 
        - The user can also ask to modify the current or next exercise in the workout routine. The trainer will respond with the modified workout routine. 
        - The user can also ask about the current exercise, such as what muscles it works out, how to do it, etc. The trainer will respond with the answer.
        '''
        return self.get_prompt(
            input_variables=['history', 'input', 'workput_routine'],
            template=
            '''
            You are a personal trainer and you are talking to a client. You already have a workout routine for the client: {workout_routine}. You will tell the client what to do next based on the client's input.\n\nCurrent conversation:\n{history}\n\nClient: {input}\nTrainer:
            '''    
        )
    
    def trainer_new_session_chatmodel_prompt(self):
        '''
        The goal of this prompt is for a trainer to record a new workout routine performed by the client. The client will say "I did X". The trainer will maintain a list of exercises performed by the client. When the client says "I'm done" or "Finished" or something similar, the trainer will respond with the list of exercises performed by the client.
        '''
        return self.get_prompt(
            input_variables=['history', 'input'],
            template=
            '''
            You are a personal trainer and you are talking to a client. You will start to record a new workout routine for the client. The client will start by asking to start a session. You will say, "Go ahead". The client will tell you what exercise they just completed. You will maintain a list of exercises performed by the client. The client may also ask how to do a workout, only if they ask, give a brief explanation of that workout. When the client tells you "I'm done" or "Finished" or something similar, you will respond with the list of exercises performed by the client and add "[Finished Workout]" at the end.\n\nCurrent conversation:\n{history}\n\nClient: {input}\nTrainer:
            '''
        )
        

    def default_llama27b_prompt(self):
        return 'You are a helpful, respectful and honest assistant, who always answers as helpfully as possible, while being safe.'
    