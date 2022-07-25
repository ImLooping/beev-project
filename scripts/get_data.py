import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
import datetime as dt
from google.oauth2 import service_account
from datetime import datetime, timedelta
import requests
import json
import time


key_path = 'scripts/beev-analytics-f28819d84e56.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
bqclient = bigquery.Client(credentials=credentials, project='beev-analytics')
brands = ['audi', 'hyundai', 'mini', 'renault', 'dacia', 'bmw', 'jaguar', 'nissan',
          'citroen', 'seat', 'mg', 'ds', 'kia', 'opel', 'skoda', 'tesla', 'aiways', 
          'ford', 'mazda', 'peugeot', 'smart', 'fiat', 'toyota', 'honda', 'mercedes', 
          'porsche', 'volkswagen', 'polestar']
url = 'https://app.beev.co/api/1.1/obj/vehicule'
vh = requests.get(url)
vh = json.loads(vh.text)
def get_brands(x):
    for i in brands:
        if i in x or i in x.lower() or i in x.upper() or i in x.title() or i in x.capitalize():
            return i.capitalize()
        else:
            pass
brands_models = {i["Model"]: [i['Model'].rstrip().lstrip().lower().replace(' ', '-'), 
                              i['Model'].rstrip().lstrip().lower().replace(' ', '')] 
                 for i in vh['response']['results']}
def get_model(x):
    for i, j in brands_models.items():
        if j[0] in x or j[0] in x.lower() or j[0] in x.upper() or j[0] in x.title() or j[0] in x.capitalize():
            return i
        elif j[1] in x or j[1] in x.lower() or j[1] in x.upper() or j[1] in x.title() or j[1] in x.capitalize():
            return i
        else:
            pass

def global_query(start, end):
    bqclient = bigquery.Client(credentials=credentials, project='beev-analytics')
    query_string = f"""
        WITH
            tables as (
                SELECT
                user_pseudo_id as client_id,
                event_timestamp as timestamp,
                event_name as event_name,
                device.category as device,
                device.language as language,
                device.web_info.browser as browser,
                device.web_info.hostname as hostname,
                geo.country as country,
                geo.city as city,
                (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
                (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location')
                    AS url,
                (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_title') AS page_title,
                (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'source') AS source, 
                LEAD
                    (event_timestamp) OVER (PARTITION BY (SELECT value.int_value FROM UNNEST(event_params)
                    WHERE key = 'ga_session_id')
                    ORDER BY event_timestamp ASC) AS next_hit_in_the_same_session
                FROM
                    `beev-analytics.analytics_314142962.events_*`
                WHERE event_date BETWEEN '{start}' AND '{end}'
                        AND event_name IN ('page_view', 'onboarding_lead_cs', 'onboarding_lead_ev')
            )

        SELECT 
            EXTRACT(DATE FROM TIMESTAMP_SECONDS(CAST(timestamp/1000000 AS INT))) AS date,
            *,
            round((next_hit_in_the_same_session - timestamp)/1000000, 0) AS time_on_page_in_seconds
        FROM tables
        ORDER BY timestamp ASC;
        """
    return (bqclient.query(query_string).result().to_dataframe(create_bqstorage_client=True))

def run(start, end):
    # Change start format   
    start = datetime.strftime(start, '%Y%m%d')
    # Call global query
    df = global_query(start, end)
    # Create new columns 
    tmp_total = df.groupby(['client_id', 'ga_session_id']).sum().reset_index()[['client_id', 'ga_session_id', 'time_on_page_in_seconds']].rename(columns={'time_on_page_in_seconds': 'total_time'})
    tmp_max = df.groupby(['client_id', 'ga_session_id'])['timestamp'].max().reset_index()[['client_id', 'ga_session_id', 'timestamp']].rename(columns={'timestamp': 'max_time'})
    tmp_min = df.groupby(['client_id', 'ga_session_id'])['timestamp'].min().reset_index()[['client_id', 'ga_session_id', 'timestamp']].rename(columns={'timestamp': 'min_time'})
    def get_source(x):
        for i in x:
            if i != 'None':
                return i
            else:
                return 'No Source'
    tmp_source = df.groupby(['client_id', 'ga_session_id'])['source'].unique().reset_index()[['client_id', 'ga_session_id', 'source']].rename(columns={'source': 'all_source'})
    tmp_source['all_source'] = tmp_source['all_source'].apply(get_source).drop(columns={'source'})
    df = pd.merge(df, tmp_total, on=['client_id', 'ga_session_id'], how='left')\
            .merge(tmp_max, on=['client_id', 'ga_session_id'], how='left')\
            .merge(tmp_min, on=['client_id', 'ga_session_id'], how='left')\
            .merge(tmp_source, on=['client_id', 'ga_session_id'], how='left')
    df['brand'] = df['url'].apply(get_brands)
    df['models'] = df['url'].apply(get_model)
    # Save CSV
    df.to_csv('data/data.csv')
