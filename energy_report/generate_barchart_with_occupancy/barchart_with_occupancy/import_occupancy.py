import pandas as pd
import psycopg2


def import_occupancy(db, site_name, period_current,
                     table_name = 'building_occupancy',
                     selected_columns = ["date", "occupancy"]):
    
    # organisation can be added later
    
    start_time = period_current.start_time
    end_time = period_current.end_time
    
    selected_columns_str = ", ".join(selected_columns)
    date_clause_str = f"(date between '{start_time}' and '{end_time}')"

    s  = f"""SELECT {selected_columns_str} FROM {table_name} WHERE building='{site_name}' and {date_clause_str}"""

    conn = psycopg2.connect(db.CONNECTION)

    data_cursor = conn.cursor()
    data_cursor.execute(s)
    listTables = data_cursor.fetchall()

    df_occupancy = pd.DataFrame(listTables, columns=selected_columns)

    df_occupancy['month']=pd.to_datetime(df_occupancy.date).dt.month
    df_occupancy['Date']=pd.to_datetime(df_occupancy.date).dt.day
    df_occupancy=df_occupancy.set_index("Date").sort_index()
    df_occupancy_fixed=df_occupancy.drop(columns=['date'])

    df_occupancy_cur =  df_occupancy_fixed # To select particular month
    
    return df_occupancy_cur