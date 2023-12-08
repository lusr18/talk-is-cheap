# talk-is-cheap
Multi-modal AI application for research based fitness and diet coaching. 


## environment
1. create a `.env` file and create the following 
```
OPENAI_API_KEY=<OPENAI_API_KEY>
HUGGINGFACEHUB_API_TOKEN=<HUGGINGFACEHUB_API_TOKEN>
```

2. conda environment
```
conda env create -f environment.yml
```

## running
1. Create local databases
```
cd tools
python create_db_script.py --sql_script create_workout_db.sql --database_path personal.sqlite3
```

2. Run app.py with streamlit
```
streamlit run app.py
```


