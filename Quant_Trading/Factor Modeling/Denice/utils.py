from datetime import datetime as dt

## ASSUMES DATE FORMAT IN DD-MM-YYYY
def ConvertDt(dates_as_str:list[str]):
    return [dt.strptime(date_string, "%d-%m-%Y") for date_string in dates_as_str]