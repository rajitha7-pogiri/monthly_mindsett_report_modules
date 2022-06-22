from fpdf import FPDF
from PIL import ImageColor

import colorsys

cd = {"tomato": '#FF836A',"aquablue": '#6DC2B3',"peach": '#FED6D2',"darkgrey": '#9F9D9C',"potato": '#FEF8C8',"cyan": '#B6E4E1'}

assets_folder = path.join(path.dirname(__file__), 'assets/report_template/')

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
        
