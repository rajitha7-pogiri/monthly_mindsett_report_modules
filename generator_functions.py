
from pathlib import Path
import pickle
import os
import matplotlib.pyplot as plt
from datetime import date

from preprocessing_for_energy_meter_with_benchmarking import preprocessing_for_energy_meter_with_benchmarking

from .processing_functions import (statement_for_biggest_ooh, preprocessing_for_statement, 
                                    statement_for_avg_action_time, statement_for_total_ooh, 
                                    preprocessing_for_piechart,preprocessing_for_barchart,
                                    import_data_with_meta,enriching_time_features,preprocessing_for_co2_barchart,query_building_total)

from .pie_chart import piechart_comparison_design
from .energy_meter_with_benchmarking import energy_meter_with_benchmarking
from .barchart_with_occupancy import (import_occupancy,generate_day_code,energy_and_occupancy_barchart_design)
from .barchart_with_co2 import co2_barchart_design
from .report_template import generate_report

files_folder = os.path.join(os.getcwd(), 'files/')
figures_folder = os.path.join(os.getcwd(), 'figures/')

def generate_insight_statements(db, df_meta_with_value, 
                                month_current=None,
                                month_step=1, 
                                directory_to_savefile='./files/'): # todo: update the default value for directory

    df_for_statements = preprocessing_for_statement(df_meta_with_value,  month_current=month_current, month_step=month_step)

    statements_list = []

    statement_str_total_ooh = statement_for_total_ooh(df_for_statements)
    statements_list.append(statement_str_total_ooh)

    statement_str_biggest_ooh = statement_for_biggest_ooh(df_for_statements)
    statements_list.append(statement_str_biggest_ooh)

    # preparation for the third statement

    asset_name = 'Pizza Oven'

    if asset_name in df_meta_with_value.circuit_description.unique():

        site_name = df_meta_with_value.site_name.unique()[0]
        max_period = df_meta_with_value.index.tz_convert(None).to_period('M').unique().max()
        start_time_str = max_period.start_time
        end_time_str = max_period.end_time

        statement_str_avg_action_time = statement_for_avg_action_time(db, site_name, asset_name, start_time_str, end_time_str,
                                  action=1)
        statements_list.append(statement_str_avg_action_time)

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

    consumption_mwh_cur = df_for_piechart['sum'].sum()/1000
    consumption_mwh_pre = df_for_piechart['sum_pre'].sum()/1000

    return consumption_mwh_cur, consumption_mwh_pre


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


def generate_energy_meter_with_benchmarking(df_meta_with_value_building,
                                            directory_to_savefig='./figures/'):
    consumption_mwh_cur, consumption_mwh_pre= preprocessing_for_energy_meter_with_benchmarking(df_meta_with_value_building)
    energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre)
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Monthly_total_and_bm_latest.png",format='png', dpi=200)



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

    # todo: the value should be obtained from the mains directly

    #consumption_mwh_cur, consumption_mwh_pre = generate_piechart(df_meta_with_value, cf.asset_group)
    consumption_mwh_cur, consumption_mwh_pre = generate_energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre)
    #energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre, cf.floor_sqm, industry=cf.industry)
    generate_energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre, cf.floor_sqm, industry=cf.industry)

    generate_barchart_with_occupancy(cf.postgresdb, cf.site_name, df_meta_with_value, occupancy_available=cf.occupancy_available)



    generate_co2_barchart(df_meta_with_value_building)

    generate_report(cf.site_name, organisation=cf.organisation)


