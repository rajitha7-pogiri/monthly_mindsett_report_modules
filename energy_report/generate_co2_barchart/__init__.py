from pathlib import Path
import matplotlib.pyplot as plt

from .preprocessing_for_co2_barchart import preprocessing_for_co2_barchart
from .barchart_with_co2 import co2_barchart_design

def generate_co2_barchart(df_meta_with_value_building,
                          directory_to_savefig='./figures/'):
                          
    df_grouped_working_hours_period_unstacked= preprocessing_for_co2_barchart(df_meta_with_value_building)

    co2_barchart_design(df_grouped_working_hours_period_unstacked)
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Total_consumption_barchart_with_Co2.png",format='png', dpi=200,transparent=True, bbox_inches='tight', pad_inches=0)