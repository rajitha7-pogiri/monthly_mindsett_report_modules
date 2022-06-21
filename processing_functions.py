
import pandas as pd

def resample_by_channels(df_source, reading_interval_in_mins=10):
    
    df_source_grouped = df_source.groupby(["nid", "channel", pd.Grouper(freq=f'{reading_interval_in_mins}Min')]).mean()
    df_source_pivot = df_source_grouped.unstack(level=[0,1])
    df_source_pivot_resampled = df_source_pivot.resample(f"{reading_interval_in_mins}Min").mean().ffill()
    df_source_filled = df_source_pivot_resampled.stack(level=[1,2]).reset_index()
    df_source_filled['channel']= df_source_filled['channel'].astype(str)
    
    return df_source_filled

def enriching_time_features(df_meta_with_value, weekend=5, end_time="18:00:00", start_time="08:00:00"):
    
    # manipulate and clean the data
    df_meta_with_value.time=pd.to_datetime(df_meta_with_value.time) 
    df_meta_with_value = df_meta_with_value.set_index("time") 

    # enrich_time_information
    df_meta_with_value["date"] = df_meta_with_value.index.date
    df_meta_with_value["day_of_month"] = df_meta_with_value.index.day
    df_meta_with_value["time_of_day"] = df_meta_with_value.index.time
    df_meta_with_value["weekday"] = df_meta_with_value.index.weekday
    df_meta_with_value["day_name"] = df_meta_with_value.index.day_name()
    df_meta_with_value["day_code"] = df_meta_with_value["day_name"].str[0]
    df_meta_with_value["month"] = df_meta_with_value.index.month

    df_meta_with_value["out_of_hours"] = df_meta_with_value['weekday'].ge(weekend) | \
                                            (df_meta_with_value["time_of_day"] > pd.to_datetime(end_time).time()) | \
                                            (df_meta_with_value["time_of_day"] < pd.to_datetime(start_time).time())
    return df_meta_with_value

def statement_for_biggest_ooh(df_ooh_biggest):
    
    statement = f"""The biggest out-of-hour consumers of energy are """

    for index, item in enumerate(df_ooh_biggest['sum'].round().astype('int').iteritems()):

        statement_item = str(index+1)+'. '+item[0]+' '+str(item[1])+'kwh, '
        statement += statement_item

    statement[:-2]+' over previous period.'
    
    return statement

def statement_for_total_ooh(df_ooh_total, row_index_for_total='Total'):
    
    sub_pct_value = df_ooh_total['sub_pct'][row_index_for_total]
    sub_pct_abs_value = round(abs(sub_pct_value * 100))

    if sub_pct_abs_value > 1:
        if sub_pct_value > 0:
            statement_direction = "up"
        else:
            statement_direction = "down"
        statement = f"""The out-of-hour use had gone {statement_direction} by {sub_pct_abs_value}% previous week."""

    else:   
        statement = f"""The out-of-hour use had been similar to previous week."""
        
    return statement