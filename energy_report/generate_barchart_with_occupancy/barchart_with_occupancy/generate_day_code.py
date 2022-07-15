

def generate_day_code_list(day_code_dict):
    previous_day_month = None
    previous_day_year = None
    day_code_list = []

    for item in day_code_dict:
        weekday_str = day_code_dict[item]
        day_str = "\n"+str(item.day)
        if item.month == previous_day_month:
            month_str = ""
        else:
            month_str = " "+str(item.strftime("%b"))
        previous_day_month = item.month

        if item.year == previous_day_year:
            year_str = ''
        else:
            year_str = " "+str(item.year)
        previous_day_year = item.year

        day_code = weekday_str+day_str+'\n'+month_str+'\n'+year_str

        day_code_list.append(day_code)
        
    return day_code_list


def generate_day_code(df_meta_with_value):
    
    multi_index = df_meta_with_value.groupby(["date", 'day_code']).sum().index

    day_code_dict = dict(multi_index)

    day_code_list = generate_day_code_list(day_code_dict)

    day_code_list.insert(0,"")
    day_code_list.insert(0,"")
    # day_code_list.insert(0,"")
    day_code_list.append("")
    day_code_list.append("")

    return day_code_list