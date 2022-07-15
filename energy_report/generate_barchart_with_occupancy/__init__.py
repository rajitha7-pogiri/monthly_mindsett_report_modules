from pathlib import Path
import matplotlib.pyplot as plt
from datetime import date

from .preprocessing_for_barchart import preprocessing_for_barchart
from .barchart_with_occupancy import (import_occupancy,
                                      generate_day_code,
                                      energy_and_occupancy_barchart_design)

def generate_barchart_with_occupancy(db_occupancy, site_name, df_meta_with_value, 
                                     occupancy_available = False,
                                     tick_range_e=None,
                                     tick_range_o=None,
                                     top_hours=True,
                                     directory_to_savefig='./figures/'):


    period_current = df_meta_with_value["period"].unique()[-1]

    df_meta_with_value_for_barchart = df_meta_with_value.loc[df_meta_with_value["period"]==period_current]

    df_pivot_working_hours = preprocessing_for_barchart(df_meta_with_value_for_barchart)

    if occupancy_available: 
        # import occupancy data
        df_occupancy_cur = import_occupancy(db_occupancy, site_name, period_current)
        # print("df_occupancy_cur: ", df_occupancy_cur.info())
    else:
        df_occupancy_cur = None

    day_code_list = generate_day_code(df_meta_with_value_for_barchart)

    # barchart with occupancy
    
    energy_and_occupancy_barchart_design(df_pivot_working_hours,
                                             day_code_list,
                                             df_occupancy_cur = df_occupancy_cur,
                                             tick_range_e=tick_range_e,
                                             tick_range_o=tick_range_o,
                                             top_hours=top_hours)

    
    # Specify the directory to save figures, if it does not exist, create it
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"daily_consumption_barchart_with_occupancy_mar_with_pattern_MWh.png",format='png', dpi=200)
