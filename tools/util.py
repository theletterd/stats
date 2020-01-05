import datetime
import pytz
pdt = pytz.timezone('US/Pacific')

def convert_kg_to_lbs(kg):
    return kg / 0.454

def convert_metres_to_miles(metres):
    if not metres:
        return 0
    return metres / 1609.0


def get_dates_between(start_date, end_date):
    assert start_date <= end_date

    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date = start_date + datetime.timedelta(days=1)

    return dates

def datetime_today_pacific():
    return datetime.datetime.utcnow().astimezone(pdt)

def today_pacific():
    return datetime_today_pacific().date()
