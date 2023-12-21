# Langchain Notes


## SQLDatabaseChain


### Default Prompt
```python
PromptTemplate(input_variables=['input', 'table_info', 'top_k'], 
    template =  """

    You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question. \n

    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.\n

    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.\n

    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.\n
    Pay attention to use date(\'now\') function to get the current date, if the question involves "today".\n\n

    Use the following format:\n\n

    Question: Question here\n
    SQLQuery: SQL Query to run\n
    SQLResult: Result of the SQLQuery\n
    Answer: Final answer here\n\n

    Only use the following tables:\n
    {table_info}\n\n

    Question: {input}
"""
),
llm=OpenAI(client=<openai.resources.completions.Completions object at 0x7f945da8af90>, 
    async_client=<openai.resources.completions.AsyncCompletions object at 0x7f945daed790>, 
    temperature=0.0, 
    max_tokens=1000, 
    openai_api_key='<api_key>', 
    openai_proxy=''
)
```

Default prompt might not be enough, for example

1. recent workout -> get all entries of most recent date
2. Graph for me or show me a graph of my x exercise record. Make sure that in Numpy format for ability to graph.


## ChatOpenAI
Everytime you make converation...

```python
PromptTemplate(input_variables=['history', 'input'], 
    template='The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:'
    {'input': 'Nutrition tips.', 'history': '', 'response': "Sure! I'd be happy to provide you with some nutrition tips. What specific aspect of nutrition are you interested in? Are you looking for tips on healthy eating, weight management, or a specific diet?"}
    {'input': 'Weight management.', 'history': "Human: Nutrition tips.\nAI: Sure! I'd be happy to provide you with some nutrition tips. What specific aspect of nutrition are you interested in? Are you looking for tips on healthy eating, weight management, or a specific diet?", 'response': "Great! When it comes to weight management, there are a few key tips that can help. First, it's important to maintain a balanced diet that includes a variety of foods from different food groups. This ensures that you're getting all the necessary nutrients while also controlling your calorie intake.\n\nSecond, portion control is crucial for weight management. It's helpful to be mindful of your portion sizes and avoid eating oversized portions. One trick is to use smaller plates and bowls to help control the amount of food you consume.\n\nIn addition to portion control, it's important to eat at regular intervals throughout the day. This helps to keep your metabolism active and prevents overeating. It's also beneficial to include protein-rich foods in your meals and snacks, as they help to keep you feeling fuller for longer.\n\nAnother important aspect of weight management is staying hydrated. Drinking plenty of water helps to support your body's metabolism and can help control your appetite. It's generally recommended to drink at least 8 glasses of water per day.\n\nLastly, incorporating regular physical activity into your routine is key for weight management. Aim for at least 150 minutes of moderate-intensity aerobic exercise per week, along with strength training exercises at least twice a week.\n\nRemember, weight management is a long-term process, and it's important to make sustainable lifestyle changes rather than relying on quick fixes or fad diets. It's always a good idea to consult with a healthcare professional or registered dietitian for personalized advice based on your specific needs and goals."}
)
```