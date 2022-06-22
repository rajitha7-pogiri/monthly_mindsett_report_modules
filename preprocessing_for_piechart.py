from datetime import date
import pandas as pd

def preprocessing_for_piechart(df_meta_with_value, 
                                asset_group='asset_class',
                                reading_interval_in_mins=10,
                                pct_level_tobe_others = 0.06,
                                month_current=None,
                                month_step=1):
    # Conversion into MWh
    w_to_kw_para = 1./1000
    min_to_hour_para = 1./60

    wm_to_kwh_parameter = w_to_kw_para * min_to_hour_para
    reading_to_kwh_parameter = reading_interval_in_mins * wm_to_kwh_parameter

    sr_pivot_asset_class = df_meta_with_value.groupby(["month",asset_group]).sum()["W"] * reading_to_kwh_parameter

    df_pivot_asset_group_by_month = sr_pivot_asset_class.unstack(["month"])
    
    # can be improved by using the 'month' information from the dataframe
    if month_current is None:#
        today = date.today()
        month_current = int(today.strftime("%m")) - 1

    month_tobe_compared = (month_current - month_step)

    df_pivot_asset_group_by_month_renamed = df_pivot_asset_group_by_month.loc[:,month_current].to_frame().rename(columns={month_current: "sum"})
    df_pivot_asset_group_by_month_renamed["sum_pre"] = df_pivot_asset_group_by_month.loc[:,month_tobe_compared]
    df_pivot_asset_group_by_month_renamed['sub'] = df_pivot_asset_group_by_month.loc[:,month_current] - df_pivot_asset_group_by_month.loc[:,month_tobe_compared]

    df_pivot_asset_group_by_month_renamed["pct"] = df_pivot_asset_group_by_month_renamed["sum"]/df_pivot_asset_group_by_month_renamed["sum"].sum()
    df_pivot_asset_group_by_month_renamed["gt_4pct"] = df_pivot_asset_group_by_month_renamed["pct"].gt(pct_level_tobe_others)

    df_asset_group_monthly_sum = df_pivot_asset_group_by_month_renamed.reset_index()

    df_asset_group_monthly_sum["group_with_others"] = df_asset_group_monthly_sum.apply(get_group_with_others, asset_group=asset_group, axis=1)

    df_asset_group_monthly_sum_others = df_asset_group_monthly_sum.groupby(["group_with_others"]).sum()

    df_asset_group_monthly_sum_others["sum_for_sort"] = df_asset_group_monthly_sum_others["sum"] 

    df_asset_group_monthly_sum_others.loc["Others", "sum_for_sort"] = 0

    df_asset_group_monthly_sum_others.sort_values(["sum_for_sort"], ascending=False, inplace=True)

    df_asset_group_monthly_sum_others["sub_pct"] = df_asset_group_monthly_sum_others["sub"]/df_asset_group_monthly_sum_others["sum_pre"]
    
    return df_asset_group_monthly_sum_others