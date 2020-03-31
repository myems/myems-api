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

View online: https://app.getpostman.com/run-collection/a34d69ad0cbbfab2840a

View in Postman: import the file MyEMS.postman_collection.json with Postman


[Energy Category](#Energy-Category) | [Energy Item](#Energy-Item)

[Data Source](#Data-Source) | [Point](#Point)

[Tariff](#Tariff) | [Cost Center](#Cost-Center)

[Meter](#Meter) | [Virtual Meter](#Virtual-Meter) | [Offline Meter](#Offline-Meter) 

[Space](#Space) | [Tenant](#Tenant) | [Tenant Type](#Tenant-Type)

[User](#User) | [Privilege](#Privilege) | [Contact](#Contact)

[Timezone](#Timezone)


### Contact
* GET Contact by ID
```bash
$ curl -i -X GET http://BASE_URL/contacts/{id}
```
* GET All Contacts
```bash
$ curl -i -X GET http://BASE_URL/contacts
```
* DELETE Contact by ID
```bash
$ curl -i -X DELETE http://BASE_URL/contacts/{id}
```
* POST Create a New Contact
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"albert", "email":"albert@myems.io", "phone":"+8613888888888", "description":"contact description"}}' http://BASE_URL/contacts
```
* PUT Update a Contact
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"albert", "email":"albert@myems.io", "phone":"+8613888888899", "description":"contact description"}}' http://BASE_URL/contacts/{id}
```

### Cost Center
* GET Cost Center by ID

```bash
$ curl -i -X GET http://BASE_URL/costcenters/{id}
```
Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Cost Center ID                            |
| name          | string    | Cost Center name                          |
| uuid          | string    | Cost Center UUID                          |
| external_id   | string    | Cost Center External ID ( For example, ID in SAP, ERP...) |

* GET all Cost Centers
```bash
$ curl -i -X GET http://BASE_URL/costcenters
```
* DELETE Cost Center by ID
```bash
$ curl -i -X DELETE http://BASE_URL/costcenters/{id}
```
* POST Create New Cost Center
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
* POST Create a Cost Center and Tariff Relation
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"tariff_id":"3"}}' http://BASE_URL/costcenters/{id}/tariffs
```
* DELETE a Cost Center and Tariff Relation by tid
```bash
$ curl -i -X DELETE http://BASE_URL/costcenters/{id}/tariffs/{tid}
```

### Data Source
* GET Data Source by ID

```bash
$ curl -i -X GET http://BASE_URL/datasources/{id}
```
Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Complex ID                                |
| name          | string    | Complex name                              |
| uuid          | string    | Complex UUID                              |
| protocol      | string    | Protocol Type Supported: bacnet-ip, modbus-tcp, s7, opc-ua, control-logix, |
| connection    | json      | Connection data in JSON. BACnet/IP example: {"host":"10.1.2.88"}, Modbus TCP example: {"host":"10.1.2.88", "port":502}, S7 example: {"host":"10.1.2.202", "port":102, "rack": 0, "slot": 2}, ControlLogix example: {"host":"10.1.2.88","port":44818,"processorslot":3} OPC UA example: {"url":"opc.tcp://10.1.2.5:49320/OPCUA/SimulationServer/"} |

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


### Energy Category
* GET an Energy Category by ID

```bash
$ curl -i -X GET http://BASE_URL/energycategories/{id}
```
Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Energy Category ID                        |
| name          | string    | Energy Category name                      |
| uuid          | string    | Energy Category UUID                      |
| unit_of_measure   | string| Unit of measure                           |
| kgce          | string    | KG coal equivalent                        |
| kgco2e        | string    | KG Carbon dioxide equivalent              |


* GET All Energy Categories
```bash
$ curl -i -X GET http://BASE_URL/energycategories
```
* DELETE an Energy Category by ID
```bash
$ curl -i -X DELETE http://BASE_URL/energycategories/{id}
```
* POST Create an Energy Category
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"电","unit_of_measure":"kWh", "kgce":0.1229 , "kgco2e":0.8825}}' http://BASE_URL/energycategories
```
* PUT Update an Energy Category
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"电","unit_of_measure":"kWh", "kgce":0.1329 , "kgco2e":0.9825}}' http://BASE_URL/energycategories/{id}
```


### Energy Item
* GET an Energy Item by ID

```bash
$ curl -i -X GET http://BASE_URL/energyitems/{id}
```
Result in JSON

| Name          | Data Type | Description                           |
|---------------|-----------|---------------------------------------|
| id            | integer   | Energy Item ID                        |
| name          | string    | Energy Item name                      |
| uuid          | string    | Energy Item UUID                      |
| Energy Category ID   | integer | Energy Category ID               |


* GET All Energy Items
```bash
$ curl -i -X GET http://BASE_URL/energyitems
```
* DELETE an Energy Item by ID
```bash
$ curl -i -X DELETE http://BASE_URL/energyitems/{id}
```
* POST Create an Energy Item
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"空调用电","energy_category_id":1}}' http://BASE_URL/energyitems
```
* PUT Update an Energy Item
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"动力用电","energy_category_id":1}}' http://BASE_URL/energyitems/{id}
```

### Meter
* GET Meter by ID

```bash
$ curl -i -X GET http://BASE_URL/meters/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Meter ID                                  |
| name          | string    | Meter name                                |
| uuid          | string    | Meter UUID                                |
| energy_category| Object   | Energy Category Object                    |
| is_counted    | boolean   | Meter is counted in associated unit       |
| max_hourly_value | decimal(18,3)   | Maximum energy consumption per hour|
| energy_item   | Object    | Energy Item Object                        |
| cost_center   | Object    | Cost Center Object                        |
| location      | string    | Meter location                            |
| description   | string    | Meter description                         |

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
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"PM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "cost_center_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/meters
```
* PUT Update a Meter
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"PM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "cost_center_id":1, "location":"floor1", "description":"空调用电"}}' http://BASE_URL/meters/{id}
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

```bash
$ curl -i -X GET http://BASE_URL/offlinemeters/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Offline Meter ID                          |
| name          | string    | Offline Meter name                        |
| uuid          | string    | Offline Meter UUID                        |
| energy_category| Object   | Energy Category Object                    |
| is_counted    | boolean   | Offline Meter is counted in associated unit   |
| max_hourly_value | decimal(18,3)   | Maximum energy consumption per hour|
| energy_item   | Object    | Energy Item Object                        |
| energy_item   | Object    | Cost Center Object                        |
| location      | string    | Offline Meter location                    |
| description   | string    | Offline Meter description                 |

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
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"OfflinePM20", "energy_category_id":1, "max_hourly_value":999.99, "is_counted":true, "energy_item_id":1, "cost_center_id":1, location":"floor1", "description":"空调用电"}}' http://BASE_URL/offlinemeters
```
* PUT Update a Offline Meter
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"OfflinePM20", "energy_category_id":1, "max_hourly_value":9999.99, "is_counted":true, "energy_item_id":1, "cost_center_id":1, location":"floor1", "description":"空调用电"}}' http://BASE_URL/offlinemeters/{id}
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

```bash
$ curl -i -X GET http://BASE_URL/points/{id}
```
Result in JSON

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


### Sensor
* GET a Sensor by ID

```bash
$ curl -i -X GET http://BASE_URL/sensors/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Sensor ID                                 |
| name          | string    | Sensor name                               |
| uuid          | string    | Sensor UUID                               |
| location      | string    | Sensor location                           |
| description   | string    | Sensor description                        |

* GET All Sensors
```bash
$ curl -i -X GET http://BASE_URL/sensors
```
* DELETE a Sensor by ID
```bash
$ curl -i -X DELETE http://BASE_URL/sensors/{id}
```
* POST Create New Sensor
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"Sensor10", "location":"sensor location", "description":"sensor description"}}' http://BASE_URL/sensors
```
* PUT Update a Sensor
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"Sensor10", "location":"sensor location", "description":"sensor description"}}' http://BASE_URL/sensors/{id}
```
* GET All Points associated with Sensor ID
```bash
$ curl -i -X GET http://BASE_URL/sensors/{id}/points
```
* POST Sensor Point Relation
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"point_id":"3"}}' http://BASE_URL/sensors/{id}/points
```
* DELETE Sensor Point Relation
```bash
$ curl -i -X DELETE http://BASE_URL/sensors/{id}/points/{pid}
```


### Space
* GET Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Space ID                                  |
| name          | string    | Space name                                |
| uuid          | string    | Space UUID                                |
| parent_space_id| integer  | Parent Space ID                           |
| area          | decimal(18, 3) | Area                                 |
| timezone      | Object    | Timezone Object                           |
| is_input_counted | boolean | Indicates if the space's energy input is counted for aggregating|                        |
| is_output_counted | boolean | Indicates if the space's energy output is counted for aggregating|                        |
| contact       | Object    | Contact Object                            |
| cost_center   | Object    | Cost Center Object                        |
| location      | string    | Space location                            |
| description   | string    | Space description                         |

* GET All Spaces
```bash
$ curl -i -X GET http://BASE_URL/spaces
```
* DELETE Space by ID
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}
```
* POST Create a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"MyEMSSpace", "parent_space_id":1, "area":999.99, "timezone_id":56, "is_input_counted":true, "is_output_counted":false, "contact_id":1, "cost_center_id":1, "location":"My location", "description":"Space description"}}' http://BASE_URL/spaces
```
* PUT Update a Space
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"MyEMSSpace", "parent_space_id":2, "area":999.99, "timezone_id":56, "is_input_counted":true, "is_output_counted":true, "contact_id":1, "cost_center_id":1, "location":"My location", "description":"Space description"}}' http://BASE_URL/spaces/{id}
```
* GET All Children of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/children
```
* GET All Equipments of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/equipments
```
* POST Bind an Equipment to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"equipment_id":1}}' http://BASE_URL/spaces/{id}/equipments
```
* DELETE an Equipment from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/equipments/{eid}
```
* GET All Meters of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/meters
```
* POST Bind a Meter to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"meter_id":1}}' http://BASE_URL/spaces/{id}/meters
```
* DELETE a Meter from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/meters/{mid}
```
* GET All Offline Meters of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/offlinemeters
```
* POST Bind an Offline Meter to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"offline_meter_id":1}}' http://BASE_URL/spaces/{id}/offlinemeters
```
* DELETE an Offline Meter from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/offlinemeters/{mid}
```
* GET All Points of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/points
```
* POST Bind a Point to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"point_id":1}}' http://BASE_URL/spaces/{id}/points
```
* DELETE a Point from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/points/{pid}
```
* GET All Sensors of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/sensors
```
* POST Bind a Sensor to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"sensor_id":1}}' http://BASE_URL/spaces/{id}/sensors
```
* DELETE a Sensor from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/sensors/{sid}
```
* GET All Tenants of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/tenants
```
* GET All Virtual Meters of Space by ID
```bash
$ curl -i -X GET http://BASE_URL/spaces/{id}/virtualmeters
```
* POST Bind an Virtual Meter to a Space
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"virtual_meter_id":1}}' http://BASE_URL/spaces/{id}/virtualmeters
```
* DELETE an Virtual Meter from Space
```bash
$ curl -i -X DELETE http://BASE_URL/spaces/{id}/virtualmeters/{mid}
```

### Tariff
* GET Tariff by id

```bash
$ curl -i -X GET http://BASE_URL/tariffs/{id}
```
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


### Tenant
* GET Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Tenant ID                                 |
| name          | string    | Tenant name                               |
| uuid          | string    | Tenant UUID                               |
| parent_space_id| integer  | Parent Space ID                           |
| buildings     | string    | Buildings (one or many)                   |
| floors        | string    | Floors (one or many)                      |
| rooms         | string    | Rooms (one or many)                       |
| area          | decimal(18, 3) | Area                                 |
| tenant_type   | Object    | Tenant Type object                        |
| is_key_tenant | boolean   | Indicates if this is a key tenant         |
| lease_number  | string    | Tenant lease number                       |
| lease_start_datetime_utc | float   | Lease start datetime in utc timezone (POSIX timestamp * 1000)  |
| lease_end_datetime_utc   | float   | Lease end datetime in utc timezone (POSIX timestamp * 1000)    |
| is_in_lease   | boolean   | Indicates if this tenant is in lease      |
| contact       | Object    | Contact Object                            |
| cost_center   | Object    | Cost Center Object                        |
| description   | string    | Tenant description                        |

* GET All Tenants
```bash
$ curl -i -X GET http://BASE_URL/tenants
```
* POST Create New Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"Starbucks", "parent_space_id":2, "buildings":"Building #1", "floors":"L1 L2 L3", "rooms":"1201b+2247+3F", "area":418.8, "tenant_type_id":9, "is_key_tenant":true, "lease_number":"6b0da806",  "lease_start_datetime_utc":"2019-12-31T16:00:00", "lease_end_datetime_utc":"2022-12-31T16:00:00", "is_in_lease":true, "contact_id":1, "cost_center_id":1, "description":"my description"}}' http://BASE_URL/tenants
```
* PUT Update a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"Hermes 爱马仕", "parent_space_id":3, "buildings":"Building #1", "floors":"L1 L2 L3 L4 L5", "rooms":"1201b+2247+3F", "area":818.8, "tenant_type_id":9, "is_key_tenant":true, "lease_number":"6b0da806",  "lease_start_datetime_utc":"2019-12-31T16:00:00", "lease_end_datetime_utc":"2022-12-31T16:00:00", "is_in_lease":true, "contact_id":1, "cost_center_id":1, "description":"my description"}}' http://BASE_URL/tenants/{id}
```
* DELETE Tenant by ID
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}
```
* GET All Meters of Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}/meters
```
* POST Bind a Meter to a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"meter_id":1}}' http://BASE_URL/tenants/{id}/meters
```
* DELETE a Meter from Tenant
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}/meters/{mid}
```
* GET All Offline Meters of Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}/offlinemeters
```
* POST Bind an Offline Meter to a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"offline_meter_id":1}}' http://BASE_URL/tenants/{id}/offlinemeters
```
* DELETE an Offline Meter from Tenant
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}/offlinemeters/{mid}
```
* GET All Points of Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}/points
```
* POST Bind a Point to a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"point_id":1}}' http://BASE_URL/tenants/{id}/points
```
* DELETE a Point from Tenant
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}/points/{pid}
```
* GET All Sensors of Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}/sensors
```
* POST Bind a Sensor to a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"sensor_id":1}}' http://BASE_URL/tenants/{id}/sensors
```
* DELETE a Sensor from Tenant
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}/sensors/{sid}
```
* GET All Virtual Meters of Tenant by ID
```bash
$ curl -i -X GET http://BASE_URL/tenants/{id}/virtualmeters
```
* POST Bind an Virtual Meter to a Tenant
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"virtual_meter_id":1}}' http://BASE_URL/tenants/{id}/virtualmeters
```
* DELETE an Virtual Meter from Tenant
```bash
$ curl -i -X DELETE http://BASE_URL/tenants/{id}/virtualmeters/{mid}
```


### Tenant Type
* GET a Tenant Type by ID

```bash
$ curl -i -X GET http://BASE_URL/tenanttypes/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Tenant Type ID                            |
| name          | string    | Tenant Type name                          |
| uuid          | string    | Tenant Type UUID                          |
| description   | string    | Tenant Type description                   |
| simplified_code | string  | Tenant Type simplified code               |

* GET All Tenant Types
```bash
$ curl -i -X GET http://BASE_URL/tenanttypes
```
* POST Create New Tenant Types
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name": "Office", "description":"办公", "simplified_code":"OF"}}' http://BASE_URL/tenanttypes
```
* PUT Update a Tenant Types
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name": "Office1", "description":"办公", "simplified_code":"OF1"}}' http://BASE_URL/tenanttypes/{id}
```
* DELETE a Tenant Types by ID
```bash
$ curl -i -X DELETE http://BASE_URL/tenanttypes/{id}
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
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"albert", "display_name":"Mr. Albert", "email":"albert@myems.io", "is_admin":false, "password":"!MyEMS1"}}' http://BASE_URL/users
```
* PUT User Profile
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"albert", "display_name":"Mr. Albert", "email":"albert@myems.io", "is_admin":false, "privilege_id":1, "password":"!MyEMS1"}}' http://BASE_URL/users/{id}
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

```bash
$ curl -i -X GET http://BASE_URL/virtualmeters/{id}
```
Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Virtual Meter ID                          |
| name          | string    | Virtual Meter name                        |
| uuid          | string    | Virtual Meter UUID                        |
| energy_category| Object   | Energy Category Object                    |
| is_counted    | boolean   | the Virtual Meter is counted in           |
| energy_item   | Object    | Energy Item Object                        |
| cost_center   | Object    | Cost Center Object                        |
| location      | string    | Offline Meter location                    |
| description   | string    | Offline Meter description                 |
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
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"VM21", "energy_category_id":1, "is_counted": true, "energy_item_id":1, "cost_center_id":1, "location":"virtual location", "description":"virtual description", "expression": {"equation":"x1-x2-x3", "variables":[{"name":"x1", "meter_type":"meter", "meter_id":3},{"name":"x2", "meter_type":"meter", "meter_id":4},{"name":"x3", "meter_type":"meter", "meter_id":5}] } }}' http://BASE_URL/virtualmeters
```
* PUT Update a Virtual Meter by ID
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"VM21", "energy_category_id":1, "is_counted": true, "energy_item_id":1, "cost_center_id":1, "location":"virtual location", "description":"virtual description", "expression": {"equation":"x1-x2-x3", "variables":[{"name":"x1", "meter_type":"meter", "meter_id":3},{"name":"x2", "meter_type":"meter", "meter_id":4},{"name":"x3", "meter_type":"meter", "meter_id":5}] } }}' http://BASE_URL/virtualmeters/{id}
```