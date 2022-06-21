
import pandas as pd

def resample_by_channels(df_source, reading_interval_in_mins=10):
    
    df_source_grouped = df_source.groupby(["nid", "channel", pd.Grouper(freq=f'{reading_interval_in_mins}Min')]).mean()
    df_source_pivot = df_source_grouped.unstack(level=[0,1])
    df_source_pivot_resampled = df_source_pivot.resample(f"{reading_interval_in_mins}Min").mean().ffill()
    df_source_filled = df_source_pivot_resampled.stack(level=[1,2]).reset_index()
    df_source_filled['channel']= df_source_filled['channel'].astype(str)
    
    return df_source_filled