from argparse import ArgumentParser
import calendar
import datetime
from datetime import timedelta
from pytils import http
from home_store.app import app, mydb


def sensor_records(name, day):
    with app.app_context():
        return mydb.sensor_history(name, from_time=day, 
            to_time=day+timedelta(days=1))    

def sparse_records(records):
    for hour in range(24):
        by_hour = [x for x in records if x.timestamp.hour == hour]
        if len(by_hour) > 0:
            keep = min(by_hour, key= lambda x: x.timestamp)
            records.remove(keep)
    return records

def remove_records(records):
    with app.app_context():
        for record in records:
            mydb.delete(record)

def get_int_tuple(period):
    year, month = period.split('-')
    return int(year), int(month)

def sparse_day(name, date):
    day = datetime.datetime.strptime(date, '%Y-%m-%d')
    records = sensor_records(name, day)
    records = sparse_records(records)
    remove_records(records)

def sparse_period(name, period):
    print('SpARSE', name, period)
    if len(period) == 7:
        year, month = get_int_tuple(period)
        num_days = calendar.monthrange(year, month)[1]
        for day in range(1, num_days+1):
            sparse_day(name, str(datetime.date(year, month, day)))
    else:
        sparse_day(name, period)
