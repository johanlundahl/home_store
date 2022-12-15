import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytils.http import Filter
from pytils import http
import pytils.logging  # noqa: F401
import logging
from home_store.config import Config
from home_store.models import mydb, Sensor, Panel


DB_FILE_NAME = 'sensors.db'
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DB_FILE_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mydb.init_app(app)


@app.route('/api/v2', methods=['GET'])
def root():
    rules = app.url_map.iter_rules()
    endpoints = [str(rule) for rule in rules if len(rule.arguments) == 0]
    return jsonify(endpoints)


@app.route('/api/v2/status', methods=['GET'])
@http.validate_querystrings(method='GET')
def status():
    with mydb:
        db_count = mydb.size()
        file = 'home_store/{}'.format(DB_FILE_NAME)
        db_size = os.path.getsize(file) if os.path.exists(file) else -1
        oldest = mydb.oldest().timestamp if mydb.oldest() is not None else ''
        newest = mydb.newest().timestamp if mydb.newest() is not None else ''
        result = {'size': db_size, 'count': db_count,
                  'oldest': oldest, 'newest': newest}
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
            result = [{'name': name, 'href': f'/api/sensors/{name}'}
                      for name in sensors]
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
        return jsonify(sensor.to_json())
    return 500


@app.route('/api/v2/sensors/<name>/min-max', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=['date'])
def sensor_high_low_v2(name):
    with mydb:
        high = mydb.sensor_max(name, request.args['date'])
        low = mydb.sensor_min(name, request.args['date'])
        sensor = {'name': name, 'date': request.args['date'],
                  'min': low.to_json(), 'max': high.to_json()}
        return jsonify(sensor)
    return 500


@app.route('/api/v2/sensors/<name>/readings', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=['date', 'timestamp',
                            'page', 'page_size', 'sort'])
# Add hour parameter which can take multiple values, e.g. hour=0,6,12,18
def sensor_history_v2(name):
    args = request.args
    date_args = Filter.args_matching(args, 'date')
    timestamp_args = Filter.args_matching(args, 'timestamp')
    date_filters = [get_arg(args, d, True) for d in date_args]
    date_filters += [get_arg(args, d, False) for d in timestamp_args]

    offset = int(args['page']) if 'page' in args else 0
    limit = int(args['page_size']) if 'page_size' in args else 20
    sort = request.args['sort'] if 'sort' in args else 'desc'

    with mydb:
        date_filters = [a.to_json() for a in date_filters]
        # range(0, 24, 3)

        sensors = mydb.sensor(name, filters=date_filters, offset=offset,
                              limit=limit, sort=sort)
        sensors = [s.to_json() for s in sensors]
        return jsonify(sensors)
    return 500


@app.route('/api/v2/panels', methods=['POST', 'GET'])
@http.validate_querystrings(method='GET')
def panels():
    if request.method == 'POST':
        content = request.get_json()
        if Panel.valid_create(content):
            with mydb:
                panel = mydb.add(Panel.create(content))
                return jsonify(panel.to_json())
        else:
            return 'All required parameters were not received.', 400

    if request.method == 'GET':
        with mydb:
            panels = mydb.panels()
            result = [{'id': x, 'href': f'/api/v2/panels/{x}'}
                      for x in panels]
            return jsonify(result)


@app.route('/api/v2/panels/<id>', methods=['GET'])
@http.validate_querystrings(method='GET', parameters=['date', 'timestamp',
                            'page', 'page_size', 'sort'])
def panel(id):
    # filter options and return all latest...
    args = request.args
    date_args = Filter.args_matching(args, 'date')
    timestamp_args = Filter.args_matching(args, 'timestamp')
    date_filters = [get_arg(args, d, True) for d in date_args]
    date_filters += [get_arg(args, d, False) for d in timestamp_args]

    offset = int(args['page']) if 'page' in args else 0
    limit = int(args['page_size']) if 'page_size' in args else 20
    sort = request.args['sort'] if 'sort' in args else 'desc'

    if request.method == 'GET':
        with mydb:
            panels = mydb.panel(id, filters=date_filters, offset=offset,
                                limit=limit, sort=sort)
            if len(panels) > 0:
                panels = [p.to_json() for p in panels]
                return jsonify(panels)
            else:
                return '', 404


@app.route('/api/v2/panels/<id>/latest', methods=['GET'])
def panel_latest(id):
    if request.method == 'GET':
        with mydb:
            panel = mydb.panel_latest(id)
            if panel is not None:
                return jsonify(panel.to_json())
            else:
                return '', 404


def get_arg(args, arg, ignore_type):
    return Filter.from_arg(arg, args[arg], ignore_type)


def calculate_date_range(filters):
    lower = filters
    return lower


if __name__ == '__main__':
    try:
        cfg = Config.init()
        app.run(host=cfg.server.address, port=cfg.server.port)

    except Exception:
        logging.exception('Application Exception')
