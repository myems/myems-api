import falcon
import simplejson as json
import mysql.connector
import config
from datetime import datetime, timedelta, timezone
import utilities
from decimal import *


class Reporting:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    ####################################################################################################################
    # PROCEDURES
    # Step 1: valid parameters
    # Step 2: query the space
    # Step 3: query energy categories
    # Step 4: query associated sensors
    # Step 5: query associated points
    # Step 6: query child spaces
    # Step 7: query base period energy input
    # Step 8: query reporting period energy input
    # Step 9: query associated sensors, points and tariff data
    # Step 10: query child spaces energy input
    # Step 11: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        print(req.params)
        space_id = req.params.get('spaceid')
        period_type = req.params.get('periodtype')
        base_period_begins_datetime = req.params.get('baseperiodbeginsdatetime')
        base_period_ends_datetime = req.params.get('baseperiodendsdatetime')
        reporting_period_begins_datetime = req.params.get('reportingperiodbeginsdatetime')
        reporting_period_ends_datetime = req.params.get('reportingperiodendsdatetime')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if space_id is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_SPACE_ID')
        else:
            space_id = str.strip(space_id)
            if not space_id.isdigit() or int(space_id) <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_SPACE_ID')

        if period_type is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_PERIOD_TYPE')
        else:
            period_type = str.strip(period_type)
            if period_type not in ['hourly', 'daily', 'monthly', 'yearly']:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_PERIOD_TYPE')

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        base_start_datetime_utc = None
        if base_period_begins_datetime is not None and len(str.strip(base_period_begins_datetime)) > 0:
            base_period_begins_datetime = str.strip(base_period_begins_datetime)
            try:
                base_start_datetime_utc = datetime.strptime(base_period_begins_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_BASE_PERIOD_BEGINS_DATETIME")
            base_start_datetime_utc = base_start_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        base_end_datetime_utc = None
        if base_period_ends_datetime is not None and len(str.strip(base_period_ends_datetime)) > 0:
            base_period_ends_datetime = str.strip(base_period_ends_datetime)
            try:
                base_end_datetime_utc = datetime.strptime(base_period_ends_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_BASE_PERIOD_ENDS_DATETIME")
            base_end_datetime_utc = base_end_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if base_start_datetime_utc is not None and base_end_datetime_utc is not None and \
                base_start_datetime_utc >= base_end_datetime_utc:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_BASE_PERIOD_ENDS_DATETIME')

        if reporting_period_begins_datetime is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description="API.INVALID_REPORTING_PERIOD_BEGINS_DATETIME")
        else:
            reporting_period_begins_datetime = str.strip(reporting_period_begins_datetime)
            try:
                reporting_start_datetime_utc = datetime.strptime(reporting_period_begins_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_REPORTING_PERIOD_BEGINS_DATETIME")
            reporting_start_datetime_utc = reporting_start_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if reporting_period_ends_datetime is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description="API.INVALID_REPORTING_PERIOD_ENDS_DATETIME")
        else:
            reporting_period_ends_datetime = str.strip(reporting_period_ends_datetime)
            try:
                reporting_end_datetime_utc = datetime.strptime(reporting_period_ends_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_REPORTING_PERIOD_ENDS_DATETIME")
            reporting_end_datetime_utc = reporting_end_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if reporting_start_datetime_utc >= reporting_end_datetime_utc:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_REPORTING_PERIOD_ENDS_DATETIME')

        ################################################################################################################
        # Step 2: query the space
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT id, name, cost_center_id, "
                       " FROM tbl_spaces "
                       " WHERE id = %s ", (space_id,))
        row_space = cursor.fetchone()
        if row_space is None:
            if cursor:
                cursor.close()
            if cnx:
                cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND', description='API.SPACE_NOT_FOUND')

        space = dict()
        space['id'] = row_space[0]
        space['name'] = row_space[1]
        space['cost_center_id'] = row_space[2]

        ################################################################################################################
        # Step 3: query energy categories
        ################################################################################################################
        cursor.execute(" SELECT id, name, unit_of_measure, kgce, kgco2e "
                       " FROM tbl_energy_categories ORDER BY id ", )
        rows_energy_categories = cursor.fetchall()
        if rows_energy_categories is None or len(rows_energy_categories) == 0:
            if cursor:
                cursor.close()
            if cnx:
                cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404,
                                   title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')

        energy_category_dict = dict()
        for row_energy_category in rows_energy_categories:
            energy_category_dict[row_energy_category[0]] = {"name": row_energy_category[1],
                                                            "unit_of_measure": row_energy_category[2],
                                                            "kgce": row_energy_category[3],
                                                            "kgco2e": row_energy_category[4]}

        ################################################################################################################
        # Step 4: query associated sensors
        ################################################################################################################
        point_list = list()
        cursor.execute(" SELECT po.id, po.name, po.units, po.object_type  "
                       " FROM tbl_spaces sp, tbl_sensors se, tbl_spaces_sensors spse, "
                       "      tbl_points po, tbl_sensors_points sepo "
                       " WHERE sp.id = %s AND sp.id = spse.space_id AND spse.sensor_id = se.id "
                       "       AND se.id = sepo.sensor_id AND sepo.point_id = po.id "
                       " ORDER BY po.id ", )
        rows_points = cursor.fetchall()
        if rows_points is not None and len(rows_points) > 0:
            for row in rows_points:
                point_list.append({"id": row[0], "name": row[1], "units": row[2], "object_type": row[3]})

        ################################################################################################################
        # Step 5: query associated points
        ################################################################################################################
        cursor.execute(" SELECT po.id, po.name, po.units, po.object_type  "
                       " FROM tbl_spaces sp, tbl_spaces_points sppo, tbl_points po "
                       " WHERE sp.id = %s AND sp.id = sppo.space_id AND sppo.point_id = po.id "
                       " ORDER BY po.id ", )
        rows_points = cursor.fetchall()
        if rows_points is not None and len(rows_points) > 0:
            for row in rows_points:
                point_list.append({"id": row[0], "name": row[1], "units": row[2], "object_type": row[3]})
        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()
        ################################################################################################################
        # Step 6: query child spaces
        ################################################################################################################
        child_space_list = list()
        cursor.execute(" SELECT id, name  "
                       " FROM tbl_spaces "
                       " WHERE parent_space_id = %s "
                       " ORDER BY id ", )
        rows_child_spaces = cursor.fetchall()
        if rows_child_spaces is not None and len(rows_child_spaces) > 0:
            for row in rows_child_spaces:
                child_space_list.append({"id": row[0], "name": row[1]})
        ################################################################################################################
        # Step 7: query base period energy input
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_energy_db)
        cursor = cnx.cursor()
        query = (" SELECT start_datetime_utc, actual_value, energy_category_id "
                 " FROM tbl_space_input_category_hourly "
                 " WHERE space_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (space['id'], base_start_datetime_utc, base_end_datetime_utc))
        rows_space_hourly = cursor.fetchall()

        rows_space_periodically = utilities.aggregate_hourly_data_by_period(rows_space_hourly,
                                                                            base_start_datetime_utc,
                                                                            period_type)
        base = dict()
        base['timestamps'] = list()
        base['values_in_category'] = list()
        base['total_in_category'] = Decimal(0.0)
        base['values_in_kgce'] = list()
        base['total_in_kgce'] = Decimal(0.0)
        base['values_in_kgco2e'] = list()
        base['total_in_kgco2e'] = Decimal(0.0)

        for row_space_periodically in rows_space_periodically:
            current_datetime_local = row_space_periodically[0].replace(tzinfo=timezone.utc) + \
                                     timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_space_periodically[1] is None else row_space_periodically[1]
            base['timestamps'].append(current_datetime)
            base['values_in_category'].append(actual_value)
            base['total_in_category'] += actual_value
            base['values_in_kgce'].append(actual_value * space['kgce'])
            base['total_in_kgce'] += actual_value * space['kgce']
            base['values_in_kgco2e'].append(actual_value * space['kgco2e'])
            base['total_in_kgco2e'] += actual_value * space['kgco2e']

        ################################################################################################################
        # Step 8: query reporting period energy input
        ################################################################################################################
        query = (" SELECT start_datetime_utc, actual_value, energy_category_id "
                 " FROM tbl_space_input_category_hourly "
                 " WHERE meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (space['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
        rows_space_hourly = cursor.fetchall()

        rows_space_periodically = utilities.aggregate_hourly_data_by_period(rows_space_hourly,
                                                                            reporting_start_datetime_utc,
                                                                            period_type)
        reporting = dict()
        reporting['timestamps'] = list()
        reporting['values_in_category'] = list()
        reporting['total_in_category'] = Decimal(0.0)
        reporting['values_in_kgce'] = list()
        reporting['total_in_kgce'] = Decimal(0.0)
        reporting['values_in_kgco2e'] = list()
        reporting['total_in_kgco2e'] = Decimal(0.0)

        for row_space_periodically in rows_space_periodically:
            current_datetime_local = row_space_periodically[0].replace(tzinfo=timezone.utc) + \
                timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_space_periodically[1] is None else row_space_periodically[1]

            reporting['timestamps'].append(current_datetime)
            reporting['values_in_category'].append(actual_value)
            reporting['total_in_category'] += actual_value
            reporting['values_in_kgce'].append(actual_value * space['kgce'])
            reporting['total_in_kgce'] += actual_value * space['kgce']
            reporting['values_in_kgco2e'].append(actual_value * space['kgco2e'])
            reporting['total_in_kgco2e'] += actual_value * space['kgco2e']

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 9: query associated sensors, points and tariff data
        ################################################################################################################
        tariff_dict = utilities.get_energy_category_tariffs(space['cost_center_id'],
                                                            space['energy_category_id'],
                                                            reporting_start_datetime_utc,
                                                            reporting_end_datetime_utc)
        print(tariff_dict)
        tariff_timestamp_list = list()
        tariff_value_list = list()
        for k, v in tariff_dict.items():
            tariff_timestamp_list.append(k.isoformat()[0:19][0:19])
            tariff_value_list.append(v)

        ################################################################################################################
        # Step 10: query child spaces data
        ################################################################################################################

        ################################################################################################################
        # Step 11: construct the report
        ################################################################################################################
        result = {
            "space": {
                "cost_center_id": space['cost_center_id'],
                "energy_category_id": space['energy_category_id'],
                "energy_category_name": space['energy_category_name'],
                "unit_of_measure": space['unit_of_measure'],
                "kgce": space['kgce'],
                "kgco2e": space['kgco2e'],
            },
            "energy_categories": {

            },
            "reporting_period": {
                "increment_rate":
                    (reporting['total_in_category'] - base['total_in_category'])/base['total_in_category']
                    if base['total_in_category'] > 0 else None,
                "total_in_category": reporting['total_in_category'],
                "total_in_kgce": reporting['total_in_kgce'],
                "total_in_kgco2e": reporting['total_in_kgco2e'],
                "timestamps": [reporting['timestamps'],
                               reporting['timestamps'],
                               reporting['timestamps']],
                "values": [reporting['values_in_category'],
                           reporting['values_in_kgce'],
                           reporting['values_in_kgco2e']],
            },
            "base_period": {
                "total_in_category": base['total_in_category'],
                "total_in_kgce": base['total_in_kgce'],
                "total_in_kgco2e": base['total_in_kgco2e'],
                "timestamps": [base['timestamps'],
                               base['timestamps'],
                               base['timestamps']],
                "values": [base['values_in_category'],
                           base['values_in_kgce'],
                           base['values_in_kgco2e']],
            },
            "parameters": {
                "names": ['TARIFF'],
                "timestamps": [tariff_timestamp_list],
                "values": [tariff_value_list]
            },
            "child_spaces": {
                "total_in_category": base['total_in_category'],
                "total_in_kgce": base['total_in_kgce'],
                "total_in_kgco2e": base['total_in_kgco2e'],
                "timestamps": [base['timestamps'],
                               base['timestamps'],
                               base['timestamps']],
                "values": [base['values_in_category'],
                           base['values_in_kgce'],
                           base['values_in_kgco2e']],
            },
        }

        resp.body = json.dumps(result)
