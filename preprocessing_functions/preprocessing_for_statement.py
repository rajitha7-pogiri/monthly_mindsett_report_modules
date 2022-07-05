

from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine

from monthly_mindsett_report_modules.utility_functions import enriching_time_features


from .get_group_with_others import get_group_with_others

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

def preprocessing_for_statement(df_meta_with_value, 
                                asset_group='asset_class',
                                row_index_for_total = "Total", 
                                reading_interval_in_mins=10,
                                pct_level_tobe_others = 0.06,
                                month_current=None,
                                month_step=1):
    
    #Conversion into MWh
    w_to_kw_para = 1./1000
    min_to_hour_para = 1./60
    
    wm_to_kwh_parameter = w_to_kw_para * min_to_hour_para
    reading_to_kwh_parameter = reading_interval_in_mins * wm_to_kwh_parameter
    sr_pivot_asset_group = df_meta_with_value.groupby([asset_group, 'month', 'out_of_hours']).sum()["W"] * reading_to_kwh_parameter  # Div 1000 for convertion to MWh

    df_pivot_asset_group_by_month = sr_pivot_asset_group.unstack(["out_of_hours"]).rename(columns={True:'sum'})['sum']

    # can be improved by using the 'month' information from the dataframe
    if month_current is None:#
        today = date.today()
        month_current = int(today.strftime("%m")) - 1
         
    month_tobe_compared = (month_current - month_step)

    df_pivot_asset_group_by_month_renamed = df_pivot_asset_group_by_month.loc[:,month_current].to_frame().rename(columns={month_current: "sum"})
    df_pivot_asset_group_by_month_renamed["sum_pre"] = df_pivot_asset_group_by_month.loc[:,month_tobe_compared]

    sr_total = df_pivot_asset_group_by_month_renamed.sum()

    df_total = sr_total.to_frame().transpose()
    df_total.index = [row_index_for_total]

    df_total.index.name = df_pivot_asset_group_by_month_renamed.index.name

    df_pivot_asset_group_by_month_renamed = pd.concat([df_pivot_asset_group_by_month_renamed, df_total])

    df_pivot_asset_group_by_month_renamed['sub'] = df_pivot_asset_group_by_month_renamed.loc[:,'sum'] - df_pivot_asset_group_by_month_renamed.loc[:,'sum_pre']

    df_pivot_asset_group_by_month_renamed["pct"] = df_pivot_asset_group_by_month_renamed["sum"]/df_pivot_asset_group_by_month_renamed.loc[row_index_for_total, "sum"]
    df_pivot_asset_group_by_month_renamed["gt_4pct"] = df_pivot_asset_group_by_month_renamed["pct"].gt(pct_level_tobe_others)

    df_asset_group_monthly_sum = df_pivot_asset_group_by_month_renamed.reset_index()

    df_asset_group_monthly_sum["group_with_others"] = df_asset_group_monthly_sum.apply(get_group_with_others,asset_group=asset_group,axis=1)

    df_asset_group_monthly_sum_others = df_asset_group_monthly_sum.groupby(["group_with_others"]).sum()

    df_asset_group_monthly_sum_others["sum_for_sort"] = df_asset_group_monthly_sum_others["sum"] 

    df_asset_group_monthly_sum_others.loc["Others", "sum_for_sort"] = 0

    df_asset_group_monthly_sum_others.sort_values(["sum_for_sort"], ascending=False, inplace=True)
    df_asset_group_monthly_sum_others["sub_pct"] = df_asset_group_monthly_sum_others["sub"]/df_asset_group_monthly_sum_others["sum_pre"]
    
    return df_asset_group_monthly_sum_others

