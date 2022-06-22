from datetime import date
import pandas as pd
from sqlalchemy import create_engine

from .db_read_query import  db_read_query

def resample_by_channels(df_source, reading_interval_in_mins=10):
    
    df_source_grouped = df_source.groupby(["nid", "channel", pd.Grouper(freq=f'{reading_interval_in_mins}Min')]).mean()
    df_source_pivot = df_source_grouped.unstack(level=[0,1])
    df_source_pivot_resampled = df_source_pivot.resample(f"{reading_interval_in_mins}Min").mean().ffill()
    df_source_filled = df_source_pivot_resampled.stack(level=[1,2]).reset_index()
    df_source_filled['channel']= df_source_filled['channel'].astype(str)
    
    return df_source_filled

def enriching_time_features(df_meta_with_value, weekend=5, working_end_time="18:00:00", working_start_time="08:00:00"):
    
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
                                            (df_meta_with_value["time_of_day"] > pd.to_datetime(working_end_time).time()) | \
                                            (df_meta_with_value["time_of_day"] < pd.to_datetime(working_start_time).time())
    return df_meta_with_value

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
        statement = f"""The out-of-hour use had gone {statement_direction} by {sub_pct_abs_value}% previous week."""

    else:   
        statement = f"""The out-of-hour use had been similar to previous week."""
        
    return statement

def get_group_with_others(row, asset_group):
    if row["gt_4pct"]:
        return row[asset_group]
    else:
        return "Others"

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