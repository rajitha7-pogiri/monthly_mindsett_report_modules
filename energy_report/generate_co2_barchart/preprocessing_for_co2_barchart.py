import pandas as pd
from itertools import product

def preprocessing_for_co2_barchart(df_meta_with_value,
                                   period_column="period", 
                                   out_of_hours_column="out_of_hours", 
                                   kwh_column="kwh",
                                   no_of_month=6):

    # df_meta_with_value[period_column]  = df_meta_with_value.index.tz_convert(None).to_period(freq)

    df_grouped_working_hours_period = df_meta_with_value.groupby([period_column, out_of_hours_column]).sum()[kwh_column]

    # handle the situation that not all groups exist
    period_max = df_meta_with_value[period_column].max()
    expected_periods = [period_max-i for i in range(no_of_month)]
    expected_working_hours = [True, False]
    expected_group_index = pd.Index(product(expected_periods, expected_working_hours))
    missing_group_index = expected_group_index.drop(df_grouped_working_hours_period.index)

    for indice in missing_group_index:
        df_grouped_working_hours_period.loc[indice] = 0

    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period.unstack()
    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period_unstacked.sort_index()


    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period_unstacked.div(1000)
    
    return df_grouped_working_hours_period_unstacked