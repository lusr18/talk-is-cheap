# talk-is-cheap
Multi-modal AI application for research based fitness and diet coaching. 

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


