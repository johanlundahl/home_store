from flask import Flask, render_template, request, jsonify
from temp_store.model.sensor import Sensor
from temp_store.db import MyDB
from temp_store import db
from temp_store.encoder import Encoder


app = Flask(__name__)
app.json_encoder = Encoder

db = MyDB(db.db_uri)


@app.route('/api', methods=['GET'])
def root():
	return ''

@app.route('/api/sensors', methods=['POST', 'GET'])
def sensors():
	if request.method == 'POST':
		content = request.get_json()
		if Sensor.valid_create(content):
			with db:
				db.add(Sensor.create(content))
			return '', 200
		else:
			return '', 400
	if request.method == 'GET':
		with db:
			sensors = db.sensors()
			return jsonify(sensors)


if __name__ == '__main__':
    app.run(host='0.0.0.0')