from app.models import GlobalQuery, Daily
import csv
import pandas as pd
import numpy as np
import re
from datetime import datetime

def run():
    """
    Save all data from data.csv to GlobalQuery model
    Next step is to save this data to a table for daily reports
    """
    with open('data/data.csv') as file:
        list_global_query = GlobalQuery.objects.all()
        df = pd.DataFrame(list(list_global_query))
        
        # check data in Daily table
        max_date = Daily.objects.all().aggregate(Max('date'))['date__max']
        if max_date is None:
            for row in df.itertuples():
                Daily.objects.create(
                    date = row.date,
                    nb_client = df.groupby(['date'])['client_id'].count().to_list(),
                    nb_page = df.groupby(['date'])['url'].count().to_list(),
                    brands = row.brand,
                    modeles = row.model,
                    total_time_on_page = row.time_on_page,
                    total_cs = row.cs,
                    total_ev = row.ev,
                    wc_brands = row.wc_brand,
                    wc_models = row.wc_model,
                )
        
        for row in reader:
            print(row)
            
            rows = GlobalQuery(

                date = row[1],
                client_id = row[2],
                timestamp = row[3],
                event_name = row[4],
                device = row[5],
                language = row[6],
                browser = row[7],
                hostname = row[8],
                country = row[9],
                city = row[10],
                ga_session_id = row[11],
                url = row[12],
                # Remove all emoji from the page_title
                page_title = emoji_pattern.sub(r'', row[13]),
                #
                # source = row[14],
                # next_hit_in_the_same_session = row[15],
                time_on_page_in_seconds = row[16],
                total_time = row[17],
                maxi = datetime.fromtimestamp(int(row[18])/1000000).strftime('%Y-%m-%d %H:%M:%S'),
                mini = datetime.fromtimestamp(int(row[19])/1000000).strftime('%Y-%m-%d %H:%M:%S'),
                all_source = row[20]
            )
            
            rows.save()
