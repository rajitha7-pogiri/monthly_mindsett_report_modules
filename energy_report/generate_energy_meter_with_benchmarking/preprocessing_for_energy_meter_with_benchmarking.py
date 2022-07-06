

def preprocessing_for_energy_meter_with_benchmarking(df_meta_with_value_building,
                                                     freq='M', 
                                                     period_column="period",  
                                                     kwh_column="kwh"):

    df_meta_with_value_building[period_column]  = df_meta_with_value_building.index.tz_convert(None).to_period(freq)

    df_monthly_total= df_meta_with_value_building.groupby([period_column])[kwh_column].sum().div(1000).tail(2)

    consumption_mwh_pre, consumption_mwh_cur = df_monthly_total.to_list()

    return consumption_mwh_cur, consumption_mwh_pre