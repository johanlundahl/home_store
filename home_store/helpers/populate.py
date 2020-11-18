import random
from random import randrange
from argparse import ArgumentParser
from datetime import timedelta
import datetime
import calendar
from home_store.app import app, mydb
from home_store.models import Sensor


def add(sensor):
    with app.app_context():
        mydb.session.add(sensor)
        mydb.session.commit()

def create_sensor(name, date_str):
    temp = create_value()
    hum = create_value()
    timestamp = create_timestamp(date_str)
    return Sensor(name, temp, hum, timestamp)

def create_value():
    return round(random.random()*100, 1)

def create_timestamp(date_str):
    time_of_day = timedelta(hours = randrange(24), 
        seconds = randrange(60)*60 + randrange(60))
    day = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return day + time_of_day

def create_for_day(name, date, count):
    for x in range(count):
        s1 = create_sensor(name, date)
        add(s1)

def get_int_tuple(year_month):
    year, month = year_month.split('-')
    return int(year), int(month)

def create_for_period(name, period, count):
    if len(period) == 7:
        year, month = get_int_tuple(period)
        num_days = calendar.monthrange(year, month)[1]
        for day in range(1, num_days+1):
            create_for_day(name, str(datetime.date(year, month, day)), count)
    else:
        create_for_day(name, period, count)
