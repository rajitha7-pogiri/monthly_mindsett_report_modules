from pathlib import Path
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import matplotlib.text as mpltext


# import matplotlib.transforms as mtransforms
from matplotlib.patches import FancyBboxPatch

import matplotlib.patheffects as path_effects
from matplotlib.patheffects import PathPatchEffect, SimpleLineShadow, Normal

from os import path


assets_folder = path.join(path.dirname(__file__), 'assets/')

cd = {"tomato": '#FF836A',"aquablue": '#6DC2B3',"peach": '#FED6D2',"darkgrey": '#9F9D9C',"potato": '#FEF8C8',
      "cyan": '#B6E4E1',"dimgray":'#696969',"Seafoam":'#87e0cf',"gainsboro":'#DCDCDC'}

def energy_meter_design(ax, consumption_mwh_cur, consumption_mwh_pre,
                        conv_mwh_co2 = 0.233,
                        conv_mwh_pnd = 170,
                        fx = 0.2, # fancy box x-axis value
                        fy = 0.3, # fancy box y-axis value
                        fs  = 0.6, # fancy box scale factor
                        image_folder = assets_folder
                        ):

    ax.set_xlim(0.2, 0.9)
    ax.set_ylim(0.2, 0.9)
    iz  = 0.06 * fs # icon zooming factor

    # add a fancy box as the energy meter outline

    fancybox_width  = fs
    fancybox_height = fs
    fancybox = mpatches.FancyBboxPatch(
                [fx, fy], fancybox_width, fancybox_height, fc="w", ec='k', lw=1.5, ls= 'dotted',
                boxstyle=mpatches.BoxStyle("Round", rounding_size=0.07, pad=0.02))
    ax.add_artist(fancybox)

    # text sub-title 
    text_title = mpltext.Text(x=fx+0.45*fs, y=fy+0.7*fs, text=f'Equivalent$^*$', 
                              va=u'baseline', color='grey', ha=u'right', fontweight='light',fontstyle='italic', fontsize='10')
    ax.add_artist(text_title)

    # text footnote
    text_footnote = mpltext.Text(x=fx+0.5*fs, y=fy+0.05*fs, text=f'* {conv_mwh_co2:1.3f}$t$ CO2e $\Leftrightarrow$ 1MWh $\Leftrightarrow$ £{conv_mwh_pnd:1.1f}', 
                                 va=u'baseline', color='k', ha=u'center', fontsize='9')
    ax.add_artist(text_footnote)

    ## text readings settings
    re_w = 0.80   # reading width
    re_x = 0.127  # reading x-axis value
    re_y = 0.80   # reading y-axis value
    re_c = "k"    # reading colour
    r_fs = "16"   # reading fontsize

    ## reading - energy 
    reading = consumption_mwh_cur
    reading_value = f"{reading:1.1f} MWh"
    # reading - energy - text - monthly total
    rt_x = re_x + 0.15 + 0.03
    rt_y = re_y
    readingtext = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{reading_value}', 
                               va=u'bottom', color=re_c, ha=u'center', fontweight="bold", fontsize='18')

    # reading - energy - text - monthly change
    rt_x = re_x + 0.473
    rt_y = re_y + 0.02

    change_value = (consumption_mwh_cur - consumption_mwh_pre) / consumption_mwh_pre

    if change_value > 0: 
        change_arrow_str = r'${\blacktriangle}$'
    else:
        change_arrow_str = r'$\:\!\triangledown\:\!$'

    change_in_percentage = change_arrow_str + " " + str(int(abs(change_value)*100)) + r"$\;$"+"%"
    text_percentage = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{change_in_percentage}', 
                                   va=u'baseline', color='k', ha=u'left', fontweight="bold", fontsize='18')
    ax.add_artist(text_percentage)

    # horizontal line to separate the different readings
    rl_x = re_x * 0.2       # the x-axis value of the line at the bottom of the reading 
    rl_y = re_y - 0.15        # the y-axis value of the line at the bottom of the reading
    rl_w = re_w * 1.2    # the width value of the line at the bottom of the reading
    horizontal_line = mpatches.Rectangle([fx+rl_x*fs, fy+rl_y*fs], 
                                         rl_w*fs, 0, facecolor="k", edgecolor='k', lw=1, ls= 'dotted')
    ax.add_artist(readingtext)
    ax.add_artist(horizontal_line)


    ## reading - co2
    re_y = 0.48
    reading = consumption_mwh_cur * conv_mwh_co2
    reading_value = f"{reading:1.1f} tons"
    image_name = 'co2.png'

    # reading - co2 - icon
    ri_x = re_x + 0.09  # reading icon x-axis value
    ri_y = re_y + 0.042
    icon = mpimg.imread(image_folder + image_name)
    ibox = OffsetImage(icon, zoom=2*iz)
    readingicon = AnnotationBbox(ibox, (fx+ri_x*fs, fy+ri_y*fs), frameon = False)

    # reading - co2 - text
    rt_x = re_x + 0.342
    rt_y = re_y
    readingtext = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{reading_value}', 
                               va=u'bottom', color=re_c, ha=u'left', fontweight="bold", fontsize=r_fs)

    # horizontal line to separate the different readings
    rl_x = re_x         # the x-axis value of the line at the bottom of the reading 
    rl_y = re_y - 0.07      # the y-axis value of the line at the bottom of the reading
    rl_w = re_w * 0.9   # the width value of the line at the bottom of the reading
    horizontal_line = mpatches.Rectangle([fx+rl_x*fs, fy+rl_y*fs], 
                                         rl_w*fs, 0, facecolor="k", edgecolor='k', lw=1, ls= 'dotted')

    ax.add_artist(readingicon)
    ax.add_artist(readingtext)
    ax.add_artist(horizontal_line)


    ## reading - billing
    re_y = 0.23
    reading = consumption_mwh_cur * conv_mwh_pnd
    reading_value = f"{reading:,.2f}".replace(".", ". ") 
    image_name = 'pound-sterling.png'

    # reading - billing - icon
    ri_x = re_x + 0.09  # reading icon x-axis value
    ri_y = re_y + 0.06
    icon = mpimg.imread(image_folder + image_name)
    ibox = OffsetImage(icon, zoom=1.6*iz)
    readingicon = AnnotationBbox(ibox, (fx+ri_x*fs, fy+ri_y*fs), frameon = False)

    # reading - billing - text
    rt_x = re_x + 0.342
    rt_y = re_y
    readingtext = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{reading_value}', 
                               va=u'bottom', color=re_c, ha=u'left', fontweight="bold", fontsize=r_fs)

    # horizontal line to separate the different readings
    rl_x = re_x          # the x-axis value of the line at the bottom of the reading 
    rl_y = re_y - 0.07        # the y-axis value of the line at the bottom of the reading
    rl_w = re_w * 0.9    # the width value of the line at the bottom of the reading
    horizontal_line = mpatches.Rectangle([fx+rl_x*fs, fy+rl_y*fs], 
                                         rl_w*fs, 0, facecolor="k", edgecolor='k', lw=1, ls= 'dotted')

    ax.add_artist(readingicon)
    ax.add_artist(readingtext)
    ax.add_artist(horizontal_line)


    ## benchmarking design
    re_y = 0.65
    ri_y = re_y + 0.07*fs

    ax.axis('equal')

def benchmarking_design(ax, consumption_mwh_cur, floor_sqm,
                        kwh_per_sqm_good = 10.33,
                        kwh_per_sqm_typical = 14.5,
                        fx = 0.2, # fancy box x-axis value
                        fy = 0.18, # fancy box y-axis value
                        fs = 0.6 # fancy box scale factor
                        ):


        mwh_good = floor_sqm * kwh_per_sqm_good / 1000
        mwh_typical = floor_sqm * kwh_per_sqm_typical / 1000
        
        mwh_btw_good_typical = mwh_typical - mwh_good
        
        key_values_list = [mwh_typical + mwh_btw_good_typical,
                           mwh_good - mwh_btw_good_typical,
                           consumption_mwh_cur + mwh_btw_good_typical/2,
                           consumption_mwh_cur - mwh_btw_good_typical/2]
        
        ticks_max = max(key_values_list)
        ticks_min = min(key_values_list)
        
        ticks_values_list = [ticks_min, mwh_good, mwh_typical, ticks_max]
        ticks_range = ticks_max - ticks_min
        
        ## ruler settings
        ru_x = 0  # the x-axis of benchmarking ruler
        ru_y = 0  # the x-axis of benchmarking ruler
        ru_w = 1  # the width of benchmarking ruler
        ru_h = 0.08  # the height of benchmarking ruler
        
        rp_edgecolor = 'k' # edgecolor of the ruler body parts
        

        # ruler body - part one - good
        rp_x = ru_x         # the x-axis value of this part
        rp_y = ru_y - 0.07      # the y-axis value of this part
        rp_w = ru_w * (ticks_values_list[1]-ticks_values_list[0])/ticks_range   # the width value of this part
        rp_h = ru_h
        rp_c = cd["aquablue"]
        ruler_body_part_one = mpatches.Rectangle([fx+rp_x*fs, fy+rp_y*fs], 
                                             rp_w*fs, rp_h*fs, facecolor=rp_c, edgecolor=rp_edgecolor, lw=1)
        
        rpa_x = rp_x + rp_w/2.0 # ruler body part annotation - x axis
        rpa_y = rp_y  # ruler body part annotation - y axis
        rpa_text = "GOOD"

        ax.annotate(rpa_text, (fx+fs*rpa_x, fx+fs*rpa_y), color='w', weight='bold', 
                    fontsize=8, ha='center', va='center')

        # ruler body - part two - normal
        rp_x = rp_x + rp_w     # the x-axis value of this part
        rp_y = ru_y - 0.07      # the y-axis value of this part
        rp_w = ru_w * (ticks_values_list[2]-ticks_values_list[1])/ticks_range   # the width value of this part
        rp_h = ru_h
        rp_c = cd["potato"]
        ruler_body_part_two = mpatches.Rectangle([fx+rp_x*fs, fy+rp_y*fs], 
                                             rp_w*fs, rp_h*fs, facecolor=rp_c, edgecolor=rp_edgecolor, lw=1)
        
        rpa_x = rp_x + rp_w/2.0 # ruler body part annotation - x axis
        rpa_y = rp_y  # ruler body part annotation - y axis
        rpa_text = "NORM"

        ax.annotate(rpa_text, (fx+fs*rpa_x, fx+fs*rpa_y), color='#9F9D9C', weight='bold', 
                    fontsize=8, ha='center', va='center')

        # ruler body - part three - poor
        rp_x = rp_x + rp_w     # the x-axis value of this part
        rp_y = ru_y - 0.07      # the y-axis value of this part
        rp_w = ru_w * (ticks_values_list[3]-ticks_values_list[2])/ticks_range   # the width value of this part
        rp_h = ru_h
        rp_c = cd["tomato"]
        ruler_body_part_thr = mpatches.Rectangle([fx+rp_x*fs, fy+rp_y*fs], 
                                             rp_w*fs, rp_h*fs, facecolor=rp_c, edgecolor=rp_edgecolor, lw=1)
        
        rpa_x = rp_x + rp_w/2.0 # ruler body part annotation - x axis
        rpa_y = rp_y  # ruler body part annotation - y axis
        rpa_text = "POOR"

        ax.annotate(rpa_text, (fx+fs*rpa_x, fx+fs*rpa_y), color='w', weight='bold', 
                    fontsize=8, ha='center', va='center')

        ax.add_artist(ruler_body_part_one)
        ax.add_artist(ruler_body_part_two)
        ax.add_artist(ruler_body_part_thr)


        # ruler ticks labels
        
        rt_fs = 12  # the fontsize of ruler ticks labels
        rt_c = "grey"  # the font color of ruler ticks labels
        rt_va = u'bottom' 
        rt_ha = u'center' 
        rt_fontweight = "light"
        
        ru_rt_y = -0.18 # ruler ticks y-axis in relation to the ruler y-axis
        
        tick = ticks_values_list[0]
        rt_x = ru_x + (tick-ticks_min)/ticks_range
        rt_y = ru_y + ru_rt_y
        tick_value = f"{tick:1.1f}"
        tick_label_one = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{tick_value}', 
                                  va=rt_va, color=rt_c, ha=rt_ha, fontweight=rt_fontweight, fontsize=rt_fs)

        tick = ticks_values_list[1]
        rt_x = ru_x + (tick-ticks_min)/ticks_range
        rt_y = ru_y + ru_rt_y
        tick_value = f"{tick:1.1f}"
        tick_label_two = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{tick_value}', 
                                  va=rt_va, color=rt_c, ha=rt_ha, fontweight=rt_fontweight, fontsize=rt_fs)

        tick = ticks_values_list[2]
        rt_x = ru_x + (tick-ticks_min)/ticks_range
        rt_y = ru_y + ru_rt_y
        tick_value = f"{tick:1.1f}"
        tick_label_thr = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{tick_value}', 
                                  va=rt_va, color=rt_c, ha=rt_ha, fontweight=rt_fontweight, fontsize=rt_fs)

        tick = ticks_values_list[3]
        rt_x = ru_x + (tick-ticks_min)/ticks_range
        rt_y = ru_y + ru_rt_y
        tick_value = f"{tick:1.1f}"
        tick_label_four = mpltext.Text(x=fx+rt_x*fs, y=fy+rt_y*fs, text=f'{tick_value}', 
                                  va=rt_va, color=rt_c, ha=rt_ha, fontweight=rt_fontweight, fontsize=rt_fs)

        ax.add_artist(tick_label_one)
        ax.add_artist(tick_label_two)
        ax.add_artist(tick_label_thr)
        ax.add_artist(tick_label_four)

        # ruler indicator
        indicator_value = consumption_mwh_cur
        rih_x = ru_x + (indicator_value-ticks_min)/ticks_range # x-axis value of the ruler indicator head
        rih_y = ru_y + 0.084  # y-axis value of the ruler indicator head
        rih_r = 0.045

        indicator_head = mpatches.Circle((fx+(rih_x)*fs, fy+rih_y*fs), rih_r*fs, 
                                         fc="w", color = "w", ec="k", lw=1.3, zorder=10
                                         ) #path_effects=[path_effects.withSimplePatchShadow()]

        rib_x = ru_x + (indicator_value-ticks_min)/ticks_range # x-axis value of the ruler indicator head
        rib_y = ru_y - 0.09  # y-axis value of the ruler indicator head
        rib_w = 0.02
        rib_h = ru_h * 2

        indicator_body = mpatches.Rectangle([fx+(rib_x-rib_w/2)*fs, fy+rib_y*fs], rib_w*fs, rib_h*fs, 
                                            fc="w", ec="k", lw=1.3,  zorder=10) #path_effects=[path_effects.withSimplePatchShadow()]
        ax.add_artist(indicator_body)
        ax.add_artist(indicator_head)
        
        ## title

        tt_x = ru_x + ru_w/2
        tt_y = ru_y - 0.26
        #title = f"BBP Benchmarking (REEB)"
        #tt_c = '#9F9D9C'
        #title_text = mpltext.Text(x=fx+tt_x*fs, y=fy+tt_y*fs, text=f'{title}', 
                                  #va="center", ha="center", color=tt_c, fontweight="normal", fontsize=12) #fontfamily='serif'
        
        #ax.add_artist(title_text)

def energy_meter_with_benchmarking(consumption_mwh_cur, consumption_mwh_pre, floor_size,
                                    size_in_sqm = True,
                                    industry = "office",
                                    period = 30,
                                    conv_mwh_co2 = 0.233,
                                    conv_mwh_pnd = 190,
                                    fx = 0.2, # fancy box x-axis value
                                    fy = 0.3, # fancy box y-axis value
                                    fs  = 0.6, # fancy box scale factor
                                    image_folder = assets_folder,
                                    kwh_per_sqm_good = 10.33,
                                    kwh_per_sqm_typical = 14.5,
                                    directory_to_savefig = './figures/'
                                  ):

    plt.style.use('seaborn-white')
    fig, ax = plt.subplots(figsize=(5, 5.5))

    if size_in_sqm:
        floor_sqm = floor_size
    else:
        floor_sqm = floor_size * 0.0929

    if industry == "office":
        floor_sqm_as_office = floor_sqm
    elif industry == "food service":
        # https://cdn2.hubspot.net/hubfs/5055051/Offers/Energy%20Benchmarking%20Report%20-%20Iota.pdf?utm_campaign=Offer%3A%20Energy%20Benchmarking%20Report&utm_medium=email&_hsmi=72631957&_hsenc=p2ANqtz-8urx_6ejMPQ25rp-u0vAHPq0cmKPTvL18SQTEf22gtrdDV2x7wGnd5kkP40_bx3M5hOWp3tysnbPI4JjWriJEp2fb5o7PzNF5D9VFqQNjYVLVxKtE&utm_content=72631957&utm_source=hs_automation
        floor_sqm_as_office = floor_sqm * 3 #55/15

    floor_sqm_as_office_for_month = floor_sqm_as_office * period / 30 # default days in a month

    
    energy_meter_design(ax, consumption_mwh_cur, consumption_mwh_pre, 
                        conv_mwh_co2=conv_mwh_co2,
                        conv_mwh_pnd=conv_mwh_pnd,
                        fx=fx, fy=fy, fs=fs,
                        image_folder = image_folder)
    benchmarking_design(ax, consumption_mwh_cur, floor_sqm_as_office_for_month,
                        fx=fx, fy=fy-0.12, fs=fs,
                        kwh_per_sqm_good=kwh_per_sqm_good,
                        kwh_per_sqm_typical=kwh_per_sqm_typical
                       )
    ax.set_xlim(0, 1) # shouldn't be modified
    ax.set_ylim(-1, 2)

    plt.axis('off')
    # Specify the directory to save figures, if it does not exist, create it
    Path(directory_to_savefig).mkdir(parents=True, exist_ok=True)
    plt.savefig(directory_to_savefig+"Monthly_total_and_bm_latest.png", format='png', dpi=200,transparent=True, bbox_inches='tight', pad_inches=0)
