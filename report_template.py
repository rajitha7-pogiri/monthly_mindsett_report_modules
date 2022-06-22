from fpdf import FPDF
from PIL import ImageColor
import os
from datetime import date, timedelta

import colorsys

cd = {"tomato": '#FF836A',"aquablue": '#6DC2B3',"peach": '#FED6D2',"darkgrey": '#9F9D9C',"potato": '#FEF8C8',"cyan": '#B6E4E1'}

assets_folder = os.path.join(os.path.dirname(__file__), 'assets/report_template/')
figures_folder = os.path.join(os.getcwd(), 'figures/')

class PDF(FPDF):

    def header(self):
        #Logo
        self.image(assets_folder+'LetterHead - header - Mindsett.png', 0, 0, self.w)
        #Fontsize and type
        self.set_font('Arial', 'B', 15)
        self.image(assets_folder+"mindsett_logo_white_transparent.png", 15, 15, 45)
        
    def footer(self):
        #Logo
        footer_height = 32
        img_path = assets_folder+'LetterHead - Footer - Mindsett.png'
        footer_width = 210
        self.image(img_path, 0, self.h-footer_height, footer_width)
        self.set_font('Arial', 'B', 15)
        
        self.set_y(self.h-footer_height + 5)
        self.set_x(20)
        self.set_font('Arial', "I", 8)
        color_rgb = ImageColor.getcolor(cd["darkgrey"], "RGB")
        color_hsv = colorsys.rgb_to_hsv(*color_rgb)
        color_rgb_changed = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1], color_hsv[2])
        self.set_text_color(*color_rgb_changed)
        #self.cell(pdf.w - 30, 10, '**BBP benchmarking (REEB) ', 0, 0, 'B')
        
    def write_multicell_with_styles(self, max_width, cell_height, text_list):
        # Source:https://stackoverflow.com/questions/60736940/how-to-make-inline-bold-text-using-pyfpdf#
        startx = self.get_x()
        self.set_font('Arial', '', 12)

        #loop through differenct sections in different styles
        for text_part in text_list:
            #check and set style
            try:
                current_style = text_part['style']
                self.set_font('Arial', current_style, 12)
            except KeyError:
                self.set_font('Arial', '', 12)

            #loop through words and write them down
            space_width = self.get_string_width(' ')
            for word in text_part['text'].split(' '):
                current_pos = self.get_x()
                word_width = self.get_string_width(word)
                #check for newline
                if (current_pos + word_width) > (startx + max_width):
                    #return 
                    self.set_y(self.get_y() + cell_height)
                    self.set_x(startx)
                self.cell(word_width, 5, word)
                #add a space
                self.set_x(self.get_x() + space_width)
        

def generate_report(site_name, statements_list=None, organisation=None, report_file_name='Mindsett_Apr_CharterHouse_v.1.pdf'):

    pdf = PDF()
    pdf.add_page()

    pdf.image(assets_folder+'Screenshot_by_date.png', 0.3, 70, 8)
    pdf.image(assets_folder+'Screenshot_by_asset.png', 0.3, 70+65, 8)
    pdf.image(assets_folder+'Screenshot_insights.png', 0.3, 70+130, 8)
    pdf.set_font('Arial', "B", 28)
    # Line break
    pdf.ln(17)

    color_rgb = ImageColor.getcolor(cd["aquablue"], "RGB")
    color_hsv = colorsys.rgb_to_hsv(*color_rgb)
    color_rgb_changed = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1]*1.2, color_hsv[2]*0.85)
    pdf.set_text_color(*color_rgb_changed)

    pdf.cell(pdf.w - 30, 10, 'Energy Consumption', 0, 0, 'R')
    pdf.set_font('Arial', "I", 16)
    # Line break
    pdf.ln(11)

    color_rgb = ImageColor.getcolor(cd["darkgrey"], "RGB")
    color_hsv = colorsys.rgb_to_hsv(*color_rgb)
    color_rgb_changed = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1], color_hsv[2])
    pdf.set_text_color(*color_rgb_changed)

    # generate the month with year
    # to be improved for ad_hoc use
    today = date.today()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    
    if organisation is None:
        pdf.cell(pdf.w - 30, 10, f'{site_name} - {lastMonth.strftime("%B %Y")} ', 0, 0, 'R')
    else:
        pdf.cell(pdf.w - 30, 10, f'{organisation} - {site_name} - {lastMonth.strftime("%B %Y")} ', 0, 0, 'R')

    pdf.image(figures_folder+'consumption_by_assetclass_piechart_mindsett.png', 16, 55+69, 144)
    pdf.image(figures_folder+'Total_consumption_barchart_with_Co2.png', 142, 55+72, 57)

    pdf.image(figures_folder+'Monthly_total_and_bm.png', 14.5, 48+9, 65-7)


    pdf.ln(151) #Contol on paragraphs 
    pdf.set_x(29)
    pdf.image(figures_folder+'daily_consumption_barchart_with_occupancy_mar_with_pattern_MWh.png',71, 61, 131)


    # pdf.set_x(20)
    # pdf.set_font('Arial', 'I', 12)
    # pdf.set_text_color(0,0,0)
    # pdf.multi_cell(pdf.w - 30, 10, 'Review on Previous Points: \n')

    # text_list_ac = [{'text': '- Even though AC consumption decreased by 11%, still'},
    #              {'style':'B', 'text': 'first floor AC'},
    #              {'text':'was working out of hours during first week of April (1st,2nd,4th), later in the second week it worked for four consecutive days (7th,8th,9th,10th) and also on 20th April. '}]

    # #text_list_km = [{'text': '- As occupancy increased by 30% there is expected increase in'},
    #              #{'style':'B', 'text': 'car charging. '}]

    # text_list_im = [{'text': '- The percentage of out of hours consumption slightly decreased compared to previous month. '}]


    # text_list  = text_list_ac + text_list_im
    # pdf.set_x(29)
    # pdf.write_multicell_with_styles(pdf.w-40,6,text_list)

    pdf.ln(5)
    pdf.set_x(20)
    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(0,0,0)
    pdf.multi_cell(pdf.w - 50, 10, 'Automated Observations: \n')

    text_list = []

    for statement in statements_list:

        statement_text =  [{'text': '- '+statement+' '}]
        text_list += statement_text

    pdf.set_x(29)
    pdf.write_multicell_with_styles(pdf.w-50,6,text_list)

    pdf.output(report_file_name,'F')