

def preprocessing_for_energy_meter_with_benchmarking(df_meta_with_value_building,
                                                     period_column="period",  
                                                     kwh_column="kwh"):

    df_period_total = df_meta_with_value_building.groupby([period_column])[kwh_column].sum().div(1000).tail(2)

    consumption_mwh_pre, consumption_mwh_cur = df_period_total.to_list()

    days_in_period = df_period_total.index[-1].day

    return consumption_mwh_cur, consumption_mwh_pre, days_in_period