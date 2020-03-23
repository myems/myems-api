import falcon
import json
import mysql.connector
import config
import uuid
import datetime


class DataSourceCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, protocol, connection "
                 " FROM tbl_data_sources "
                 " ORDER BY id")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "protocol": row[3], "connection": row[4]}
                result.append(meta_result)

        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.ERROR', description=ex)

        new_values = json.loads(raw_json, encoding='utf-8')

        if 'name' not in new_values['data'].keys() or len(new_values['data']['name']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_NAME')

        if 'protocol' not in new_values['data'].keys() \
                or new_values['data']['protocol'] not in \
                ('modbus-tcp', 'modbus-rtu', 'bacnet-ip', 's7', 'profibus', 'profinet', 'opc-ua', 'lora', 'simulation',
                 'control-logix'):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_PROTOCOL.')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        add_values = (" INSERT INTO tbl_data_sources (name, uuid, protocol, connection) "
                      " VALUES (%s, %s, %s, %s) ")
        cursor.execute(add_values, (new_values['data']['name'],
                                    str(uuid.uuid4()),
                                    new_values['data']['protocol'],
                                    new_values['data']['connection']))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/datasources/' + str(new_id)


class DataSourceItem:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, protocol, connection "
                 " FROM tbl_data_sources "
                 " WHERE id =%s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()
        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        result = {"id": row[0], "name": row[1], "uuid": row[2], "protocol": row[3], "connection": row[4]}
        resp.body = json.dumps(result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        # check if this data source is being used by any meters
        cursor.execute(" SELECT DISTINCT(m.name) "
                       " FROM tbl_meters m, tbl_meters_points mp, tbl_points p, tbl_data_sources ds "
                       " WHERE m.id = mp.meter_id AND mp.point_id = p.id AND p.data_source_id = ds.id "
                       "       AND ds.id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_meter = cursor.fetchone()
        if row_meter is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_DATA_SOURCE_IS_BEING_USED_BY_A_METER' + row_meter[0])

        cursor.execute(" DELETE FROM tbl_points WHERE data_source_id = %s ", (id_,))
        cursor.execute(" DELETE FROM tbl_data_sources WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()
        resp.status = falcon.HTTP_204

    @staticmethod
    def on_put(req, resp, id_):
        """Handles PUT requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'API.ERROR', ex)

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        new_values = json.loads(raw_json, encoding='utf-8')

        if 'name' not in new_values['data'].keys() or len(new_values['data']['name']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_NAME')

        if 'protocol' not in new_values['data'].keys() \
                or new_values['data']['protocol'] not in \
                ('modbus-tcp', 'modbus-rtu', 'bacnet-ip', 's7', 'profibus', 'profinet', 'opc-ua', 'lora', 'simulation',
                 'control-logix'):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_PROTOCOL.')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        update_row = (" UPDATE tbl_data_sources "
                      " SET name = %s, protocol = %s, connection = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (new_values['data']['name'],
                                    new_values['data']['protocol'],
                                    new_values['data']['connection'],
                                    id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_200


class DataSourcePointCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        result = list()
        # Get points of the data source
        query_point = (" SELECT id, name, data_source_id, object_type, "
                       "        units, low_limit, hi_limit, is_trend, address, ratio "
                       " FROM tbl_points "
                       " WHERE data_source_id = %s "
                       " ORDER BY name ")
        cursor.execute(query_point, (id_,))
        rows_point = cursor.fetchall()

        if rows_point is not None and len(rows_point) > 0:
            for row in rows_point:
                meta_result = {"id": row[0],
                               "name": row[1],
                               "data_source_id": row[2],
                               "object_type": row[3],
                               "units": row[4],
                               "low_limit": row[5],
                               "hi_limit": row[6],
                               "is_trend": True if row[7] else False,
                               "address": row[8],
                               "ratio": row[9]}
                result.append(meta_result)

        cursor.close()
        cnx.disconnect()
        resp.body = json.dumps(result)


class DataSourceStatusCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        # Get the data source
        query_point = (" SELECT id, name, connection, last_seen_datetime_utc "
                       " FROM tbl_data_sources "
                       " ORDER BY name ")
        cursor.execute(query_point, )
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')
        rows_point = cursor.fetchall()

        result = dict()
        if rows_point is not None and len(rows_point) > 0:
            for row in rows_point:
                id = row[0]
                name = row[1]
                connection = row[2]
                last_time = row[3]
                now_time = datetime.datetime.utcnow().replace(second=0, microsecond=0, tzinfo=None)
                status = "offline"

                if "host" in connection:
                    ip = json.loads(connection)["host"]
                else:
                    continue

                if (now_time - last_time).total_seconds() > 5 * 60:
                    status = "online"

                result[name] = {
                    "ip": ip,
                    "status": status
                }
        cursor.close()
        cnx.disconnect()
        resp.body = json.dumps(result)
