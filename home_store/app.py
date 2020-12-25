from datetime import datetime
import os
import json
from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
from pytils.http import Filter
from pytils import log, http
from pytils import config
from home_store.models import mydb, Sensor
from home_store.models import Encoder

DB_FILE_NAME = 'sensors.db'
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DB_FILE_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder = Encoder
mydb.init_app(app)

@app.route('/api/v2', methods=['GET'])
def root():
    endpoints = [str(rule) for rule in app.url_map.iter_rules() if len(rule.arguments) == 0]
    return jsonify(endpoints)

@app.route('/api/v2/status', methods=['GET'])
@http.validate_querystrings(method='GET')
def status():
    with mydb:
        db_count = mydb.size()
        db_size = os.path.getsize('home_store/{}'.format(DB_FILE_NAME))
        oldest = mydb.oldest().timestamp if mydb.oldest() is not None else '' 
        newest = mydb.newest().timestamp if mydb.newest() is not None else ''
        result = {'size': db_size, 'count': db_count, 'oldest': oldest, 'newest': newest}
        return jsonify(result)

@app.route('/api/v2/sensors', methods=['POST', 'GET'])
@http.validate_querystrings(method='GET')
def sensors():
    if request.method == 'POST':
        content = request.get_json()
        if Sensor.valid_create(content):
            with mydb:
                sensor = mydb.add(Sensor.create(content))
                return jsonify(sensor.to_json())
        else:
            return 'All required parameters were not received.', 400
    if request.method == 'GET':        
        with mydb:
            sensors = mydb.sensors()
            result = [{'name': name, 'href': '/api/sensors/{}'.format(name)} for name in sensors]
            return jsonify(result)


@app.route('/api/v2/sensors/<name>', methods=['GET'])
@http.validate_querystrings(method='GET')
def sensor_v2(name):
    with mydb:
        sensor = mydb.latest_sensor(name)
        if sensor is not None:
            return jsonify(sensor.to_json_summary())
        else:
            return '', 404

@app.route('/api/v2/sensors/<name>/latest', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=[])
def sensor_latest_v2(name):
    with mydb:
        sensor = mydb.latest_sensor(name)
        return jsonify(sensor)
    return 500

@app.route('/api/v2/sensors/<name>/min-max', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=['date'])
def sensor_high_low_v2(name):
    with mydb:
        high = mydb.sensor_max(name, request.args['date'])
        low = mydb.sensor_min(name, request.args['date'])
        sensor = {'name': name, 'date': request.args['date'], 'min': low, 'max': high}
        return jsonify(sensor)
    return 500

@app.route('/api/v2/sensors/<name>/readings', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=['date', 'timestamp', 'page', 'page_size', 'sort'])
def sensor_history_v2(name):
    date_args = Filter.args_matching(request.args, 'date')
    timestamp_args = Filter.args_matching(request.args, 'timestamp')
            
    date_filters = [Filter.from_arg(date, request.args[date], ignore_type=True) for date in date_args]
    date_filters += [Filter.from_arg(date, request.args[date], ignore_type=False) for date in timestamp_args]
    
    offset = int(request.args['page']) if 'page' in request.args else 0 
    limit = int(request.args['page_size']) if 'page_size' in request.args else 20
    sort = request.args['sort'] if 'sort' in request.args else 'desc'

    with mydb:
        date_filters = [a.to_json() for a in date_filters]
        sensors = mydb.sensor(name, filters=date_filters, offset=offset, limit=limit, sort=sort)
        return jsonify(sensors)
    return 500


if __name__ == '__main__':
    try:
        log.init()
        cfg = config.init()
        app.run(host=cfg.server.address, port=cfg.server.port)
    except Exception:
        log.exception('Application Exception')
    