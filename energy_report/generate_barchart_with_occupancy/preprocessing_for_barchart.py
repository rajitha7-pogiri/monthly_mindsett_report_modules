

def preprocessing_for_barchart(df_meta_with_value, reading_interval_in_mins=10):
    
    # select data only for the current period

    # Conversion into MWh
    w_to_mw_para = 1./1000/1000
    min_to_hour_para = 1./60

    wm_to_mwh_parameter = w_to_mw_para * min_to_hour_para
    reading_to_mwh_parameter = reading_interval_in_mins * wm_to_mwh_parameter

    # todo: Better to change to df_meta_value_building
    df_grouped_working_hours_multiple_period = df_meta_with_value.groupby(["date", 'out_of_hours', "period"]).sum()["W"] * reading_to_mwh_parameter  # Div 1000 for convertion to MWh

    df_grouped_working_hours_multiple_period_unstack = df_grouped_working_hours_multiple_period.unstack(["period"])
    period_current = df_grouped_working_hours_multiple_period_unstack.columns[-1]
    df_grouped_working_hours = df_grouped_working_hours_multiple_period_unstack.loc[:, period_current]

    df_pivot_working_hours_sorted = df_grouped_working_hours.unstack(['out_of_hours']).sort_index(axis=1,level=1, ascending=False)
    
    return df_pivot_working_hours_sorted