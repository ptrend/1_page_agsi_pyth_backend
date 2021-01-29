'''AGSIdata
output agsi_data.js"'''

import requests
from datetime import datetime
import pandas as pd
import json as json

def agsi_scrap_fun():
    now1 = datetime.now() 
    df_dictionary={}
    
    headers = {"x-key": "709a7d013e4fda8f3e21166c33a1a691"}
    df_columns=['status', 'gasDayStartedOn', 'gasInStorage', 'workingGasVolume']
    
    with open("agsi_links.json") as json_file:
        json_urls = json.load(json_file)
        json_file.close()
        
    for key in json_urls.keys():
        url_list = json_urls[key] 
        df_country = pd.DataFrame(columns=df_columns)
        for url in url_list:
            try:
                df = pd.read_json((requests.get(url,headers=headers)).text).dropna(axis="index")
                df = df[(df['gasInStorage']!="-") & (df['status']!="N")]
                df = df[["gasDayStartedOn","gasInStorage","workingGasVolume"]]
                df[['gasInStorage','workingGasVolume']] = df[['gasInStorage','workingGasVolume']].astype(float)
                if (len(df)):
                    df_country = pd.concat([df_country,df],axis = 0)
            except:
                print(url,": blad")
        df_country = df_country.sort_values("gasDayStartedOn",ascending = True).reset_index()
        df_country = df_country.groupby("gasDayStartedOn")[['gasInStorage','workingGasVolume']].sum().reset_index()
        df_country['gasInStorage'] = round(df_country['gasInStorage'],1)
        df_country['workingGasVolume'] = round(df_country['workingGasVolume'],1)
        df_country['percent'] = round((df_country['gasInStorage'] / df_country['workingGasVolume']) * 100,1).fillna(0)
        print(key)
        hist = df_country.values
        arr_rob = []
        for row in hist:
            arr_rob.append([(item) for item in row])
        df_dictionary[key] = arr_rob
    now2 = datetime.now()               
    print(now2-now1)
    
    with open("agsi_data.js", "w") as f:
        f.write("let stor=" + str(df_dictionary))
        f.close()
    
    dict_last_data = {}
    for key in df_dictionary.keys():
        dict_last_data[key]={}
        dict_last_data[key]["last_gasinstorage"] = df_dictionary[key][-1][1]
        dict_last_data[key]['last_percent'] = df_dictionary[key][-1][3]
    with open("last_agsi_data.js","w") as f:
        f.write("let stor=" + str(dict_last_data))
        f.close()
        
agsi_scrap_fun()
