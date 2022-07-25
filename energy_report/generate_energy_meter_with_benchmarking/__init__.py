from pathlib import Path
import matplotlib.pyplot as plt

from .preprocessing_for_energy_meter_with_benchmarking import preprocessing_for_energy_meter_with_benchmarking
from .energy_meter_with_benchmarking import energy_meter_with_benchmarking


def generate_energy_meter_with_benchmarking(df_meta_with_value_building, floor_size,
                                            industry = "office",
                                            size_in_sqm = True,
                                            directory_to_savefig='./figures/'):
                                            
    consumption_mwh_cur, consumption_mwh_pre, days_in_period = preprocessing_for_energy_meter_with_benchmarking(df_meta_with_value_building)


    energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre, floor_size, 
                                    industry=industry, period=days_in_period, size_in_sqm=size_in_sqm)
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Monthly_total_and_bm_latest.png", format='png', dpi=200,transparent=True, bbox_inches='tight', pad_inches=0)