from app.models import GlobalQuery
import csv
import pandas as pd
import numpy as np
import re
from datetime import datetime
from django.db.models import Max

def run(start):
    """
    Save all data from data.csv to GlobalQuery model
    Next step is to save this data to a table for daily reports
    """
    with open('data/data.csv') as file:
        reader = csv.reader(file)
        next(reader)

        # Delete the last date from the database
        if start != '2022-06-01':
            # Format start date to YYYY-MM-DD
            GlobalQuery.objects.filter(date=start).delete()
        else:
            GlobalQuery.objects.all().delete()
        
        # Re for remove all emoji from text
        emoji_pattern = re.compile("["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        u"\U00002500-\U00002BEF"  # chinese char
                                        u"\U00002702-\U000027B0"
                                        u"\U00002702-\U000027B0"
                                        u"\U000024C2-\U0001F251"
                                        u"\U0001f926-\U0001f937"
                                        u"\U00010000-\U0010ffff"
                                        u"\u2640-\u2642" 
                                        u"\u2600-\u2B55"
                                        u"\u200d"
                                        u"\u23cf"
                                        u"\u23e9"
                                        u"\u231a"
                                        u"\ufe0f"  # dingbats
                                        u"\u3030"
                                "]+", flags=re.UNICODE)
        
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
                page_title = emoji_pattern.sub(r'', row[13]),
                time_on_page_in_seconds = 0 if row[16] == '' else row[16],
                total_time = row[17],
                maxi = datetime.fromtimestamp(int(row[18])/1000000).strftime('%Y-%m-%d %H:%M:%S'),
                mini = datetime.fromtimestamp(int(row[19])/1000000).strftime('%Y-%m-%d %H:%M:%S'),
                all_source = row[20],
                brands = row[21],
                modeles = row[22],
            )
            
            rows.save()
    return 'Data saved'
