
def preprocessing_for_co2_barchart(df_meta_with_value,
                                   period_column="period", 
                                   out_of_hours_column="out_of_hours", 
                                   kwh_column="kwh"):

    # df_meta_with_value[period_column]  = df_meta_with_value.index.tz_convert(None).to_period(freq)

    df_grouped_working_hours_period = df_meta_with_value.groupby([period_column, out_of_hours_column]).sum()[kwh_column]
    
    print('df_meta_with_value: ', df_meta_with_value)
    print('df_grouped_working_hours_period: ', df_grouped_working_hours_period)
    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period.unstack()
    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period_unstacked.sort_index()


    df_grouped_working_hours_period_unstacked = df_grouped_working_hours_period_unstacked.div(1000)
    
    return df_grouped_working_hours_period_unstacked