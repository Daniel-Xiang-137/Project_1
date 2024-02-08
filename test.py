from google.cloud import bigquery as bq
from google.oauth2 import service_account as sa

credentials = sa.Credentials.from_service_account_file("engaged-tape-412316-0c6a1760feec.json")
project_id = "engaged-tape-412316"
client = bq.Client(credentials=credentials, project=project_id)
rows = client.query("""
                           SELECT *
                           FROM Energy_Data.Energy_Data;""")
for r in rows:
    print(r)