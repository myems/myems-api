# MyEMS API Service

## Introduction
Providing REST API service for MyEMS Web APP, Android APP and iOS APP and/or third parties


## Prerequisites
simplejson
mysql.connector
falcon
falcon_cors
gunicorn


## Installation

* Install simplejson
```
$ cd ~/tools
$ git clone https://github.com/simplejson/simplejson.git
$ cd simplejson
$ sudo python3 setup.py install 
```

* Install MySQL Connector

  refer to http://dev.mysql.com/downloads/connector/python/
  
  select Platform:Platform Independent
  
  and select 'Platform Independent (Architecture Independent), Compressed TAR Archive Python' in list
```
  $ cd ~/tools
  $ wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-8.0.18.tar.gz
  $ tar xzf mysql-connector-python-8.0.18.tar.gz
  $ cd ~/tools/mysql-connector-python-8.0.18
  $ sudo python3 setup.py install
```

* Install Falcon,

  if you are behind proxy, use --proxy parameter

  Refer to 
  
  https://falconframework.org/

  https://github.com/lwcolton/falcon-cors

  https://github.com/yohanboniface/falcon-multipart
```
  $ mkdir ~/tools/falcon && cd ~/tools/falcon
  $ pip3 download cython falcon falcon-cors falcon-multipart
  $ export LC_ALL="en_US.UTF-8"
  $ export LC_CTYPE="en_US.UTF-8"
  $ sudo dpkg-reconfigure locales
  $ sudo pip3 install --upgrade --no-index --find-links ~/tools/falcon cython falcon falcon-cors falcon-multipart
```

* Install gunicorn, refer to http://gunicorn.org
```
  $ mkdir ~/tools/gunicorn && cd ~/tools/gunicorn
  $ pip3 download gunicorn
  $ sudo pip3 install --no-index --find-links ~/tools/gunicorn gunicorn
```

* Install gunicorn service for myems-api:
```
  $ cd ~/myems-api
  $ sudo cp -R ~/myems-api /myems-api
```
  Check and change the config file if necessary:
```
  $ sudo nano /myems-api/config.py
```
   Change the listening port (8080 as an example) in gunicorn.socket:
```
   $ sudo nano /myems-api/gunicorn.socket
ListenStream=0.0.0.0:8080
    $ sudo ufw allow 8080
```
   Setup systemd configure files:
```
   $ sudo cp /myems-api/gunicorn.service /lib/systemd/system/
   $ sudo cp /myems-api/gunicorn.socket /lib/systemd/system/
   $ sudo cp /myems-api/gunicorn.conf /usr/lib/tmpfiles.d/
```
   Next enable the services so they autostart at boot:
```
   $ sudo systemctl enable gunicorn.service
   $ sudo systemctl enable gunicorn.socket
```

## Run for debugging and testing
```
$ cd myems-api
$ sudo gunicorn -b 127.0.0.1:8080 app:api
```

## API List
[Data Source](#Data-Source) | [Point](#Point)

[Tariff](#Tariff) | [Cost Center](#Cost-Center)

[Meter](#Meter) | [Virtual Meter](#Virtual-Meter) | [Offline Meter](#Offline-Meter) 

[User](#User) | [Privilege](#Privilege)




### Cost Center
* GET Cost Center by ID

Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Cost Center ID                            |
| name          | string    | Cost Center name                          |
| uuid          | string    | Cost Center UUID                          |
| external_id   | string    | Cost Center External ID ( For example, ID in SAP, ERP...) |

```bash
$ curl -i -X GET http://BASE_URL/costcenters/{id}
```
* GET all Cost Centers
```bash
$ curl -i -X GET http://BASE_URL/costcenters
```
* DELETE Cost Center by ID
```bash
$ curl -i -X DELETE http://BASE_URL/costcenters/{id}
```
* POST Create a Cost Center
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"动力中心", "external_id":"21829198980001"}}' http://BASE_URL/costcenters
```
* PUT Update a Cost Center
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"动力中心2", "external_id":"21829198980002"}}' http://BASE_URL/costcenters/{id}
```
* GET All Tariffs associated with Cost Center ID
```bash
$ curl -i -X GET http://BASE_URL/costcenters/{id}/tariffs
```
* POST a Cost Center and Tariff Relation
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"tariff_id":"3"}}' http://BASE_URL/costcenters/{id}/tariffs
```
* DELETE a Cost Center and Tariff Relation
```bash
$ curl -i -X DELETE http://BASE_URL/costcenters/{id}/tariffs/{pid}
```

### Data Source
* GET Data Source by ID

Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Complex ID                                |
| name          | string    | Complex name                              |
| uuid          | string    | Complex UUID                              |
| protocol      | string    | Protocol Type Supported: bacnet-ip, modbus-tcp, s7, opc-ua, control-logix, |
| connection    | json      | Connection data in JSON. BACnet/IP example: {"host":"10.1.2.88"}, Modbus TCP example: {"host":"10.1.2.88", "port":502}, S7 example: {"host":"10.1.2.202", "port":102, "rack": 0, "slot": 2}, ControlLogix example: {"host":"10.1.2.88","port":44818,"processorslot":3} OPC UA example: {"url":"opc.tcp://10.1.2.5:49320/OPCUA/SimulationServer/"} |

```bash
$ curl -i -X GET http://BASE_URL/datasources/{id}
```
* GET all Data Sources
```bash
$ curl -i -X GET http://BASE_URL/datasources
```
* DELETE Data Source by ID
```bash
$ curl -i -X DELETE http://BASE_URL/datasources/{id}
```
* POST Data Source
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"Modbus1", "protocol":"modbus-tcp", "connection":"{\"host\":\"10.1.2.88\", \"port\":502}"}}' http://BASE_URL/datasources
```
* PUT Data Source
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"Modbus1", "protocol":"modbus-tcp", "connection":"{\"host\":\"10.1.2.99\", \"port\":502}"}}' http://BASE_URL/datasources/{id}
```
* GET all points of the Data Source by ID
```bash
$ curl -i -X GET http://BASE_URL/datasources/{id}/points
```


### Meter
* GET Meter by ID

Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Meter ID                                  |
| name          | string    | Meter name                                |
| uuid          | string    | Meter UUID                                |
| energy_category| Object   | Energy Category Object                    |
| is_counted    | boolean   | Meter is counted in associated unit       |
| max_hourly_value | decimal(18,3)   | Maximum energy consumption per hour|
| energy_item   | Object   | Energy Item Object                         |
| location      | string    | Meter location                            |
| description   | string    | Meter description                         |

```bash
$ curl -i -X GET http://BASE_URL/meters/{id}
```
* GET All Meters
```bash
$ curl -i -X GET http://BASE_URL/meters
```
* DELETE Meter by ID
```bash
$ curl -i -X DELETE http://BASE_URL/meters/{id}
```
* POST Create a Meter
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"PM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/meters
```
* PUT Update a Meter
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"PM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/meters/{id}
```
* GET All Points associated with Meter ID
```bash
$ curl -i -X GET http://BASE_URL/meters/{id}/points
```
* POST Meter Point Relation
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"point_id":"3"}}' http://BASE_URL/meters/{id}/points
```
* DELETE Meter Point Relation
```bash
$ curl -i -X DELETE http://BASE_URL/meters/{id}/points/{pid}
```


### Offline Meter
* GET Offline Meter by ID

Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Offline Meter ID                          |
| name          | string    | Offline Meter name                        |
| uuid          | string    | Offline Meter UUID                        |
| energy_category| Object   | Energy Category Object                    |
| is_counted    | boolean   | Offline Meter is counted in associated unit   |
| max_hourly_value | decimal(18,3)   | Maximum energy consumption per hour|
| energy_item   | Object   | Energy Item Object                         |
| location      | string    | Offline Meter location                    |
| description   | string    | Offline Meter description                 |

```bash
$ curl -i -X GET http://BASE_URL/offlinemeters/{id}
```
* GET All Offline Meters
```bash
$ curl -i -X GET http://BASE_URL/offlinemeters
```
* DELETE Offline Meter by ID
```bash
$ curl -i -X DELETE http://BASE_URL/offlinemeters/{id}
```
* POST Create a Offline Meter
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"OfflinePM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/offlinemeters
```
* PUT Update a Offline Meter
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"OfflinePM20", "energy_category_id":1, "max_hourly_value":9999.99, "is_counted":true, "energy_item_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/offlinemeters/{id}
```


### Privilege
* GET Privilege by ID
```bash
$ curl -i -X GET http://BASE_URL/privileges/{id}
```
* GET All Privileges
```bash
$ curl -i -X GET http://BASE_URL/privileges
```
* DELETE Privilege by ID
```bash
$ curl -i -X DELETE http://BASE_URL/privileges/{id}
```
* POST New Privilege
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"superusers","data":"{\"spaces\":[1,2,3,5]}"}}' http://BASE_URL/privileges
```
* PUT Privilege
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"superusers", "data":"{\"spaces\":[1, 3]}"}}' http://BASE_URL/privileges/{id}
```



### Point

* GET Point by ID

Response Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Point ID                                  |
| name          | string    | Point name                                |
| data_source_id| integer   | Data Source ID                            |
| object_type   | string    | Object Type ('ENERGY_VALUE', 'ANALOG_VALUE, 'BINARY_VALUE')   |
| units         | string    | Units of Measure                          |
| low_limit     | float     | Low Limit of the Point Value              |
| hi_limit      | float     | High Limit of the Point Value             |
| is_trend      | boolean   | The Point Value is Recorded as Trend      |
| address       | json      | Address structure varied by protocol      |
|               |           | Modbus TCP Structure                      |
| ├slave_id     | integer   | Slave ID                                  |
| ├function_code| integer   | Modbus functions:READ_COILS = 1, READ_DISCRETE_INPUTS = 2, READ_HOLDING_REGISTERS = 3, READ_INPUT_REGISTERS = 4    |
| ├offset       | integer   | Offset                                    |
| ├number_of_registers  | integer   | Number of Registers               |
| └format       | string    | Data Format. see below introductions      |
|               |           | ControlLogix Structure                    |
| ├data_type    | string    | 'REAL', 'DINT', 'STRING'                  |
| └tag          | string    | Tag Name                                  |
|               |           | BACnet/IP Structure                       |
| ├object_type  | string    | BACnet Object Type ('analogValue', 'analogInput', 'analogOutput', 'binaryValue', 'binaryInput', 'binaryOutput')|
| ├object_id    | integer   | BACnet Object Instance Number             |
| ├property_name| string    | BACnet Property Name ('presentValue')     |
| └property_array_index| integer/null    | BACnet Property Array Index or None of Object Type is not Array   |


```bash
$ curl -i -X GET http://BASE_URL/points/{id}
```
* GET all Points
```bash
$ curl -i -X GET http://BASE_URL/points
```
* DELETE Point by ID
```bash
$ curl -i -X DELETE http://BASE_URL/points/{id}
```
* POST Point
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"ModbusPoint1", "data_source_id":1, "object_type": "ENERGY_VALUE", "units":"kWh", "low_limit":0, "hi_limit":999999999, "is_trend":true, "address":"{\"slave_id\":1, \"function_code\":3, \"offset\":1, \"number_of_registers\":2, \"data_format\":\"float\"}"}}' http://BASE_URL/points
```
* PUT Point
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"ModbusPoint1", "data_source_id":1, "object_type": "ENERGY_VALUE", "units":"kWh", "low_limit":0, "hi_limit":999999999, "is_trend":true, "address":"{\"slave_id\":1, \"function_code\":3, \"offset\":1, \"number_of_registers\":2, \"data_format\":\"float\"}"}}' http://BASE_URL/points/{id}
```


### Tariff
* GET Tariff by id

Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Tariff ID                                 |
| name          | string    | Tariff name                               |
| uuid          | string    | Tariff UUID                               |
| unit_of_price | string    | Unit of Price                             |
| valid_from    | float     | Valid From (POSIX timestamp * 1000)       |
| valid_through | float     | Valid Through (POSIX timestamp * 1000)    |
| tariff_type   | string    | Tariff type (timeofuse or block)          |
| timeofuse[]   | json array| Time Of Use items                         |
| ├             | integer   | array index                               |
|  ├ start_time_of_day  | string    | Start time of day                 |
|  ├ end_time_of_day    | string    | End time of day                   |
|  ├ peak_type  | string    | Peak type: toppeak,onpeak,midpeak,offpeak |
|  └ price      | decimal   | Price                                     |
| block[]       | json array| Block items                               |
| ├             | integer   | array index                               |
|  ├ start_amount | decimal | Start amount                              |
|  ├ end_amount | decimal   | End amount                                |
|  └ price      | decimal   | Price                                     |

```bash
$ curl -i -X GET http://BASE_URL/tariffs/{id}
```
* GET All Tariffs
```bash
$ curl -i -X GET http://BASE_URL/tariffs
```
* DELETE Tariff by ID
```bash
$ curl -i -X DELETE http://BASE_URL/tariffs/{id}
```
* POST Create a Tariff
To POST a block tariff:
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"阶梯电价","energy_category_id":1, "tariff_type":"block", "unit_of_price":"元/千瓦时", "valid_from":"2020-01-01T00:00:00", "valid_through":"2021-01-01T00:00:00", "block":[{"start_amount":"0", "end_amount":"10000", "price":"0.567"}, {"start_amount":"10000", "end_amount":"30000", "price":"0.678"}, {"start_amount":"30000", "end_amount":"100000", "price":"0.789"}]}}' http://BASE_URL/tariffs
```
To POST a time of use tariff:
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"2020分时电价1-6","energy_category_id":1, "tariff_type":"timeofuse", "unit_of_price":"元/千瓦时", "valid_from":"2020-01-01T00:00:00", "valid_through":"2020-07-01T00:00:00", "timeofuse":[{"start_time_of_day":"00:00:00", "end_time_of_day":"05:59:59", "peak_type":"offpeak", "price":0.345}, {"start_time_of_day":"06:00:00", "end_time_of_day":"07:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"08:00:00", "end_time_of_day":"10:59:59", "peak_type":"onpeak", "price":1.159}, {"start_time_of_day":"11:00:00", "end_time_of_day":"17:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"18:00:00", "end_time_of_day":"20:59:59", "peak_type":"onpeak", "price":1.159}, {"start_time_of_day":"21:00:00", "end_time_of_day":"21:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"22:00:00", "end_time_of_day":"23:59:59", "peak_type":"offpeak", "price":0.345}]}}' http://BASE_URL/tariffs
```

* PUT Update a Tariff
To update a block tariff:
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"阶梯电价","energy_category_id":1, "tariff_type":"block", "unit_of_price":"元/千瓦时", "valid_from":"2020-01-01T00:00:00", "valid_through":"2021-01-01T00:00:00", "block":[{"start_amount":"0", "end_amount":"20000", "price":"0.567"}, {"start_amount":"20000", "end_amount":"30000", "price":"0.678"}, {"start_amount":"30000", "end_amount":"100000", "price":"0.789"}]}}' http://BASE_URL/tariffs/{id}
```
To update a time of use tariff:
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"2020分时电价1-6","energy_category_id":1, "tariff_type":"timeofuse", "unit_of_price":"元/千瓦时", "valid_from":"2020-01-01T00:00:00", "valid_through":"2020-07-01T00:00:00", "timeofuse":[{"start_time_of_day":"00:00:00", "end_time_of_day":"05:59:59", "peak_type":"offpeak", "price":0.456}, {"start_time_of_day":"06:00:00", "end_time_of_day":"07:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"08:00:00", "end_time_of_day":"10:59:59", "peak_type":"onpeak", "price":1.159}, {"start_time_of_day":"11:00:00", "end_time_of_day":"17:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"18:00:00", "end_time_of_day":"20:59:59", "peak_type":"onpeak", "price":1.159}, {"start_time_of_day":"21:00:00", "end_time_of_day":"21:59:59", "peak_type":"midpeak", "price":0.708}, {"start_time_of_day":"22:00:00", "end_time_of_day":"23:59:59", "peak_type":"offpeak", "price":0.345}]}}' http://BASE_URL/tariffs/{id}
```


### Timezone
* GET a Timezone by ID
```bash
$ curl -i -X GET http://BASE_URL/timezones/{id}
```
* GET all Timezones
```bash
$ curl -i -X GET http://BASE_URL/timezones
```
* PUT Update a Timezone by ID
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"Hawaiian Standard Time","description":"(GMT-10:00) Hawaii", "utc_offset":"-10:00"}}' http://BASE_URL/timezones/{id}
```

### User
* GET User by ID
```bash
$ curl -i -X GET http://BASE_URL/users/{id}
```
* GET All Users
```bash
$ curl -i -X GET http://BASE_URL/users
```
* DELETE User by id
```bash
$ curl -i -X DELETE http://BASE_URL/users/{id}
```
* POST New User
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"johnson", "display_name":"约翰逊", "email":"johnson@myems.io", "is_admin":true, password":"Thi$Pa$$w0rd"}}' http://BASE_URL/users
```
* PUT User Profile
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"johnson", "display_name":"约翰逊", "is_admin":true, "email":"johnson@myems.io"}}' http://BASE_URL/users/{id}
```
* PUT User Login
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"username":"johnson", "password":"!Password1"}}' http://BASE_URL/users/login
```
* PUT User Logout
```bash
$ curl -i -H "Content-Type: application/json" -X PUT --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/logout
```
* PUT User change password
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"password":"NewPassword1"}}' --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/changepassword
```
* PUT User reset any user's password called by administrator
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"johnson","password":"NewPassword1"}}' --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/resetpassword
```


### Virtual Meter
* GET a Virtual Meter by ID

Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Virtual Meter ID                          |
| name          | string    | Virtual Meter name                        |
| uuid          | string    | Virtual Meter UUID                        |
| energy_category   | json  | Energy Category                           |
| ├ id          | integer   | Energy Category ID                        |
| ├ name        | string    | Energy Category name                      |
| ├ uuid        | string    | Energy Category UUID                      |
| ├ unit_of_measure | string| Unit of measure                           |
| ├ kgce        | string    | KG coal equivalent                        |
| └ kgco2e      | string    | KG Carbon dioxide equivalent              |
| is_counted    | boolean   | the Virtual Meter is counted in           |
| expression    | json      | Expression                                |
|  ├ id         | integer   | Expression ID                             |
|  ├ uuid       | string    | Expression UUID                           |
|  ├ equation   | string    | Expression Equation                       |
|  └ variables[]| json array| Expression Variables                      |
|  ├            | integer   | array index                               |
|   ├ id        | integer   | Variable ID                               |
|   ├ name      | string    | Variable Name                             |
|   ├ meter_type| string    | Meter Type ('meter', 'offline_meter', 'virtual_meter' |
|   ├ meter_name| string    | Meter Name                                |

```bash
$ curl -i -X GET http://BASE_URL/virtualmeters/{id}
```
* GET All Virtual Meters
```bash
$ curl -i -X GET http://BASE_URL/virtualmeters
```
* DELETE a Virtual Meter by ID
```bash
$ curl -i -X DELETE http://BASE_URL/virtualmeters/{id}
```
* POST Create New Virtual Meter
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"VM20", "energy_category_id":1, "is_counted": true, "expression": {"equation":"x1+x2-x3", "variables":[{"name":"x1", "meter_type":"meter", "meter_id":1},{"name":"x2", "meter_type":"meter", "meter_id":2},{"name":"x3", "meter_type":"meter", "meter_id":3}]}}}' http://BASE_URL/virtualmeters
```
* PUT Update a Virtual Meter by ID
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"VM20", "energy_category_id":1, "is_counted": true, "expression": {"equation":"x1+x2-x3", "variables":[{"name":"x1", "meter_type":"meter", "meter_id":1},{"name":"x2", "meter_type":"meter", "meter_id":2},{"name":"x3", "meter_type":"meter", "meter_id":3}]}}}' http://BASE_URL/virtualmeters/{id}
```