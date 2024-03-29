[![lint](https://github.com/johanlundahl/home_store/actions/workflows/lint.yml/badge.svg)](https://github.com/johanlundahl/home_store/actions/workflows/lint.yml)
[![Test](https://github.com/johanlundahl/home_store/actions/workflows/test.yml/badge.svg)](https://github.com/johanlundahl/home_store/actions/workflows/test.yml)
[![Coverage](https://coveralls.io/repos/github/johanlundahl/home_store/badge.svg?branch=master)](https://coveralls.io/github/johanlundahl/home_store?branch=master)

# Home Store
This project stores sensor reading values to a database. Other components can interact with this component through REST endpoints.

This project is suitable to run on a Raspberry Pi and is intended to use with [Home Monitor](http://github.com/johanlundahl/home_monitor), [Temp Sensor](http://github.com/johanlundahl/temp_sensor), [Home Eye](http://github.com/johanlundahl/home_eye) and [Mosquitto MQTT Broker](https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/).

## Installation guide

### Set up the application
Clone this git repo

```
$ git clone https://github.com/johanlundahl/home_store
```

Requires python 3.9 or above. Install required python modules and create the database

```
$ make init
``` 

### Running
Run the application using
```
$ make run
```
This will also create the required config file `home_store/app.yaml` if it doesn't already exist. To make the application start automatically at reboot run the following command
```
$ make autostart
```

### Logging
Application events are logged to the application log file and can be viewed through
```
$ make logging
```

### Database functionality
Use the cmdtool to setup, clean or drop the database. It can also help you simulate database entries for testing. Se the complete list of functionality by entering
```
$ python3 -m home_store.cmdtool -h
``` 


## How to use the application
The application exposes http endpoint to interact with. The web application runs on port 5000 by default and has the endpoints listed below.

The following endpoints are exposed by the application:
* [Endpoints](#endpoints)
* [Status](#status)
* Sensors
    * [List sensors](#list-sensors)
    * [Add sensor value](#add-sensor-value)
    * [Get sensor values](#get-sensor-values)
    * [Get latest sensor value](#get-latest-sensor-value)
    * [Get sensor history](#get-sensor-history)
* Panels
    * [Get panels](#get-panels)
    * [Add panel](#add-panel)
    * [Get panel values](#get-panel-values)
    * [Get latest panel values](#get-latest-panel-values)


### Endpoints
Lists all endpoint of the application:
```
GET /api/v2 HTTP/1.1
```

Example request:
```
GET /api/v2 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

Example response:
``` json
[
    "/api/v2",
    "/api/v2/status",
    "/api/v2/sensors",
    "/api/v2/panels"
]
``` 

### Status
Get the status of the application database:
```
GET /api/v2/status HTTP/1.1
```

Example request:
```
GET /api/v2/sensors HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

Example response:
``` json
{
    "count": 294067,
    "newest": "2020-10-27 20:45:45",
    "oldest": "2020-05-02 21:54:08",
    "size": 35516416
}
```

Where the parameters are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `count`       | int           | Number of records in the database. |
| `newest`      | string        | Timestamp of the newest sensor value in the database. |
| `oldest`      | string        | Timestamp of the oldest sensor value in the database. |
| `size`        | int           | The file size of the database in bytes. |

Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Called with unsupported querystring parameter.   |


### List sensors
Use the following to get a list of all sensors:
```
GET /api/v2/sensors HTTP/1.1
```

Example request:
```
GET /api/v2/sensors HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

Example response:
``` json
[
    {
        "href": "/api/v2/sensors/basement",
        "name": "basement"
    },
    {
        "href": "/api/v2/sensors/garage",
        "name": "garage"
    }
]
```

Where the parameters are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `href`        | string        | Link to the sensor endpoint.  |
| `name`        | string        | Name of the sensor. |

Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Called with unsupported querystring parameter.   |


### Add sensor value
Use the following to add a new sensor value:
```
POST /api/v2/sensors HTTP/1.1
```

Example request:
```
POST /api/v2/sensors HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```
```json
{
    "name": "basement",
    "temperature": 25,
    "humidity": 57,
    "timestamp": "2019-12-27 11:14:03"
}
```
Where the parameters are described as:

| Parameter     | Type          | Required? | Description   |
| ------------- | ------------- | -----     | ---           |
| `name`        | string        | required  | Name of the sensor to add a value for. |
| `temperature` | int           | required  | Temperature sensor value. |
| `humidity`    | int           | required  | Humidity sensor value. |
| `timestamp`   | string        | required  | Timestamp of when the sensor values are generated. |


Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Any of the required parameters are missing.   |


### Get sensor values
Use the following to get sensor values for a sensor:
```
GET /api/v2/sensors/<name> HTTP/1.1
```
By default the 20 latest sensor values are returned, i.e. the same as `offset=0&limit=20`.

| Parameter     | Type          | Required? | Description   |
| ------------- | ------------- | -----     | ---           |
| `date`        | string        | optional  | Will filter the result to include values from the given date in the format `2019-12-27`. |
| `limit`       | int           | optional  | Use together with offset to paginate the results. |
| `offset`      | int           | optional  | Use together with limit to paginate the results. |
| `sort`        | enum          | optional  | Order the result ascending or descending based on timestamp with possible values of `asc`or `desc.` |
| `timestamp`   | int           | optional  | Filters the result to include values that matches the given datetime in the format `2019-12-27 18:05:22`. |

Both the `date` and the `timestamp` attributes can have an operator added to it. The valid operators are `qe`, `gt`, `ge`, `lt`, `te`. 

Example request:
```
GET /api/v2/sensors/basement?date[gt]=2019-12-26 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
``` 

Example response:
``` json
[
    {
        "date": "2019-12-27",
        "humidity": 52.0,
        "id": 3,
        "name": "basement",
        "temperature": 20.0,
        "timestamp": "2019-12-27 11:11:03"
    },
    {
        "date": "2019-12-27",
        "humidity": 53.0,
        "id": 2,
        "name": "basement",
        "temperature": 19.0,
        "timestamp": "2019-12-27 11:10:03"
    }
]
```

Where the parameters in the response are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `date`        | string        | The date of when the sensor value was measured.  |
| `humidity`    | real          | The measured humidity in %. |
| `id`          | int           | The unique id of the sensor record. |
| `name`        | string        | Name of the sensor. |
| `temperature` | real          | The measured temperature in degrees Celsius. |
| `timestamp`   | string        | The date and time of when the sensor value was measured. |


Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Any of the querystring parameters are not valid.  |


### Get latest sensor value
Use the following to get the latest sensor value for <name> as per its datetime attribute:
```
GET /api/v2/sensors/<name>/latest HTTP/1.1
```

Example request:
```
GET /api/v2/sensors/basement/latest HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

Example response:
``` json
{
    "date": "2020-10-27",
    "humidity": 56.8,
    "id": 493455,
    "name": "basement",
    "temperature": 18.8,
    "timestamp": "2020-10-27 21:04:43"
}
```

Where the parameters in the response are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `date`        | string        | The date of when the sensor value was measured.  |
| `humidity`    | real          | The measured humidity in %. |
| `id`          | int           | The unique id of the sensor record. |
| `name`        | string        | Name of the sensor. |
| `temperature` | real          | The measured temperature in degrees Celsius. |
| `timestamp`   | string        | The date and time of when the sensor value was measured. |

Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Any of the querystring parameters are not valid.  |


### Get sensor history
This endpoint will return historical sensor values. Use the `to` and `from` attributes to specify the time period. 
```
GET /api/v2/sensors/<name>/history HTTP/1.1 
```

| Parameter     | Type          | Required? | Description   |
| ------------- | ------------- | -----     | ---           |
| `from`        | string        | optional  | Start time in the format `2020-02-01 23:15:30`. |
| `to`          | string        | optional  | End time in the format `2020-02-05 12:30:00`. |
| `resolution`  | int           | optional  | Reduces the number of sensor values to the specified value. The resulting values are scattered over the given date interval. |


### Get panels
Lists all panels.
```
GET /api/v2/panels HTTP/1.1 
```

Example response:
``` json
[
    {
        "href": "/api/v2/panels/123456",
        "id":123456
    },
    {
        "href": "/api/v2/panels/123457",
        "id":123457
    }
]

```

### Add panel
Use to add a new panel value:
```
POST /api/v2/panels HTTP/1.1
```

Example request:
```
POST /api/v2/panels HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```
```json
{
    "name": "panel 1.2.3",
    "id": 123456,
    "energy": 57,
    "alarm_state": true,
    "efficiency": 75
}
```
Where the parameters are described as:

| Parameter     | Type          | Required? | Description   |
| ------------- | ------------- | -----     | ---           |
| `name`        | string        | required  | Name of the panel to add a value for. |
| `id`          | int           | required  | The id of the panel. |
| `energy`      | int           | required  | Energy produced by the panel in Wh. |
| `alarm_state` | boolean       | required  | Whether the panel is in alarm state or not. |
| `efficiency`  | int           | required  | The production level in % compared to the best producing panel. |

Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Any of the required parameters are missing.   |

### Get panel values
List values of a panel:
```
POST /api/v2/panels/<id> HTTP/1.1
```    
By default the 20 latest values are returned, i.e. the same as `offset=0&limit=20`.

| Parameter     | Type          | Required? | Description   |
| ------------- | ------------- | -----     | ---           |
| `date`        | string        | optional  | Will filter the result to include values from the given date in the format `2019-12-27`. |
| `limit`       | int           | optional  | Use together with offset to paginate the results. |
| `offset`      | int           | optional  | Use together with limit to paginate the results. |
| `sort`        | enum          | optional  | Order the result ascending or descending based on timestamp with possible values of `asc`or `desc.` |
| `timestamp`   | int           | optional  | Filters the result to include values that matches the given datetime in the format `2019-12-27 18:05:22`. |

Both the `date` and the `timestamp` attributes can have an operator added to it. The valid operators are `qe`, `gt`, `ge`, `lt`, `te`. 

Example request:
```
GET /api/v2/panels/123456?date[gt]=2019-12-26 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
``` 

Example response:
``` json
[
    {
        "alarm_state":false,
        "efficiency":51.0,
        "energy":30.0,
        "name":"panel 1.2.4",
        "panel_id":123456,
        "timestamp":"2022-12-13 19:55:34"
    },
    {
        "alarm_state":false,
        "efficiency":31.0,
        "energy":12.0,
        "name":"panel 1.2.4",
        "panel_id":123456,
        "timestamp":"2022-12-13 19:55:17"
    }
]
```

Where the parameters in the response are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `alarm_state` | boolean       | Whether the panel is in alarm state or not.  |
| `efficiency`  | real          | The production level in % compared to the best producing panel. |
| `energy`      | real          | The amount of produced energy of the panel. |
| `name`        | string        | Name of the panel. |
| `panel_id`    | int           | The id of the panel. |
| `timestamp`   | string        | The date and time of when the value was measured. |


Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 400           | Any of the querystring parameters are not valid.  |

### Get latest panel values
Get the latest panel value for <id> as per its datetime attribute:
```
GET /api/v2/panels/<id>/latest HTTP/1.1
```

Example request:
```
GET /api/v2/panels/123456/latest HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

Example response:
``` json
{
    "alarm_state": false,
    "efficiency": 51.0,
    "energy": 30.0,
    "name": "panel 1.2.4",
    "panel_id": 123456,
    "timestamp": "2022-12-13 19:55:34"
}
```

Where the parameters in the response are described as:

| Parameter     | Type          | Description   |
| ------------- | ------------- | ---           |
| `alarm_state` | boolean       | Whether the panel is in alarm state or not.  |
| `efficiency`  | real          | The production level in % compared to the best producing panel. |
| `energy`      | real          | The amount of produced energy of the panel. |
| `name`        | string        | Name of the panel. |
| `panel_id`    | int           | The id of the panel. |
| `timestamp`   | string        | The date and time of when the value was measured. |

Possible errors:

| Error code    | Description   |
| ------------- | -----------   |
| 404           | The panel was not found.  |



