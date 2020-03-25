import falcon
import simplejson as json
import mysql.connector
import config
import uuid


class VirtualMeterCollection:
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

        query = (" SELECT m.id, m.name, m.uuid, "
                 "        ec.id, ec.name, ec.uuid, ec.unit_of_measure, ec.kgce, ec.kgco2e, "
                 "        m.is_counted "
                 " FROM tbl_virtual_meters m, tbl_energy_categories ec "
                 " WHERE m.energy_category_id = ec.id "
                 " ORDER BY m.energy_category_id, m.name ")
        cursor.execute(query)
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "energy_category": {"id": row[3], "name": row[4], "uuid": row[5],
                                                   "unit_of_measure": row[6], "kgce": row[7], "kgco2e": row[8]},
                               "is_counted": True if row[9] else False,
                               "expression": {}}
                # query expression
                expression = dict()
                query_expression = (" SELECT e.id, e.uuid, e.equation "
                                    " FROM tbl_expressions e "
                                    " WHERE e.virtual_meter_id = %s ")
                cursor.execute(query_expression, (row[0],))
                row_expression = cursor.fetchone()

                if row_expression is not None:
                    expression = {'id': row_expression[0],
                                  'uuid': row_expression[1],
                                  'equation': row_expression[2],
                                  'variables': []}

                    query_variables = (" SELECT v.id, v.name, v.meter_type, v.meter_id "
                                       " FROM tbl_expressions e, tbl_variables v "
                                       " WHERE e.id = %s AND v.expression_id = e.id "
                                       " ORDER BY v.name ")
                    cursor.execute(query_variables, (row_expression[0],))
                    rows_variables = cursor.fetchall()
                    if rows_variables is not None:
                        for row_variable in rows_variables:
                            if row_variable[2].lower() == 'meter':
                                query_meter = (" SELECT m.name "
                                               " FROM tbl_meters m "
                                               " WHERE m.id = %s ")
                                cursor.execute(query_meter, (row_variable[3],))
                                row_meter = cursor.fetchone()
                                if row_meter is not None:
                                    expression['variables'].append({'id': row_variable[0],
                                                                    'name': row_variable[1],
                                                                    'meter_type': row_variable[2],
                                                                    'meter_id': row_variable[3],
                                                                    'meter_name': row_meter[0]})
                            elif row_variable[2].lower() == 'offline_meter':
                                query_meter = (" SELECT m.name "
                                               " FROM tbl_offline_meters m "
                                               " WHERE m.id = %s ")
                                cursor.execute(query_meter, (row_variable[3],))
                                row_meter = cursor.fetchone()
                                if row_meter is not None:
                                    expression['variables'].append({'id': row_variable[0],
                                                                    'name': row_variable[1],
                                                                    'meter_type': row_variable[2],
                                                                    'meter_id': row_variable[3],
                                                                    'meter_name': row_meter[0]})
                            elif row_variable[2].lower() == 'virtual_meter':
                                query_meter = (" SELECT m.name "
                                               " FROM tbl_virtual_meters m "
                                               " WHERE m.id = %s ")
                                cursor.execute(query_meter, (row_variable[3],))
                                row_meter = cursor.fetchone()
                                if row_meter is not None:
                                    expression['variables'].append({'id': row_variable[0],
                                                                    'name': row_variable[1],
                                                                    'meter_type': row_variable[2],
                                                                    'meter_id': row_variable[3],
                                                                    'meter_name': row_meter[0]})

                meta_result['expression'] = expression
                result.append(meta_result)

        cursor.close()
        cnx.disconnect()
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
                                   description='API.INVALID_VIRTUAL_METER_NAME')

        if 'energy_category_id' not in new_values['data'].keys() or new_values['data']['energy_category_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_CATEGORY_ID')

        if 'is_counted' not in new_values['data'].keys() or not isinstance(new_values['data']['is_counted'], bool):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_COUNTED_VALUE')

        if 'expression' not in new_values['data'].keys():
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EXPRESSION_OBJECT')

        if 'equation' not in new_values['data']['expression'].keys() \
                or len(new_values['data']['expression']['equation']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EQUATION_IN_EXPRESSION')
        # todo: validate equation with more rules

        if 'variables' not in new_values['data']['expression'].keys() \
                or len(new_values['data']['expression']['variables']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.EMPTY_VARIABLES_ARRAY')

        for variable in new_values['data']['expression']['variables']:
            if 'name' not in variable.keys() or \
                    len(variable['name']) == 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_NAME')
            if 'meter_type' not in variable.keys() or \
                    len(variable['meter_type']) == 0 or \
                    variable['meter_type'].lower() not in ['meter', 'offline_meter', 'virtual_meter']:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_METER_TYPE')
            if 'meter_id' not in variable.keys() or \
                    variable['meter_id'] <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_virtual_meters "
                       " WHERE name = %s ", (new_values['data']['name'],))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NAME_ALREADY_EXISTS')

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_categories "
                       " WHERE id = %s ",
                       (new_values['data']['energy_category_id'],))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')

        for variable in new_values['data']['expression']['variables']:
            if variable['meter_type'].lower() == 'meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.METER_OF_VARIABLE_NOT_FOUND')
            elif variable['meter_type'].lower() == 'offline_meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_offline_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.OFFLINE_METER_OF_VARIABLE_NOT_FOUND')
            elif variable['meter_type'].lower() == 'virtual_meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_virtual_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.VIRTUAL_METER_OF_VARIABLE_NOT_FOUND')

        add_values = (" INSERT INTO tbl_virtual_meters "
                      "     (name, uuid, energy_category_id, is_counted) "
                      " VALUES (%s, %s, %s, %s) ")
        cursor.execute(add_values, (new_values['data']['name'],
                                    str(uuid.uuid4()),
                                    new_values['data']['energy_category_id'],
                                    new_values['data']['is_counted']))
        new_id = cursor.lastrowid
        cnx.commit()

        cursor.execute(" SELECT id "
                       " FROM tbl_expressions "
                       " WHERE virtual_meter_id = %s ", (new_id,))
        row_expression = cursor.fetchone()
        if row_expression is not None:
            # delete variables
            cursor.execute(" DELETE FROM tbl_variables WHERE expression_id = %s ", (row_expression[0],))
            # delete expression
            cursor.execute(" DELETE FROM tbl_expressions WHERE id = %s ", (row_expression[0],))
            cnx.commit()

        # add expression
        add_values = (" INSERT INTO tbl_expressions (uuid, virtual_meter_id, equation) "
                      " VALUES (%s, %s, %s) ")
        cursor.execute(add_values, (str(uuid.uuid4()),
                                    new_id,
                                    new_values['data']['expression']['equation'].lower()))
        new_expression_id = cursor.lastrowid
        cnx.commit()

        # add variables
        for variable in new_values['data']['expression']['variables']:
            add_values = (" INSERT INTO tbl_variables (name, expression_id, meter_type, meter_id) "
                          " VALUES (%s, %s, %s, %s) ")
            cursor.execute(add_values, (variable['name'].lower(),
                                        new_expression_id,
                                        variable['meter_type'],
                                        variable['meter_id'],))
            cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/virtualmeters/' + str(new_id)


class VirtualMeterItem:
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
                                   description='API.INVALID_VIRTUAL_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT m.id, m.name, m.uuid, "
                 "        ec.id, ec.name, ec.uuid, ec.unit_of_measure, ec.kgce, ec.kgco2e, "
                 "        m.is_counted "
                 " FROM tbl_virtual_meters m, tbl_energy_categories ec "
                 " WHERE m.energy_category_id = ec.id AND m.id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()

        if row is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NOT_FOUND')

        result = {"id": row[0], "name": row[1], "uuid": row[2],
                  "energy_category": {"id": row[3], "name": row[4], "uuid": row[5],
                                      "unit_of_measure": row[6], "kgce": row[7], "kgco2e": row[8]},
                  "is_counted": True if row[9] else False,
                  "expression": {}}

        expression = dict()
        query_expression = (" SELECT e.id, e.uuid, e.equation "
                            " FROM tbl_expressions e "
                            " WHERE e.virtual_meter_id = %s ")
        cursor.execute(query_expression, (id_,))
        row_expression = cursor.fetchone()

        if row_expression is not None:
            expression = {'id': row_expression[0],
                          'uuid': row_expression[1],
                          'equation': row_expression[2],
                          'variables': []}

            query_variables = (" SELECT v.id, v.name, v.meter_type, v.meter_id "
                               " FROM tbl_expressions e, tbl_variables v "
                               " WHERE e.id = %s AND v.expression_id = e.id "
                               " ORDER BY v.name ")
            cursor.execute(query_variables, (row_expression[0],))
            rows_variables = cursor.fetchall()
            if rows_variables is not None:
                for row_variable in rows_variables:
                    if row_variable[2].lower() == 'meter':
                        query_meter = (" SELECT m.name "
                                       " FROM tbl_meters m "
                                       " WHERE m.id = %s ")
                        cursor.execute(query_meter, (row_variable[3],))
                        row_meter = cursor.fetchone()
                        if row_meter is not None:
                            expression['variables'].append({'id': row_variable[0],
                                                            'name': row_variable[1],
                                                            'meter_type': row_variable[2],
                                                            'meter_id': row_variable[3],
                                                            'meter_name': row_meter[0]})
                    elif row_variable[2].lower() == 'offline_meter':
                        query_meter = (" SELECT m.name "
                                       " FROM tbl_offline_meters m "
                                       " WHERE m.id = %s ")
                        cursor.execute(query_meter, (row_variable[3],))
                        row_meter = cursor.fetchone()
                        if row_meter is not None:
                            expression['variables'].append({'id': row_variable[0],
                                                            'name': row_variable[1],
                                                            'meter_type': row_variable[2],
                                                            'meter_id': row_variable[3],
                                                            'meter_name': row_meter[0]})
                    elif row_variable[2].lower() == 'virtual_meter':
                        query_meter = (" SELECT m.name "
                                       " FROM tbl_virtual_meters m "
                                       " WHERE m.id = %s ")
                        cursor.execute(query_meter, (row_variable[3],))
                        row_meter = cursor.fetchone()
                        if row_meter is not None:
                            expression['variables'].append({'id': row_variable[0],
                                                            'name': row_variable[1],
                                                            'meter_type': row_variable[2],
                                                            'meter_id': row_variable[3],
                                                            'meter_name': row_meter[0]})

        result['expression'] = expression

        cursor.close()
        cnx.disconnect()
        resp.body = json.dumps(result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_VIRTUAL_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_virtual_meters "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NOT_FOUND')

        # check relations with other virtual meters
        cursor.execute(" SELECT vm.name "
                       " FROM tbl_variables va, tbl_expressions ex, tbl_virtual_meters vm "
                       " WHERE va.meter_id = %s AND va.meter_type = 'virtual_meter' AND va.expression_id = ex.id "
                       " AND ex.virtual_meter_id = vm.id ",
                       (id_,))
        row_virtual_meter = cursor.fetchone()
        if row_virtual_meter is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_OTHER_VIRTUAL_METERS')

        # check relation with spaces
        cursor.execute(" SELECT id "
                       " FROM tbl_spaces_virtual_meters "
                       " WHERE virtual_meter_id = %s ", (id_,))
        rows_factories = cursor.fetchall()
        if rows_factories is not None and len(rows_factories) > 0:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_SPACES')

        # check relation with equipments
        cursor.execute(" SELECT id "
                       " FROM tbl_equipments_virtual_meters "
                       " WHERE virtual_meter_id = %s ", (id_,))
        rows_equipments = cursor.fetchall()
        if rows_equipments is not None and len(rows_equipments) > 0:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_EQUIPMENTS')

        cursor.execute(" SELECT id "
                       " FROM tbl_expressions "
                       " WHERE virtual_meter_id = %s ", (id_,))
        row_expression = cursor.fetchone()
        if row_expression is not None:
            # delete variables
            cursor.execute(" DELETE FROM tbl_variables WHERE expression_id = %s ", (row_expression[0],))
            # delete expression
            cursor.execute(" DELETE FROM tbl_expressions WHERE id = %s ", (row_expression[0],))
            cnx.commit()

        cursor.execute(" DELETE FROM tbl_virtual_meters WHERE id = %s ", (id_,))
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
                                   description='API.INVALID_VIRTUAL_METER_ID')

        new_values = json.loads(raw_json, encoding='utf-8')

        if 'energy_category_id' not in new_values['data'].keys() or new_values['data']['energy_category_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_CATEGORY_ID')

        if 'is_counted' not in new_values['data'].keys() or not isinstance(new_values['data']['is_counted'], bool):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_COUNTED_VALUE')

        if 'expression' not in new_values['data'].keys():
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EXPRESSION_OBJECT')

        if 'equation' not in new_values['data']['expression'].keys() \
                or len(new_values['data']['expression']['equation']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EQUATION_IN_EXPRESSION')
        # todo: validate equation with more rules

        if 'variables' not in new_values['data']['expression'].keys() \
                or len(new_values['data']['expression']['variables']) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.EMPTY_VARIABLES_ARRAY')

        for variable in new_values['data']['expression']['variables']:
            if 'name' not in variable.keys() or \
                    len(variable['name']) == 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_NAME')
            if 'meter_type' not in variable.keys() or \
                len(variable['meter_type']) == 0 or \
                    variable['meter_type'].lower() not in ['meter', 'offline_meter', 'virtual_meter']:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_METER_TYPE')
            if 'meter_id' not in variable.keys() or \
                    variable['meter_id'] <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_VARIABLE_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_virtual_meters "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_categories "
                       " WHERE id = %s ",
                       (new_values['data']['energy_category_id'],))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')

        for variable in new_values['data']['expression']['variables']:
            if variable['meter_type'].lower() == 'meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.METER_OF_VARIABLE_NOT_FOUND')
            elif variable['meter_type'].lower() == 'offline_meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_offline_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.OFFLINE_METER_OF_VARIABLE_NOT_FOUND')
            elif variable['meter_type'].lower() == 'virtual_meter':
                cursor.execute(" SELECT name "
                               " FROM tbl_virtual_meters "
                               " WHERE id = %s ", (variable['meter_id'],))
                if cursor.fetchone() is None:
                    cursor.close()
                    cnx.disconnect()
                    raise falcon.HTTPError(falcon.HTTP_404,
                                           title='API.NOT_FOUND',
                                           description='API.VIRTUAL_METER_OF_VARIABLE_NOT_FOUND')

        update_row = (" UPDATE tbl_virtual_meters "
                      " SET name = %s, energy_category_id = %s, is_counted = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (new_values['data']['name'],
                                    new_values['data']['energy_category_id'],
                                    new_values['data']['is_counted'],
                                    id_,))
        cnx.commit()

        cursor.execute(" SELECT id "
                       " FROM tbl_expressions "
                       " WHERE virtual_meter_id = %s ", (id_,))
        row_expression = cursor.fetchone()
        if row_expression is not None:
            # delete variables
            cursor.execute(" DELETE FROM tbl_variables WHERE expression_id = %s ", (row_expression[0],))
            # delete expression
            cursor.execute(" DELETE FROM tbl_expressions WHERE id = %s ", (row_expression[0],))
            cnx.commit()

        # add expression
        add_values = (" INSERT INTO tbl_expressions (uuid, virtual_meter_id, equation) "
                      " VALUES (%s, %s, %s) ")
        cursor.execute(add_values, (str(uuid.uuid4()),
                                    id_,
                                    new_values['data']['expression']['equation'].lower()))
        new_expression_id = cursor.lastrowid
        cnx.commit()

        # add variables
        for variable in new_values['data']['expression']['variables']:
            add_values = (" INSERT INTO tbl_variables (name, expression_id, meter_type, meter_id) "
                          " VALUES (%s, %s, %s, %s) ")
            cursor.execute(add_values, (variable['name'].lower(),
                                        new_expression_id,
                                        variable['meter_type'],
                                        variable['meter_id'],))
            cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_200

