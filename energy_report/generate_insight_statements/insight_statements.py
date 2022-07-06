from datetime import timedelta
import pandas as pd
from sqlalchemy import create_engine

from monthly_mindsett_report_modules.utility_functions import enriching_time_features

def statement_for_biggest_ooh(df_asset_group_monthly_sum_others, number_for_pick_out=3):

    df_ooh_biggest = df_asset_group_monthly_sum_others.head(number_for_pick_out+1).tail(number_for_pick_out).drop(columns=['gt_4pct','sum_for_sort'])
    
    statement = f"""The biggest out-of-hour consumers of energy are """

    for index, item in enumerate(df_ooh_biggest['sum'].round().astype('int').iteritems()):

        statement_item = str(index+1)+'. '+item[0]+' '+str(item[1])+'kwh, '
        statement += statement_item

    statement = statement[:-2]+' over previous period.'
    
    return statement

def statement_for_total_ooh(df_asset_group_monthly_sum_others, row_index_for_total='Total'):

    sub_pct_value = df_asset_group_monthly_sum_others['sub_pct'][row_index_for_total]
    sub_pct_abs_value = round(abs(sub_pct_value * 100))

    if sub_pct_abs_value > 1:
        if sub_pct_value > 0:
            statement_direction = "up"
        else:
            statement_direction = "down"
        statement = f"""The out-of-hour use had gone {statement_direction} by {sub_pct_abs_value}% compared to previous period."""

    else:   
        statement = f"""The out-of-hour use had been similar to previous period."""
        
    return statement

def statement_for_avg_action_time(db, site_name, asset_name, start_time, end_time,
                                  action = 1):

    engine = create_engine(db.ENGINE)

    conn = engine.connect().execution_options(stream_results=True)

    time_restriction = f"""(time >= '{start_time}') and (time < '{end_time}')"""

    statement_list = [f""""site_name"='{site_name}'"""]
    statement_full = " and ".join(statement_list)

    df_on_off = pd.read_sql_query(f"""select * from {db.table_name_on_off} where {statement_full} and {time_restriction};""",
                                        con=conn)

    df_on_off = enriching_time_features(df_on_off)

    df_on_off_avg = df_on_off.groupby(['action', 'circuit_description']).time_of_day_in_float.mean()

    avg_start_time = str(timedelta(hours=df_on_off_avg[action][asset_name])).split('.')[0][:-3]
    
    start_finish_dict = {1: 'start', -1: 'finish'}

    statement = f"The average {start_finish_dict[action]} time for {asset_name} was {avg_start_time} over this period."
    
    return statement

def insight_statements(db,df_for_statements,df_meta_with_value):   #df_meta_with_value is only used to get metadata information
    
    statements_list = []

    statement_str_total_ooh = statement_for_total_ooh(df_for_statements)
    statements_list.append(statement_str_total_ooh)

    statement_str_biggest_ooh = statement_for_biggest_ooh(df_for_statements)
    statements_list.append(statement_str_biggest_ooh)

    # preparation for the third statement

    asset_name = 'Pizza Oven'

    if asset_name in df_meta_with_value.circuit_description.unique():

        site_name = df_meta_with_value.site_name.unique()[0]
        max_period = df_meta_with_value.index.tz_convert(None).to_period('M').unique().max()
        start_time_str = max_period.start_time
        end_time_str = max_period.end_time

        statement_str_avg_action_time = statement_for_avg_action_time(db, site_name, asset_name, start_time_str, end_time_str,
                                  action=1)
        statements_list.append(statement_str_avg_action_time)
        
    return statements_list