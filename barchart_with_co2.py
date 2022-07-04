
import pandas as pd # Import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def co2_design(df_grouped_working_hours_period_reset_index):
    
    ylim_max = plt.ylim()[1]
    
    for i, (h,v) in enumerate(zip(df_grouped_working_hours_period_reset_index.max(axis=1), df_grouped_working_hours_period_reset_index.sum(axis=1))):
        plt.text(i,ylim_max*0.86, str(round(v*0.233,1)) + r"$\,t$", 
        horizontalalignment='center',
        color='darkgrey',
        fontweight="bold",fontsize=10)
    
        plt.text(i,ylim_max*0.77, r"$CO_{2}e$", 
        horizontalalignment='center',
        color='darkgrey',
        fontsize=8)

def co2_barchart_design(df_grouped_working_hours_period_unstacked, ylim=None, top_hours=True, ylim_pad_ratio = 0.5):
 
        plt.style.use('seaborn-white')
        fig,ax = plt.subplots(1, 1, figsize=(3,3.1))        
        ax_l = ax
        colors_ax_l = ['#6DC2B3']
        
        # config ylim
        if ylim is None:
            ylim_min = 0
            ylim_max = df_grouped_working_hours_period_unstacked.sum(axis=1).max()*(ylim_pad_ratio+1)
            ylim = (ylim_min,ylim_max)
         
        ax.set_ylim(ylim)
        

        #top_hours = True # False: in-hours, True: out-of-hours
        bot_hours = not top_hours

        hours_labels = {True: "Out Of Hours", False: "In Hours"}
        hours_colors = {True: "w", False: colors_ax_l[0]}
        
        bar_edgecolour = ['k','w']
        bar_fillcolour = ['k','w']

        x_ticks_labels = df_grouped_working_hours_period_unstacked.index.strftime("%b %y").tolist()   
        x_ticks_labels.insert(0,"")
        x_ticks_labels.append("")

        df_grouped_working_hours_period_reset_index = df_grouped_working_hours_period_unstacked.reset_index(drop=True)
        

        # bottom bar legend label
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[bot_hours].fillna(0)-2/1000, 
                 width=0.5, lw=1.2, color=hours_colors[bot_hours], 
                 edgecolor=bar_edgecolour[0], label=hours_labels[bot_hours])
        # top bar legend label
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[top_hours].fillna(0), 
                 width=0.5, lw=1.2, color=hours_colors[top_hours],edgecolor=bar_edgecolour[0], 
                 bottom=df_grouped_working_hours_period_reset_index[bot_hours].fillna(0)-5/1000, label=hours_labels[top_hours])
        #edge of bar
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[top_hours].fillna(0)+0.2+df_grouped_working_hours_period_reset_index[bot_hours].fillna(0), 
                 width=0.7, lw=1.5, edgecolor=bar_edgecolour[0], color=bar_fillcolour[1])


        ax_l.set_ylabel("Total consumption (MWh)", labelpad= 13,fontsize ='11')
        ax_l.yaxis.tick_right()
        ax_l.yaxis.set_label_position("right")

        # bottom bar inner part
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[bot_hours].fillna(0)-7/1000, 
                 width=0.5, lw=0, color= hours_colors[bot_hours], 
                 edgecolor=bar_edgecolour[1])
        
        #top bar inner part
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[top_hours].fillna(0), 
                 width=0.5, lw=0, color= hours_colors[top_hours], 
                 edgecolor=bar_edgecolour[1], bottom=df_grouped_working_hours_period_reset_index[bot_hours].fillna(0)-7/1000)

        # black bar for separation
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[top_hours]*0, 
                 width=0.5, lw=1, edgecolor=bar_edgecolour[0], 
                 color= bar_fillcolour[0], bottom=df_grouped_working_hours_period_reset_index[bot_hours].fillna(0)-7/1000) 

        # white bar at the bottom
        ax_l.bar(df_grouped_working_hours_period_reset_index.index, df_grouped_working_hours_period_reset_index[top_hours]*0+0.2, 
                 width=0.6, lw=0, edgecolor=bar_edgecolour[1], color= bar_fillcolour[1]) 
        
        
        ax_l.xaxis.set_major_locator(ticker.MultipleLocator(1))
        #ax_l.legend(loc='upper left', bbox_to_anchor=(0.025, 0.97))


        # fixing yticks with matplotlib.ticker "FixedLocator"
        ticks_loc = ax_l.get_xticks().tolist()
        ax_l.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))

        print(ax.get_xticks())
        ax.set_xticklabels(x_ticks_labels,fontsize ='10')
        plt.xticks(rotation=45)
        ax.tick_params(axis='both', which='major', pad=8, length=5, labelsize="10")
        top_index = df_grouped_working_hours_period_reset_index.index.min() - 0.9
        bot_index = df_grouped_working_hours_period_reset_index.index.max() + 0.9
        ax.set_xlim([top_index, bot_index])
        
        
        #C02 insertion
        co2_design(df_grouped_working_hours_period_reset_index.sort_index())


        ax_l.legend(loc='upper left', bbox_to_anchor=(-0,1.02,1,0.2),fontsize=9,ncol=2)
        fig.tight_layout()