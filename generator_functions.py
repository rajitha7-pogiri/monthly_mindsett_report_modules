
from pathlib import Path
import pickle
import os
import matplotlib.pyplot as plt

from .processing_functions import (statement_for_biggest_ooh, preprocessing_for_statement, statement_for_total_ooh, preprocessing_for_piechart)
from .pie_chart import piechart_comparison_design

files_folder = os.path.join(os.getcwd(), 'files/')
figures_folder = os.path.join(os.getcwd(), 'figures/')

def generate_insight_statements(df_meta_with_value, directory_to_savefile='./files/'): # todo: update the default value for directory

    df_for_statements = preprocessing_for_statement(df_meta_with_value)

    statements_list = []

    statement_str_total_ooh = statement_for_total_ooh(df_for_statements)
    statements_list.append(statement_str_total_ooh)

    statement_str_biggest_ooh = statement_for_biggest_ooh(df_for_statements)
    statements_list.append(statement_str_biggest_ooh)

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