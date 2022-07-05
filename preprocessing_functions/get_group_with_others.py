

def get_group_with_others(row, asset_group):
    if row["gt_4pct"]:
        return row[asset_group]
    else:
        return "Others"