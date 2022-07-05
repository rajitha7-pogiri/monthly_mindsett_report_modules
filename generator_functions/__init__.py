
from pathlib import Path
import pickle
import os
import matplotlib.pyplot as plt
from datetime import date

from monthly_mindsett_report_modules.utility_functions import enriching_time_features

from .processing_functions import ( import_data_with_meta,
                                    query_building_total,
                                    preprocessing_for_co2_barchart,
                                    preprocessing_for_piechart,
                                    preprocessing_for_barchart,
                                    preprocessing_for_energy_meter_with_benchmarking,
                                    preprocessing_for_statement)

from .pie_chart import piechart_comparison_design
from .energy_meter_with_benchmarking import energy_meter_with_benchmarking
from .barchart_with_occupancy import (import_occupancy,generate_day_code,energy_and_occupancy_barchart_design)
from .barchart_with_co2 import co2_barchart_design
from .insight_statements import insight_statements

from .report_template import generate_report

files_folder = os.path.join(os.getcwd(), 'files/')
figures_folder = os.path.join(os.getcwd(), 'figures/')

def generate_insight_statements(db, df_meta_with_value, 
                                month_current=None,
                                month_step=1, 
                                directory_to_savefile='./files/'): # todo: update the default value for directory

    df_for_statements = preprocessing_for_statement(df_meta_with_value,  month_current=month_current, month_step=month_step)

    statements_list = insight_statements(db,df_for_statements,df_meta_with_value)

    # Specify the directory to save figures, if it does not exist, create it
    Path(directory_to_savefile).mkdir(parents=True, exist_ok=True)

    with open(directory_to_savefile+'statements.pkl', 'wb') as f:
        pickle.dump(statements_list, f)


def generate_piechart(df_meta_with_value, asset_group, 
                      directory_to_savefig = './figures/'):

    df_for_piechart = preprocessing_for_piechart(df_meta_with_value, asset_group=asset_group)

    # Specify the directory to save figures, if it does not exist, create it
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)

    piechart_comparison_design(df_for_piechart, ncol=1,loc='center right')
    plt.savefig(directory_to_savefig+"consumption_by_assetclass_piechart_mindsett.png",format='png', dpi=200)


def generate_barchart_with_occupancy(db_occupancy, site_name, df_meta_with_value, 
                                     month_current=None, 
                                     occupancy_available = False,
                                     tick_range_e=None,
                                     tick_range_o=[-5, 40],
                                     top_hours=True,
                                     directory_to_savefig='./figures/'):

    if month_current is None:
        today = date.today()
        month_current = int(today.strftime("%m")) - 1

    df_meta_with_value_for_barchart = df_meta_with_value.loc[df_meta_with_value.month==month_current]

    df_pivot_working_hours = preprocessing_for_barchart(df_meta_with_value_for_barchart)

    if occupancy_available: 
        # import occupancy data
        df_occupancy_cur = import_occupancy(db_occupancy, site_name)
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


def generate_co2_barchart(df_meta_with_value_building,
                          directory_to_savefig='./figures/'):
    df_grouped_working_hours_period_unstacked= preprocessing_for_co2_barchart(df_meta_with_value_building)
    co2_barchart_design(df_grouped_working_hours_period_unstacked)
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Total_consumption_barchart_with_Co2.png",format='png', dpi=200)


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



def energy_report(cf):
    
    df_meta_with_value = import_data_with_meta(cf.postgresdb, cf.influxdb, cf.start_time, cf.end_time, cf.site_name,
                                                  exception=cf.exception,
                              meta_columns_for_join=cf.meta_columns_for_join,
                              iot_columns_for_join=cf.iot_columns_for_join)

    df_meta_with_value[cf.asset_group] = df_meta_with_value[cf.asset_group].fillna(cf.fillna_value) 

    df_meta_with_value = enriching_time_features(df_meta_with_value, 
                                                    weekend=cf.weekend, 
                                                    working_end_time=cf.working_end_time, 
                                                    working_start_time=cf.working_start_time)
                                                
    df_meta_with_value_building = query_building_total(cf.postgresdb,start_time = cf.start_time_co2_barchart,end_time = cf.end_time, building_name = cf.site_name)
    df_meta_with_value_building = enriching_time_features(df_meta_with_value_building)

    generate_insight_statements(cf.postgresdb,df_meta_with_value)

    generate_piechart(df_meta_with_value, cf.asset_group)
    
    generate_energy_meter_with_benchmarking(df_meta_with_value_building, cf.floor_sqm, industry=cf.industry, period_freq=cf.period_freq)

    generate_barchart_with_occupancy(cf.postgresdb, cf.site_name, df_meta_with_value, occupancy_available=cf.occupancy_available)

    generate_co2_barchart(df_meta_with_value_building)

    generate_report(cf.site_name, organisation=cf.organisation)


