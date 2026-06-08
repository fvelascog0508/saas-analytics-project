#########################
## saas_analytics_project
#########################

git init

Cambiar de rama a main:
    git branch -m main


mkdir app pipelines models data sql notebooks
touch README.md requirements.txt .gitignore

Crear fichero para que existan y se puedan subir a git:
touch app/app.py
touch pipelines/generate_data.py
touch models/.gitkeep
touch sql/.gitkeep
touch notebooks/.gitkeep


nano .gitignore

# Python
__pycache__/
*.pyc
venv/

# Data
*.csv
*.parquet

# Environment
.env

# Logs
logs/

# OS
.DS_Store


python3 -m venv venv
source venv/bin/activate

git add .
git commit -m "initial project structure for saas analytics"


git remote add origin git@github.com:fvelascog0508/saas-analytics-project.git

https://github.com/new
saas-analytics-project

git push -u origin main


code .

  "python.defaultInterpreterPath": "venv/bin/python"    ????

#### DATA

pip install pandas numpy
pip freeze > requirements.txt

events.csv
python pipelines/ingest_csv.py


caso                uso 
un funnel global    .iloc[0]
funnel segmentado   .groupby().transform()

pip install matplotlib seaborn -> ver heatmap

pip install streamlit plotly -> pasar a streamlit


##GEMINI

pip install google-genai

https://aistudio.google.com/app/apikey
client = genai.Client(api_key="TU_API_KEY_CORRECTA")


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)



CAmbios en git -> subida a git
    git add .
    git commit -m "Comments"
    git push
