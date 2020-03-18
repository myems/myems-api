## MyEMS API Service

### Introduction
Providing REST API service for MyEMS Web APP, Android APP and iOS APP and/or third parties


### Prerequisites
mysql.connector
gunicorn
falcon
falcon_cors


### Installation


### Run for Testing
```
$ cd feed-rest-api
$ sudo gunicorn -b 0.0.0.0:8080 app:api
```

### API List