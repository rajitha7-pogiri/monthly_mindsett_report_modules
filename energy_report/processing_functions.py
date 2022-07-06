
import pandas as pd
from sqlalchemy import create_engine

from .db_read_query import  db_read_query
from .query_building_total import query_building_total

def resample_by_channels(df_source, reading_interval_in_mins=10):
    
    df_source_grouped = df_source.groupby(["nid", "channel", pd.Grouper(freq=f'{reading_interval_in_mins}Min')]).mean()
    df_source_pivot = df_source_grouped.unstack(level=[0,1])
    df_source_pivot_resampled = df_source_pivot.resample(f"{reading_interval_in_mins}Min").mean().ffill()
    df_source_filled = df_source_pivot_resampled.stack(level=[1,2]).reset_index()
    df_source_filled['channel']= df_source_filled['channel'].astype(str)
    
    return df_source_filled


def import_metadata(db, site_name, organisation=None, exception=None):

    statement_list = [f""""site_name"='{site_name}'"""]

    if organisation is not None:
        statement_new  = f""""organisation" = '{organisation}'"""
        statement_list.append(statement_new)

    if exception is not None:
        for key in exception:
            statement_new  = f""""{key}" != '{exception[key]}'"""
            statement_list.append(statement_new)

    engine = create_engine(db.ENGINE)

    conn = engine.connect().execution_options(stream_results=True)
    
    statement_full = " and ".join(statement_list)
    df_meta = pd.read_sql_query(f"""select * from {db.table_name} where {statement_full};""",
                                    con=conn)

    df_meta.channel_number = df_meta.channel_number.astype(str)
    
    return df_meta

def import_data_with_meta(db_meta, db_iot, start_time, end_time, site_name, 
                          organisation=None, 
                          exception=None,
                          meta_columns_for_join=['nid', 'channel_number'],
                          iot_columns_for_join=['nid', 'channel'],
                          reading_interval_in_mins=10):

    df_meta = import_metadata(db_meta, site_name, 
                                 organisation=organisation, 
                                 exception=exception)

    query_start_time = pd.Timestamp(start_time, tz="UTC")
    query_end_time  =  pd.Timestamp(end_time, tz="UTC")

    df_iot = db_read_query(db_iot, query_start_time, query_end_time, df_meta)

    df_source_filled = resample_by_channels(df_iot,
                                            reading_interval_in_mins=reading_interval_in_mins)

    df_meta_with_value = df_meta.merge(df_source_filled, left_on= meta_columns_for_join, right_on=iot_columns_for_join)
    
    return df_meta_with_value
