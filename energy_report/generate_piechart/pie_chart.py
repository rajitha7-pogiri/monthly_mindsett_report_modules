import pandas as pd # Import pandas
pd.options.mode.chained_assignment = None
import matplotlib.patches as patches
from dateutil.parser import parse
import matplotlib.pyplot as plt


def generate_legend_labels_for_piechart_with_triangle(df_asset_class_monthly_sum_others, # this dataframe is required to have asset class as index and have columns "sub_pct", "sum"
                                            sum_column = "sum",
                                            pct_column = "sub_pct",
                                        space_len_long = 5,
                                        space_len_short = 1,
                                        pct_len = 4,
                                        kwh_len = 8):

    labels = []

    label_space_long = "," + " "*space_len_long 
    label_space_short = "," + " "*space_len_short

    for index, item in df_asset_class_monthly_sum_others.iterrows():

        label_pct_str = str(round(abs(item[pct_column])*100))
        label_pct_pad = ' ' *int((pct_len - len(label_pct_str))*2) + " "*label_pct_str.count('.')
        

        if item["sum"] >= 100: # KWH
            label_kwh_str = f'{item["sum"]/1000:1.1f} MWh'
        else:
            label_kwh_str = f'{item["sum"]:1.1f} KWh'
        label_kwh_pad = ' ' *int((kwh_len - len(label_kwh_str))*2) 
        label_kwh = label_kwh_pad + label_kwh_str

        # print("item[sub_pct]: ", item["sub_pct"])


        if item["sub_pct"] > 0.005: 
            label_arrow_str = r'${\blacktriangle}$'

        elif item["sub_pct"] < -0.005:
            label_arrow_str = r'$\:\!\triangledown\:\!$'

        else:
            label_arrow_str = r'--'
        
        label_arrow_pad = ' '
        label_arrow = label_arrow_pad + label_arrow_str


        label_index = index

        label = label_kwh + label_space_short + label_arrow+ " " +label_pct_str + r"%" + label_space_short + label_pct_pad + label_index

        labels.append(label)
        
    return labels


def piechart_comparison_design(df_asset_class_monthly_sum_others, ncol,loc,
                                sum_column = "sum",
                                pct_column = "sub_pct", 
                                path_for_fig = None):

    fig, ax = plt.subplots(1, 1, figsize=(9, 3.9))

    colors = ['#6DC2B3', '#FF836A', '#FED6D2', '#9F9D9C', '#B6E4E1', '#FEF8C8', '#CFCDCD', '#9DE7BE']
    other_colours = ['k', 'w']

    df_asset_class_monthly_sum_others[sum_column].plot.pie(ax=ax, autopct=lambda p: '{:.0f}%'.format(round(p)) if p > 3 else '', colors=colors,
                                                      textprops={"color": other_colours[0], "fontsize": 13}, pctdistance=0.77,
                                                      wedgeprops={'linewidth': 1, "edgecolor": other_colours[0]}, labels=None)

    df_asset_class_monthly_sum_others[sum_column].plot.pie(ax=ax, colors="k", radius=0.53,
                                                        wedgeprops={'linewidth': 1.5, "edgecolor": other_colours[0]}, labels=None)

    x0, y0, width, height = 1.3, 0, 1, 1 
    ax.legend(labels=generate_legend_labels_for_piechart_with_triangle(df_asset_class_monthly_sum_others, sum_column=sum_column, pct_column=pct_column),
              loc=loc,facecolor='white', edgecolor='w', framealpha=0.5,
            borderaxespad=0,
              bbox_to_anchor=(x0, y0, width, height), fontsize=12,  ncol=ncol, handleheight=1.2, labelspacing=0.6, title=None) # "center right" - charter house,bbox_to_anchor=(1.27, 0, 1, 1) #edgecolor=other_colours[1] #fontsize='large'

    ax.add_patch(
            patches.Rectangle((x0, y0), width, height, color='r',
                            fill=False, transform=ax.transAxes)
        )
    ax.set_ylabel("")

    my_circle = plt.Circle((0, 0), .5, color=other_colours[1], linewidth=4) # edgecolor=other_colours[0], 
    p = plt.gcf()
    p.gca().add_artist(my_circle)

    # sum_cur = df_asset_class_monthly_sum_others.sum()["sum"]/1000
    # sum_pre = df_asset_class_monthly_sum_others.sum()["sum_pre"]/1000
    # sub_pct = ((sum_cur - sum_pre)/sum_pre) * 100

    # text_kwargs = dict(ha='center', va='center', fontsize=14, color='k')
    fig.tight_layout(pad=1.2, rect=[-0.05,0.1,0.72, 0.95]) #rect=[-0.05,0.1,0.72, 0.95]
    if path_for_fig is not None:
        fig.savefig(path_for_fig)
