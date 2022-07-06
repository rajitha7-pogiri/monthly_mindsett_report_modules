from pathlib import Path
import matplotlib.pyplot as plt

from .processing_functions import preprocessing_for_energy_meter_with_benchmarking
from .energy_meter_with_benchmarking import energy_meter_with_benchmarking


def generate_energy_meter_with_benchmarking(df_meta_with_value_building, floor_sqm,
                                            industry = "office",
                                            period_freq = 'M',
                                            size_in_sqm = True,
                                            directory_to_savefig='./figures/'):
    consumption_mwh_cur, consumption_mwh_pre= preprocessing_for_energy_meter_with_benchmarking(df_meta_with_value_building,freq=period_freq)
    if period_freq == 'M':
        period = 30
    elif period_freq == 'W':
        period = 7
    else:
        raise Exception ('Please specify preiod frequency: M for month, W for week').with_traceback(period_freq)


    energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre, floor_sqm, 
                                    industry=industry, period=period, size_in_sqm=size_in_sqm)
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Monthly_total_and_bm_latest.png", format='png', dpi=200,transparent=True, bbox_inches='tight', pad_inches=0)