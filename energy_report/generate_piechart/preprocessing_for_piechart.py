from datetime import date

from monthly_mindsett_report_modules.utility_functions import get_group_with_others

def preprocessing_for_piechart(df_meta_with_value, 
                                asset_group='asset_class',
                                reading_interval_in_mins=10,
                                pct_level_tobe_others = 0.006,
                                period_current=None,
                                period_step=1):
    # Conversion into MWh
    w_to_kw_para = 1./1000
    min_to_hour_para = 1./60

    wm_to_kwh_parameter = w_to_kw_para * min_to_hour_para
    reading_to_kwh_parameter = reading_interval_in_mins * wm_to_kwh_parameter

    sr_pivot_asset_class = df_meta_with_value.groupby([asset_group, "period"]).sum()["W"] * reading_to_kwh_parameter

    df_pivot_asset_group_by_period = sr_pivot_asset_class.unstack(["period"])
    
    # using the 'period' information from the dataframe
    period_range = df_pivot_asset_group_by_period.columns
    period_current = period_range[-1]
    
     # for avoiding the case that we don't have data for the previous week
    if len(period_range) < 2:
        period_tobe_compared = period_range[-1]
    else:
        period_tobe_compared = period_range[-2]

    df_pivot_asset_group_by_period_renamed = df_pivot_asset_group_by_period.loc[:,period_current].to_frame().rename(columns={period_current: "sum"})
    df_pivot_asset_group_by_period_renamed["sum_pre"] = df_pivot_asset_group_by_period.loc[:,period_tobe_compared]
    df_pivot_asset_group_by_period_renamed['sub'] = df_pivot_asset_group_by_period.loc[:,period_current] - df_pivot_asset_group_by_period.loc[:,period_tobe_compared]

    df_pivot_asset_group_by_period_renamed["pct"] = df_pivot_asset_group_by_period_renamed["sum"]/df_pivot_asset_group_by_period_renamed["sum"].sum()
    df_pivot_asset_group_by_period_renamed["gt_4pct"] = df_pivot_asset_group_by_period_renamed["pct"].gt(pct_level_tobe_others)

    df_asset_group_period_sum = df_pivot_asset_group_by_period_renamed.reset_index()

    df_asset_group_period_sum["group_with_others"] = df_asset_group_period_sum.apply(get_group_with_others, asset_group=asset_group, axis=1)

    df_asset_group_period_sum_others = df_asset_group_period_sum.groupby(["group_with_others"]).sum()

    df_asset_group_period_sum_others["sum_for_sort"] = df_asset_group_period_sum_others["sum"] 

    df_asset_group_period_sum_others.loc["Others", "sum_for_sort"] = 0

    df_asset_group_period_sum_others.sort_values(["sum_for_sort"], ascending=False, inplace=True)

    df_asset_group_period_sum_others["sub_pct"] = df_asset_group_period_sum_others["sub"]/df_asset_group_period_sum_others["sum_pre"]
    
    return df_asset_group_period_sum_others