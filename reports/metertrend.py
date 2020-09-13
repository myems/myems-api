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
    # Step 2: query the meter and it's points
    # Step 4: query reporting period points trends
    # Step 5: query parameters data
    # Step 6: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        print(req.params)
        meter_id = req.params.get('meterid')
        reporting_period_begins_datetime = req.params.get('reportingperiodbeginsdatetime')
        reporting_period_ends_datetime = req.params.get('reportingperiodendsdatetime')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if meter_id is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_METER_ID')
        else:
            meter_id = str.strip(meter_id)
            if not meter_id.isdigit() or int(meter_id) <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_METER_ID')

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

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
        # Step 2: query the meter and it's points
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT m.id, m.name, m.cost_center_id, m.energy_category_id, "
                       "        ec.name, ec.unit_of_measure, ec.kgce, ec.kgco2e "
                       " FROM tbl_meters m, tbl_energy_categories ec "
                       " WHERE m.id = %s AND m.energy_category_id = ec.id ", (meter_id,))
        row_meter = cursor.fetchone()
        if row_meter is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND', description='API.METER_NOT_FOUND')

        meter = dict()
        meter['id'] = row_meter[0]
        meter['name'] = row_meter[1]
        meter['cost_center_id'] = row_meter[2]
        meter['energy_category_id'] = row_meter[3]
        meter['energy_category_name'] = row_meter[4]
        meter['unit_of_measure'] = row_meter[5]
        meter['kgce'] = row_meter[6]
        meter['kgco2e'] = row_meter[7]

        point_list = list()
        query = (" SELECT p.id, p.name, p.units, p.object_type "
                 " FROM tbl_points p, tbl_meters_points mp, tbl_meters m "
                 " WHERE  m.id = %s "
                 "        AND m.id = mp.meter_id "
                 "        AND p.id = mp.point_id "
                 "        AND p.is_trend = True "
                 " ORDER BY p.name  ")
        cursor.execute(query, (meter_id,))
        rows = cursor.fetchall()

        if rows is not None and len(rows) > 0:
            for row in rows:
                point_list.append({"id": row[0], "name": row[1], "units": row[2], "object_type": row[3]})

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        if len(point_list) == 0:
            raise falcon.HTTPError(falcon.HTTP_404,
                                   title='API.NOT_FOUND',
                                   description='API.THERE_IS_NOT_ASSOCIATED_POINTS')

        ################################################################################################################
        # Step 3: query reporting period points trends
        ################################################################################################################

        cnx = mysql.connector.connect(**config.myems_historical_db)
        cursor = cnx.cursor()

        reporting = dict()
        reporting['names'] = list()
        reporting['timestamps'] = list()
        reporting['values'] = list()

        for point in point_list:
            reporting['names'].append(point['name'])

            point_values = []
            if point['object_type'] == 'ANALOG_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_analog_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor.execute(query, (point['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
                rows = cursor.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        point_values.append(row[1])

            elif point['object_type'] == 'ENERGY_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_energy_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor.execute(query, (point['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
                rows = cursor.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')

                        reporting['timestamps'].append(current_datetime)

                        point_values.append(row[1])
            elif point['object_type'] == 'DIGITAL_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_digital_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s ")
                cursor.execute(query, (point['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
                rows = cursor.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        point_values.append(row[1])

            reporting['values'].append(point_values)

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 4: query parameters data
        ################################################################################################################
        tariff_dict = utilities.get_energy_category_tariffs(meter['cost_center_id'],
                                                            meter['energy_category_id'],
                                                            reporting_start_datetime_utc,
                                                            reporting_end_datetime_utc)
        print(tariff_dict)
        tariff_timestamp_list = list()
        tariff_value_list = list()
        for k, v in tariff_dict.items():
            tariff_timestamp_list.append(k.isoformat())
            tariff_value_list.append(v)

        ################################################################################################################
        # Step 5: construct the report
        ################################################################################################################
        result = {
            "meter": {
                "cost_center_id": meter['cost_center_id'],
                "energy_category_id": meter['energy_category_id'],
                "energy_category_name": meter['energy_category_name'],
                "unit_of_measure": meter['unit_of_measure'],
                "kgce": meter['kgce'],
                "kgco2e": meter['kgco2e'],
            },
            "reporting_period": {
                "names": reporting['names'],
                "timestamps": reporting['timestamps'],
                "values": reporting['values'],
            },
            "parameters": {
                "names": ['TARIFF'],
                "timestamps": tariff_timestamp_list,
                "values": [tariff_value_list]
            },
        }

        resp.body = json.dumps(result)
