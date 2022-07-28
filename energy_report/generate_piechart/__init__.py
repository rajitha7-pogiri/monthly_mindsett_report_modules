from pathlib import Path
import matplotlib.pyplot as plt

from .preprocessing_for_piechart import preprocessing_for_piechart


from .pie_chart import piechart_comparison_design

def generate_piechart(df_meta_with_value, asset_group, 
                      directory_to_savefig = './figures/'):

    df_for_piechart = preprocessing_for_piechart(df_meta_with_value, asset_group=asset_group, pct_level_tobe_others = 0.03)

    # Specify the directory to save figures, if it does not exist, create it
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)

    piechart_comparison_design(df_for_piechart, ncol=1,loc='center right')
    plt.savefig(directory_to_savefig+"consumption_by_assetclass_piechart_mindsett.png",format='png', dpi=200)