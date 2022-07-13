from pathlib import Path
import pickle

from monthly_mindsett_report_modules.utility_functions import enriching_time_features

from .processing_functions import (import_data_with_meta,
                                   query_building_total)
from .generate_insight_statements import generate_insight_statements
from .generate_piechart import generate_piechart
from .generate_energy_meter_with_benchmarking import generate_energy_meter_with_benchmarking
from .generate_barchart_with_occupancy import generate_barchart_with_occupancy
from .generate_co2_barchart import generate_co2_barchart

from .report_template import generate_report


def energy_report(cf):

    # add cache mehanism to improve efficiency for testing

    # Specify the directory to save figures, if it does not exist, create it
    directory_to_cache = './cache'
    Path(directory_to_cache).mkdir(parents=True, exist_ok=True)

    
    df_meta_with_value = import_data_with_meta(cf.postgresdb, cf.influxdb, cf.start_time, cf.end_time, cf.site_name,
                                                  exception=cf.exception,
                              meta_columns_for_join=cf.meta_columns_for_join,
                              iot_columns_for_join=cf.iot_columns_for_join)

    df_meta_with_value[cf.asset_group] = df_meta_with_value[cf.asset_group].fillna(cf.fillna_value) 

    df_meta_with_value = enriching_time_features(df_meta_with_value, 
                                                    period_freq=cf.period_freq,
                                                    weekend=cf.weekend, 
                                                    working_end_time=cf.working_end_time, 
                                                    working_start_time=cf.working_start_time)
                                                
    df_meta_with_value_building = query_building_total(cf.postgresdb, 
                                                       start_time=cf.start_time_co2_barchart,
                                                       end_time=cf.end_time, 
                                                       building_name = cf.site_name)

    df_meta_with_value_building = enriching_time_features(df_meta_with_value_building,
                                                    period_freq=cf.period_freq)

    generate_insight_statements(cf.postgresdb, df_meta_with_value)

    generate_piechart(df_meta_with_value, cf.asset_group)
    
    generate_energy_meter_with_benchmarking(df_meta_with_value_building, cf.floor_sqm, industry=cf.industry)

    generate_barchart_with_occupancy(cf.postgresdb, cf.site_name, df_meta_with_value, occupancy_available=cf.occupancy_available)

    generate_co2_barchart(df_meta_with_value_building)

    try: # Handel the case where insights statement is not provided
        generate_report(cf.site_name, statements_list=cf.insight_statements, organisation=cf.organisation)
    except:
        generate_report(cf.site_name, organisation=cf.organisation)


