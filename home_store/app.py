from datetime import datetime
import os
import json
from flask import Flask, render_template, request, jsonify
from pytils.http import Filter
from pytils import log
from home_store import db
from home_store.db import MyDB
from home_store.model.encoder import Encoder
from home_store.model.sensor import Sensor

app = Flask(__name__)
app.json_encoder = Encoder

mydb = MyDB(db.db_uri)

@app.route('/api', methods=['GET'])
def root():
    return ''

@app.route('/api/status', methods=['GET'])
def status():
    with mydb:
        db_count = mydb.size()
        db_size = os.path.getsize(db.db_file)
        oldest = mydb.oldest().timestamp
        newest = mydb.newest().timestamp
        result = {'size': db_size, 'count': db_count, 'oldest': oldest, 'newest': newest}
        return jsonify(result)

@app.route('/api/sensors', methods=['POST', 'GET'])
def sensors():
    if request.method == 'POST':
        content = request.get_json()
        if Sensor.valid_create(content):
            with mydb:
                mydb.add(Sensor.create(content))
            return '', 200
        else:
            return '', 400
    if request.method == 'GET':        
        with mydb:
            sensors = mydb.sensors()
            result = [{'name': name, 'link': '/api/sensors/{}'.format(name)} for name in sensors]
            return jsonify(result)

@app.route('/api/sensors/<name>', methods=['GET'])
def sensor(name):
    if request.method == 'GET':
        date_args = Filter.args_matching(request.args, 'date')
        timestamp_args = Filter.args_matching(request.args, 'timestamp')
                
        date_filters = [Filter.from_arg(date, request.args[date], ignore_type=True) for date in date_args]
        date_filters += [Filter.from_arg(date, request.args[date], ignore_type=False) for date in timestamp_args]
        
        offset = int(request.args['offset']) if 'offset' in request.args else 0 
        limit = int(request.args['limit']) if 'limit' in request.args else 20
        sort = request.args['sort'] if 'sort' in request.args else 'desc'

        #### FIX: filter in query instead of after call, limit do not work this way!!!
        with mydb:
            sensors = mydb.sensor(name, offset=offset, limit=limit, sort=sort)
            sensors2 = mydb.sensor2(name, offset=offset, limit=limit, sort=sort)
            print('SENSOR', len(sensors2))
            for date_filter in date_filters:
                sensors = [s for s in sensors if date_filter.evaluate(s)]
            return jsonify(sensors)
        return 500

@app.route('/api/sensors2/<name>', methods=['GET'])
def sensor2(name):
    if request.method == 'GET':
        date_args = Filter.args_matching(request.args, 'date')
        timestamp_args = Filter.args_matching(request.args, 'timestamp')
                
        date_filters = [Filter.from_arg(date, request.args[date], ignore_type=True) for date in date_args]
        date_filters += [Filter.from_arg(date, request.args[date], ignore_type=False) for date in timestamp_args]
        
        offset = int(request.args['offset']) if 'offset' in request.args else 0 
        limit = int(request.args['limit']) if 'limit' in request.args else 20
        sort = request.args['sort'] if 'sort' in request.args else 'desc'

        #### FIX: filter in query instead of after call, limit do not work this way!!!
        with mydb:
            #sensors = mydb.sensor(name, offset=offset, limit=limit, sort=sort)
            date_filters = [a.to_json() for a in date_filters]
            sensors = mydb.sensor2(name, filters=date_filters, offset=offset, limit=limit, sort=sort)
            #for date_filter in date_filters:
            #    sensors = [s for s in sensors if date_filter.evaluate(s)]
            return jsonify(sensors)
        return 500


@app.route('/api/sensors/<name>/latest', methods=['GET'])
def sensor_latest(name):
    if request.method == 'GET':
        with mydb:
            sensor = mydb.latest_sensor(name)
            return jsonify(sensor)
        return 500

@app.route('/api/sensors/<name>/history', methods=['GET'])
def sensor_history(name):
    if request.method == 'GET':
        from_time = datetime.strptime(request.args['from'], '%Y-%m-%d %H:%M:%S') if 'from' in request.args else datetime.now()-datetime.timedelta(days=1)
        to_time = datetime.strptime(request.args['to'], '%Y-%m-%d %H:%M:%S') if 'to' in request.args else datetime.now()
        resolution = int(request.args['resolution']) if 'resolution' in request.args else 20

        with mydb:
            sensors = mydb.sensor_history(name, from_time=from_time, to_time=to_time)
            sensors = sensors[0::int(len(sensors)/resolution)] if len(sensors) > resolution else sensors
            return jsonify(sensors)
        return 500

if __name__ == '__main__':
    try:
        log.init()
        app.run(host='0.0.0.0')
    except Exception:
        log.exception('Application Exception')
    