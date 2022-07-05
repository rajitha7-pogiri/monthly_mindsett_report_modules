
import pandas as pd

def enriching_time_features(df_meta_with_value, weekend=5, working_end_time="18:00:00", working_start_time="08:00:00"):
    
    # manipulate and clean the data
    df_meta_with_value.time=pd.to_datetime(df_meta_with_value.time) 
    df_meta_with_value = df_meta_with_value.set_index("time") 

    # enrich_time_information
    df_meta_with_value["date"] = df_meta_with_value.index.date
    df_meta_with_value["day_of_month"] = df_meta_with_value.index.day
    df_meta_with_value["time_of_day"] = df_meta_with_value.index.time

    df_meta_with_value['time_of_day_in_float'] = df_meta_with_value.index.hour+df_meta_with_value.index.minute/60+df_meta_with_value.index.second/3600

    df_meta_with_value["weekday"] = df_meta_with_value.index.weekday
    df_meta_with_value["day_name"] = df_meta_with_value.index.day_name()
    df_meta_with_value["day_code"] = df_meta_with_value["day_name"].str[0]
    df_meta_with_value["month"] = df_meta_with_value.index.month
    df_meta_with_value["month_name"] = df_meta_with_value.index.month_name() #new change/implementation -RP
    df_meta_with_value["out_of_hours"] = df_meta_with_value['weekday'].ge(weekend) | \
                                            (df_meta_with_value["time_of_day"] > pd.to_datetime(working_end_time).time()) | \
                                            (df_meta_with_value["time_of_day"] < pd.to_datetime(working_start_time).time())
    return df_meta_with_value