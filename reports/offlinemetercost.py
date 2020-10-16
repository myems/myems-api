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
    # Step 2: query the offline meter and energy category
    # Step 3: query base period energy consumption
    # Step 4: query base period energy cost
    # Step 5: query reporting period energy consumption
    # Step 6: query reporting period energy cost
    # Step 7: query parameters data
    # Step 8: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        print(req.params)
        offline_meter_id = req.params.get('offlinemeterid')
        period_type = req.params.get('periodtype')
        base_period_begins_datetime = req.params.get('baseperiodbeginsdatetime')
        base_period_ends_datetime = req.params.get('baseperiodendsdatetime')
        reporting_period_begins_datetime = req.params.get('reportingperiodbeginsdatetime')
        reporting_period_ends_datetime = req.params.get('reportingperiodendsdatetime')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if offline_meter_id is None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_OFFLINE_METER_ID')
        else:
            offline_meter_id = str.strip(offline_meter_id)
            if not offline_meter_id.isdigit() or int(offline_meter_id) <= 0:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       title='API.BAD_REQUEST',
                                       description='API.INVALID_OFFLINE_METER_ID')

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
        if base_period_begins_datetime is not None:
            base_period_begins_datetime = str.strip(base_period_begins_datetime)
            try:
                base_start_datetime_utc = datetime.strptime(base_period_begins_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_BASE_PERIOD_BEGINS_DATETIME")
            base_start_datetime_utc = base_start_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        base_end_datetime_utc = None
        if base_period_ends_datetime is not None:
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
        # Step 2: query the offline meter and energy category
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT m.id, m.name, m.cost_center_id, m.energy_category_id, "
                       "        ec.name, ec.unit_of_measure, ec.kgce, ec.kgco2e "
                       " FROM tbl_offline_meters m, tbl_energy_categories ec "
                       " WHERE m.id = %s AND m.energy_category_id = ec.id ", (offline_meter_id,))
        row_offline_meter = cursor.fetchone()
        if row_offline_meter is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND', description='API.OFFLINE_METER_NOT_FOUND')

        offline_meter = dict()
        offline_meter['id'] = row_offline_meter[0]
        offline_meter['name'] = row_offline_meter[1]
        offline_meter['cost_center_id'] = row_offline_meter[2]
        offline_meter['energy_category_id'] = row_offline_meter[3]
        offline_meter['energy_category_name'] = row_offline_meter[4]
        offline_meter['unit_of_measure'] = config.currency_unit
        offline_meter['kgce'] = row_offline_meter[6]
        offline_meter['kgco2e'] = row_offline_meter[7]

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 3: query base period energy consumption
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_energy_db)
        cursor = cnx.cursor()
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_offline_meter_hourly "
                 " WHERE offline_meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (offline_meter['id'], base_start_datetime_utc, base_end_datetime_utc))
        rows_offline_meter_hourly = cursor.fetchall()

        rows_offline_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_offline_meter_hourly,
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

        for row_offline_meter_periodically in rows_offline_meter_periodically:
            current_datetime_local = row_offline_meter_periodically[0].replace(tzinfo=timezone.utc) + \
                                     timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_offline_meter_periodically[1] is None \
                else row_offline_meter_periodically[1]
            base['timestamps'].append(current_datetime)
            base['values_in_kgce'].append(actual_value * offline_meter['kgce'])
            base['total_in_kgce'] += actual_value * offline_meter['kgce']
            base['values_in_kgco2e'].append(actual_value * offline_meter['kgco2e'])
            base['total_in_kgco2e'] += actual_value * offline_meter['kgco2e']

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 4: query base period energy cost
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_billing_db)
        cursor = cnx.cursor()
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_offline_meter_hourly "
                 " WHERE offline_meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (offline_meter['id'], base_start_datetime_utc, base_end_datetime_utc))
        rows_offline_meter_hourly = cursor.fetchall()

        rows_offline_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_offline_meter_hourly,
                                                                                    base_start_datetime_utc,
                                                                                    period_type)

        base['values_in_category'] = list()
        base['total_in_category'] = Decimal(0.0)

        for row_offline_meter_periodically in rows_offline_meter_periodically:
            actual_value = Decimal(0.0) if row_offline_meter_periodically[1] is None \
                else row_offline_meter_periodically[1]
            base['values_in_category'].append(actual_value)
            base['total_in_category'] += actual_value

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 5: query reporting period energy consumption
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_energy_db)
        cursor = cnx.cursor()
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_offline_meter_hourly "
                 " WHERE offline_meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (offline_meter['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
        rows_offline_meter_hourly = cursor.fetchall()

        rows_offline_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_offline_meter_hourly,
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

        for row_offline_meter_periodically in rows_offline_meter_periodically:
            current_datetime_local = row_offline_meter_periodically[0].replace(tzinfo=timezone.utc) + \
                timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_offline_meter_periodically[1] is None \
                else row_offline_meter_periodically[1]

            reporting['timestamps'].append(current_datetime)
            reporting['values_in_kgce'].append(actual_value * offline_meter['kgce'])
            reporting['total_in_kgce'] += actual_value * offline_meter['kgce']
            reporting['values_in_kgco2e'].append(actual_value * offline_meter['kgco2e'])
            reporting['total_in_kgco2e'] += actual_value * offline_meter['kgco2e']

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 6: query reporting period energy cost
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_billing_db)
        cursor = cnx.cursor()
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_offline_meter_hourly "
                 " WHERE offline_meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor.execute(query, (offline_meter['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
        rows_offline_meter_hourly = cursor.fetchall()

        rows_offline_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_offline_meter_hourly,
                                                                                    reporting_start_datetime_utc,
                                                                                    period_type)

        for row_offline_meter_periodically in rows_offline_meter_periodically:
            actual_value = Decimal(0.0) if row_offline_meter_periodically[1] is None \
                else row_offline_meter_periodically[1]

            reporting['values_in_category'].append(actual_value)
            reporting['total_in_category'] += actual_value

        cursor.close()
        cnx.disconnect()
        ################################################################################################################
        # Step 7: query parameters data
        ################################################################################################################
        tariff_dict = utilities.get_energy_category_tariffs(offline_meter['cost_center_id'],
                                                            offline_meter['energy_category_id'],
                                                            reporting_start_datetime_utc,
                                                            reporting_end_datetime_utc)
        print(tariff_dict)
        tariff_timestamp_list = list()
        tariff_value_list = list()
        for k, v in tariff_dict.items():
            tariff_timestamp_list.append(k.isoformat()[0:19])
            tariff_value_list.append(v)

        ################################################################################################################
        # Step 8: construct the report
        ################################################################################################################
        result = {
            "offline_meter": {
                "cost_center_id": offline_meter['cost_center_id'],
                "energy_category_id": offline_meter['energy_category_id'],
                "energy_category_name": offline_meter['energy_category_name'],
                "unit_of_measure": offline_meter['unit_of_measure'],
                "kgce": offline_meter['kgce'],
                "kgco2e": offline_meter['kgco2e'],
            },
            "reporting_period": {
                "increment_rate":
                    (reporting['total_in_category']-base['total_in_category'])/base['total_in_category']
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
        }

        resp.body = json.dumps(result)
