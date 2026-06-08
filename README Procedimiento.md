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



Cambios en git -> subida a git
    git add .
    git commit -m "Comments"
    git push


################ DBT LOCAL
pip install dbt-duckdb
dbt --version

Crear proyecto DBT:ç
    dbt init saas_dbt

Editar ~/.dbt/profiles.yml
    saas_dbt:
        target: dev
        outputs:
            dev:
            type: duckdb
            path: /mnt/c/Users/.../saas_analytics_project/saas.duckdb

Para que no entre en requeriments.txt
    pip uninstall dbt-duckdb

################ DBT BIGQUERY
pip install dbt-bigquery

code ~/.dbt/profiles.yml -> para abrir el fichero y editarlo

Hay que poner la ruta correcta en el json para que se puede conectar
    keys/xxxxx.json -> el json con la cuenta de servicio de bq

Comprobación conexión:
    cd saas_dbt
    dbt debug

Crear dataset y configurarlo en el profiles.yml
    project: project-ecommerce-497614
    dataset: saas_analytics

Cargar datos a BQ:
    python pipelines/load_bq.py

AHora crear sources.yml en models para configurar origen datos RAW
    version: 2

    sources:
    - name: raw
        database: project-ecommerce-497614
        schema: saas_analytics
        tables:
        - name: events_raw

Modelo staging
    stg_events.sql

dbt run desde saas_dbt

Asegurarse que el proyecto tenga permisos en IAM:
    BigQuery Data Editor
    BigQuery Data Viewer
    BigQuery Job User

lanzar modelos y comprobar en bq

Cambiar en app.py para que apunte a bq tambien cambiar la referencia a los secrets de strealit
Añadir a secrets de strealit las keys en formato TOML
Subir a git para sincronizar strealit


Para generar doc dbt
    dbt docs generate
    dbt docs serve


Particionado y cluster en stg:
    {{ config(
        materialized='table',
        partition_by={
            "field": "event_date",
            "data_type": "date"
        },
        cluster_by=["user_id", "event_type"]
    ) }}

luego dbt run --full-refresh


Con control de queries en secrets de streamlit
    DEBUG_MODE = true


## TEST DBT
Crear stg_events.yml donde se definen los criterios de test
version: 2

models:
  - name: stg_events
    description: "Cleaned events data"

    columns:
      - name: user_id
        description: "User identifier"
        tests:
          - not_null

      - name: event_date
        description: "Event date"
        tests:
          - not_null

      - name: event_type
        description: "Event type"
        tests:
          - not_null
          - accepted_values:
              arguments:
                values: ['signup', 'create_project', 'other']


luego dbt test

En dbt_project.yml -> definir estructura de models
    models:
        saas_dbt:
            # Config indicated by + and applies to all files under models/example/

            staging:
            +materialized: table

            marts:
            +materialized: table
