from datetime import date

def preprocessing_for_barchart(df_meta_with_value, reading_interval_in_mins=10):
    
    # Conversion into MWh
    w_to_mw_para = 1./1000/1000
    min_to_hour_para = 1./60

    wm_to_mwh_parameter = w_to_mw_para * min_to_hour_para
    reading_to_mwh_parameter = reading_interval_in_mins * wm_to_mwh_parameter

    df_grouped_working_hours = df_meta_with_value.groupby(["day_of_month", 'out_of_hours']).sum()["W"] * reading_to_mwh_parameter  # Div 1000 for convertion to MWh

    df_pivot_working_hours = df_grouped_working_hours.unstack().sort_index(axis=1,level=1, ascending=False)
    
    return df_pivot_working_hours