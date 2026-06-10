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

Con packages.yml se definen las dependencias de dbt
    packages:
    - package: dbt-labs/dbt_utils
        version: 1.1.1

dbt deps



Cuando se modifica sql y se añaden campos o lógica nueva
    dbt run --full-refresh




## Automatización en GitHub actions
Crear .github/workflows/dbt_run.yml

name: dbt pipeline

on:
  push:
    branches:
      - main

  schedule:
    - cron: "0 7 * * *"   # todos los días a las 07:00 UTC

  workflow_dispatch:      # botón manual

jobs:
  run-dbt:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dbt
        run: |
          pip install dbt-bigquery

      - name: Create credentials file
        env:
          BIGQUERY_KEY: ${{ secrets.BIGQUERY_KEY }}
        run: |
          echo "$BIGQUERY_KEY" > /tmp/keyfile.json

      - name: Run dbt pipeline
        env:
          GOOGLE_APPLICATION_CREDENTIALS: /tmp/keyfile.json
        run: |
          cd saas_dbt
          dbt deps
          dbt run
          dbt test


Configurar credenciales
    Ve a tu repo
    Settings → Secrets → Actions
    Create new secret

    
    {
    "type": "service_account",
    "project_id": "...",
    ...
    }


Se hace push al repo y directamente se ejecuta y se queda programado


on:
  push:
    branches:
      - main

  schedule:
    - cron: "0 7 * * *"

  workflow_dispatch:



on:
  pull_request:
    branches:
      - main

  workflow_dispatch:



Para hacer incrementales
{{ config(
    materialized='incremental',                         -> tipo incremental
    unique_key=['user_id','event_date','event_type'],   -> clave única para evitar duplicados
    partition_by={                                      -> mejora rendimiento
        "field": "event_date",
        "data_type": "date"
    },
    cluster_by=["user_id", "event_type"]                -> mejora filtros
) }}

{% if is_incremental() %}

WHERE event_date >= (
    SELECT DATE_SUB(MAX(event_date), INTERVAL 2 DAY)    -> reprocesa los últimos dos días por si entran datos retrasados
    FROM {{ this }}                                     -> hace referencia a la sql completa stg_events.sql
)

{% endif %}

Cuando se añade la unique_key al incremental DBT convierte el insert en un merge:
MERGE target_table t
USING new_data s
ON t.unique_key = s.unique_key

WHEN MATCHED THEN UPDATE
WHEN NOT MATCHED THEN INSERT

✔ si la fila existe → la actualiza
✔ si no existe → la inserta
