import falcon
import simplejson as json
import mysql.connector
import config


class PointCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)

        query = (" SELECT id, name, uuid "
                 " FROM tbl_data_sources ")
        cursor.execute(query)
        rows_data_sources = cursor.fetchall()

        data_source_dict = dict()
        if rows_data_sources is not None and len(rows_data_sources) > 0:
            for row in rows_data_sources:
                data_source_dict[row['id']] = {"id": row['id'],
                                               "name": row['name'],
                                               "uuid": row['uuid']}

        query = (" SELECT id, name, data_source_id, object_type, units, "
                 "        low_limit, high_limit, is_trend, address, ratio "
                 " FROM tbl_points ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                data_source = data_source_dict.get(row['data_source_id'], None)
                meta_result = {"id": row['id'],
                               "name": row['name'],
                               "data_source": data_source,
                               "object_type": row['object_type'],
                               "units": row['units'],
                               "low_limit": row['low_limit'],
                               "high_limit": row['high_limit'],
                               "is_trend": row['is_trend'],
                               "address": row['address'],
                               "ratio": float(row['ratio']) if row['ratio'] is not None else None}
                result.append(meta_result)

        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'API.ERROR', ex)

        new_values = json.loads(raw_json, encoding='utf-8')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        add_value = (" INSERT INTO tbl_points (name, data_source_id, "
                     "                         object_type, units, low_limit, high_limit, is_trend, address, ratio) "
                     " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_value, (new_values['data']['name'],
                                   new_values['data']['data_source_id'],
                                   new_values['data']['object_type'],
                                   new_values['data']['units'],
                                   new_values['data']['low_limit'],
                                   new_values['data']['high_limit'],
                                   new_values['data']['is_trend'],
                                   new_values['data']['address'],
                                   new_values['data']['ratio'] if 'ratio' in new_values['data'].keys() else None))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/points/' + str(new_id)


class PointItem:
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
                                   description='API.INVALID_POINT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)

        query = (" SELECT id, name, uuid "
                 " FROM tbl_data_sources ")
        cursor.execute(query)
        rows_data_sources = cursor.fetchall()

        data_source_dict = dict()
        if rows_data_sources is not None and len(rows_data_sources) > 0:
            for row in rows_data_sources:
                data_source_dict[row['id']] = {"id": row['id'],
                                               "name": row['name'],
                                               "uuid": row['uuid']}

        query = (" SELECT id, name, data_source_id, object_type, units, low_limit, high_limit, is_trend, address, ratio "
                 " FROM tbl_points "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()
        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        data_source = data_source_dict.get(row['data_source_id'], None)
        result = {"id": row['id'],
                  "name": row['name'],
                  "data_source": data_source,
                  "object_type": row['object_type'],
                  "units": row['units'],
                  "low_limit": row['low_limit'],
                  "high_limit": row['high_limit'],
                  "is_trend": bool(row['is_trend']),
                  "address": row['address'],
                  "ratio": float(row['ratio']) if row['ratio'] is not None else None}
        resp.body = json.dumps(result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POINT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        # check if this point is being used by meters
        cursor.execute(" SELECT meter_id "
                       " FROM tbl_meters_points "
                       " WHERE point_id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_meter = cursor.fetchone()
        if row_meter is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_POINT_IS_BEING_USED_BY_A_METER')

        # check if this point is being used by sensors
        cursor.execute(" SELECT sensor_id "
                       " FROM tbl_sensors_points "
                       " WHERE point_id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_sensor = cursor.fetchone()
        if row_sensor is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_POINT_IS_BEING_USED_BY_A_SENSOR')

        # check if this point is being used by spaces
        cursor.execute(" SELECT space_id "
                       " FROM tbl_spaces_points "
                       " WHERE point_id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_space = cursor.fetchone()
        if row_space is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_POINT_IS_BEING_USED_BY_A_SPACE')

        # check if this point is being used by tenants
        cursor.execute(" SELECT tenant_id "
                       " FROM tbl_tenants_points "
                       " WHERE point_id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_tenant = cursor.fetchone()
        if row_tenant is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_POINT_IS_BEING_USED_BY_A_TENANT')

        # check if this point is being used by equipment parameters
        cursor.execute(" SELECT equipment_id "
                       " FROM tbl_equipments_parameters "
                       " WHERE point_id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_tenant = cursor.fetchone()
        if row_tenant is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_POINT_IS_BEING_USED_BY_A_EQUIPMENT_PARAMETER')

        cursor.execute(" DELETE FROM tbl_points WHERE id = %s ", (id_,))
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
            raise falcon.HTTPError(falcon.HTTP_400, title='API.EXCEPTION', description=ex)

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POINT_ID')

        new_values = json.loads(raw_json, encoding='utf-8')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        update_row = (" UPDATE tbl_points "
                      " SET name = %s, data_source_id = %s, "
                      "     object_type = %s, units = %s, "
                      "     low_limit = %s, high_limit = %s, is_trend = %s, address = %s, "
                      "     ratio = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (new_values['data']['name'],
                                    new_values['data']['data_source_id'],
                                    new_values['data']['object_type'],
                                    new_values['data']['units'],
                                    new_values['data']['low_limit'],
                                    new_values['data']['high_limit'],
                                    new_values['data']['is_trend'],
                                    new_values['data']['address'],
                                    new_values['data']['ratio'] if 'ratio' in new_values['data'].keys() else None,
                                    id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_200

