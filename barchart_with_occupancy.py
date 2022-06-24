import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import matplotlib.ticker as ticker
import psycopg2
from datetime import date

def import_occupancy(db, site_name, month_current=None,
                     table_name = 'building_occupancy',
                     selected_columns = ["date", "occupancy"]):
    
    # organisation can be added later
    
    if month_current is None:#
        today = date.today()
        month_current = int(today.strftime("%m")) - 1
    
    selected_columns_str = ", ".join(selected_columns)

    s  = f"""SELECT {selected_columns_str} FROM {table_name} WHERE building='{site_name}'"""

    conn = psycopg2.connect(db.CONNECTION)

    data_cursor = conn.cursor()
    data_cursor.execute(s)
    listTables = data_cursor.fetchall()

    df_occupancy = pd.DataFrame(listTables, columns=selected_columns)

    df_occupancy['month']=pd.to_datetime(df_occupancy.date).dt.month
    df_occupancy['Date']=pd.to_datetime(df_occupancy.date).dt.day
    df_occupancy=df_occupancy.set_index("Date").sort_index()
    df_occupancy_fixed=df_occupancy.drop(columns=['date'])

    df_occupancy_cur = df_occupancy_fixed.loc[df_occupancy_fixed['month'] == month_current] # To select particular month
    
    return df_occupancy_cur


def generate_day_code(df_meta_with_value):
    
    multi_index = df_meta_with_value.groupby(["day_of_month", 'day_code']).sum().index

    day_code_dict = dict(multi_index)

    day_code_list = [str(item)+"\n"+day_code_dict[item] for item in day_code_dict]

    day_code_list.insert(0,"")
    day_code_list.insert(0,"")
    # day_code_list.insert(0,"")
    day_code_list.append("")
    day_code_list.append("")

    return day_code_list

def energy_and_occupancy_barchart_design(df_pivot_working_hours,
                                         day_code_list,
                                         tick_range_e=None,
                                         fs = (8, 3.5), # (8, 3.5) -- Charter house and academy
                                         top_hours = True, # False: in-hours, True: out-of-hours
                                         bar_color = '#6DC2B3',
                                         path_for_fig = None,
                                         tick_range_o= None,
                                         df_occupancy_cur= None):

        df_pivot_working_hours[False].fillna(0)
        
        if tick_range_e is None:
            tick_range_e = df_pivot_working_hours.sum(axis=1).max()*1.4

        white_padding_below_bar = tick_range_e/100
        white_padding_below_bar_for_legend = white_padding_below_bar/3

        df_pivot_working_hours.reset_index(drop=True, inplace=True)

        fig, ax = plt.subplots(1, 1, figsize=fs)

        plt.style.use('seaborn-white')# set ggplot style
        ax_l = ax
        colors_ax_l = [bar_color]


        ax_l.set_ylabel("Energy Consumption (MWh)", labelpad=10,fontsize ='12')
        ax_l.set_ylim([0,tick_range_e])
        ax_l.set_yticks(np.arange(0, tick_range_e, 0.1))
        ax_l.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

        if df_occupancy_cur is not None:

            df_occupancy_cur.reset_index(drop=True, inplace=True)

            # the right y axis
            ax_r = ax_l.twinx() # instantiate a second axes that shares the same x-axis
            ax_r.set_ylabel("People Registered", labelpad=10, fontsize ='12')
            ax_r.set_ylim(tick_range_o)
            ax_r.plot(df_occupancy_cur['occupancy'], color= 'k', lw=0.6, ls='dashed', marker=".", ms=6, mec="k", label='Occupancy')
            ax_r.legend(loc='upper right', bbox_to_anchor=(0.97, 0.98))

        bot_hours = not top_hours

        hours_labels = {True: "Out Of Hours", False: "In Hours"}
        hours_colors = {True: "w", False: colors_ax_l[0]}

        bar_edgecolour = ['k','w']
        bar_fillcolour = ['k','w']


        # bottom bar legend label
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[bot_hours].fillna(0)-white_padding_below_bar_for_legend,
                 width=0.5, lw=1.2, color=hours_colors[bot_hours],
                 edgecolor=bar_edgecolour[0], label=hours_labels[bot_hours])
        # top bar legend label
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[top_hours].fillna(0),
                 width=0.5, lw=1.2, color=hours_colors[top_hours],
                 edgecolor=bar_edgecolour[0], bottom=df_pivot_working_hours[bot_hours].fillna(0)-white_padding_below_bar_for_legend, label=hours_labels[top_hours])
        # edge of bar
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[top_hours].fillna(0)+df_pivot_working_hours[bot_hours].fillna(0),
                 width=0.7, lw=1.3, edgecolor=bar_edgecolour[0], color=bar_fillcolour[1])


        # bottom bar inner part
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[bot_hours].fillna(0)-white_padding_below_bar,
                 width=0.4, lw=0, color= hours_colors[bot_hours], edgecolor=bar_edgecolour[1])
        # top bar inner part
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[top_hours].fillna(0),
                 width=0.4, lw=0, color= hours_colors[top_hours],
                 edgecolor=bar_edgecolour[1], bottom=df_pivot_working_hours[bot_hours].fillna(0)-white_padding_below_bar)
        # black bar for separation
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[top_hours]*0,
                 width=0.4, lw=1, edgecolor=bar_edgecolour[0], color= bar_fillcolour[0],
                 bottom=df_pivot_working_hours[bot_hours].fillna(0)-white_padding_below_bar)
        # white bar at the bottom
        ax_l.bar(df_pivot_working_hours.index, df_pivot_working_hours[top_hours]*0+white_padding_below_bar,
                 width=0.4, lw=0, edgecolor=bar_edgecolour[1], color= bar_fillcolour[1])

        ax_l.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax_l.legend(loc='upper left', bbox_to_anchor=(0.025, 0.97))


        # fixing yticks with matplotlib.ticker "FixedLocator"
        ticks_loc = ax_l.get_xticks().tolist()
        ax_l.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))

        ax_l.set_xticklabels(day_code_list)
        ax_l.tick_params(axis='x', which='major', pad=8)
        top_index = df_pivot_working_hours.index.min() - 2
        bot_index = df_pivot_working_hours.index.max() + 2
        ax.set_xlim([top_index, bot_index])
        fig.tight_layout()
        if path_for_fig is not None:
            fig.savefig(path_for_fig)
