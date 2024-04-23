from datetime import datetime, timedelta

import pandas as pd
from pandas_market_calendars import get_calendar

asx_calendar = get_calendar('ASX')
nyse_calendar = get_calendar('XNYS')

def next_week_expiry(date: datetime, weekday):
    days_until_weekday = (weekday_mapping[weekday.upper()] - date.weekday()) % 7
    next_expire_date = date + timedelta(days=days_until_weekday)

    return next_expire_date

def next_month_expiry(date: datetime, weekday, ref_week_num=3):

    first_day_next_month = datetime(date.year if date.month != 12 else date.year + 1, (date.month % 12) + 1, 1)
    days_to_add = (weekday_mapping[weekday.upper()] - first_day_next_month.weekday() + 7) % 7 + (ref_week_num - 1) * 7
    next_expire_date = first_day_next_month + timedelta(days=days_to_add)

    return next_expire_date

def next_date_us(date, weekday, week_month, au_us):
    calendar = nyse_calendar if au_us else asx_calendar

    if week_month:
        next_us_date = next_week_expiry(date, weekday)
    else:
        next_us_date = next_month_expiry(date, weekday)

    if calendar.valid_days(start_date=next_us_date, end_date=next_us_date).size > 0:
        next_trading_day = next_us_date
    else:
        next_trading_day = calendar.valid_days(start_date=next_us_date, end_date=next_us_date + pd.Timedelta(days=10))[0]

    return next_trading_day.strftime('%Y-%m-%d')



weekday_mapping = {
    'MON': 0,
    'TUE': 1,
    'WED': 2,
    'THU': 3,
    'FRI': 4,
    'SAT': 5,
    'SUN': 6
}