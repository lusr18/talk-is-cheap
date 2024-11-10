# talk-is-cheap
Multi-modal AI personal health coach for research paper based fitness and diet coaching. 
Frontend made with streamlit, supports text and speech input，backend made with Django.（
AI using Langchain and Huggingface, creating a vector database on research based knowledge for embeddings. 
Agent functions allow for AI personal coach to access user SQL data to make tailored advice. 

## environment
1. create a `.env` file and create the following 
```
OPENAI_API_KEY=<OPENAI_API_KEY>
HUGGINGFACEHUB_API_TOKEN=<HUGGINGFACEHUB_API_TOKEN>
```

2. conda environment
```bash
conda env create -f linux_environment.yml
```

## running
1. Create local databases
```bash
# Create personal db
cd database
python create_db_script.py --sql_script create_personal_db.sql --database_path personal_db.sqlite3

# Create nutrients database
python create_db_script.py --sql_script create_nutrition_db.sql --database_path nutrition_db.sqlite3
```

2. Run app.py with streamlit
```bash
streamlit run app.py
```

## demo
![image](https://github.com/lusr18/talk-is-cheap/blob/main/assets/demo1.jpg)
![image](https://github.com/lusr18/talk-is-cheap/blob/main/assets/demo2.jpg)
![image](https://github.com/lusr18/talk-is-cheap/blob/main/assets/demo3.jpg)
![image](https://github.com/lusr18/talk-is-cheap/blob/main/assets/demo4.jpg)



