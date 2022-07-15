import pandas as pd
from sqlalchemy import create_engine

def query_building_total(db,start_time,end_time,building_name,organization=None):
    
    engine = create_engine(db.ENGINE_TRIAL)

    conn = engine.connect().execution_options(stream_results=True)

    time_period = f"""(time >= '{start_time}') and (time < '{end_time}')"""

    statement_list = [f""""building_name" like '{building_name}'"""]
    
    if organization is not None:
        statement_new = f""""organization" like '{organization}'"""
        statement_list.append(statement_new)

    statement_full = ' and '.join(statement_list)

    query = f"""select * from {db.table_name_building_total} where {statement_full} and {time_period};"""

    df_meta_with_value = pd.read_sql_query(query, con=conn)

    return df_meta_with_value