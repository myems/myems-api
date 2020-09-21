from datetime import datetime, timedelta
import mysql.connector
import collections
from decimal import *
import config


def aggregate_hourly_data_by_period(rows_hourly, start_datetime_utc, period_type):
    if period_type == "hourly":
        return rows_hourly

    elif period_type == "daily":
        start_datetime_utc_daily = start_datetime_utc

        rows_daily = list()
        temp_actual_value = Decimal(0.0)
        for row_hourly in rows_hourly:
            datetime_utc = row_hourly[0]
            actual_value = row_hourly[1]

            datetime_local_str = (datetime_utc +
                                  timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y-%m-%d %H:%M:%S')

            start_datetime_utc_day_str = (start_datetime_utc_daily +
                                          timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y-%m-%d')

            if row_hourly == rows_hourly[-1]:
                temp_actual_value += actual_value
                rows_daily.append((start_datetime_utc_daily, temp_actual_value))
                break

            if start_datetime_utc_day_str in datetime_local_str:
                temp_actual_value = temp_actual_value + actual_value

            else:
                rows_daily.append((start_datetime_utc_daily, temp_actual_value))
                temp_actual_value = Decimal(0.0)
                temp_actual_value += actual_value
                start_datetime_utc_daily = start_datetime_utc_daily + timedelta(days=1)
        return rows_daily

    elif period_type == "monthly":
        start_datetime_utc_monthly = start_datetime_utc

        rows_monthly = list()
        temp_actual_value = Decimal(0.0)
        temp = 0
        for row_hourly in rows_hourly:
            datetime_utc = row_hourly[0]
            actual_value = row_hourly[1]

            datetime_local_str = (datetime_utc +
                                  timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y-%m-%d %H:%M:%S')

            start_datetime_utc_month_str = (start_datetime_utc_monthly +
                                            timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y-%m')

            if row_hourly == rows_hourly[-1]:
                temp_actual_value += actual_value
                rows_monthly.append((start_datetime_utc_monthly, temp_actual_value))
                break

            if start_datetime_utc_month_str in datetime_local_str:
                temp_actual_value = temp_actual_value + actual_value

            else:
                temp = temp + 1
                rows_monthly.append((start_datetime_utc_monthly, temp_actual_value))
                temp_actual_value = Decimal(0.0)
                temp_actual_value += actual_value

                if start_datetime_utc_monthly.month == 1:
                    temp_day = 28
                    sy = start_datetime_utc_monthly.year
                    if (sy % 100 != 0 and sy % 4 == 0) or (sy % 100 == 0 and sy % 400 == 0):
                        temp_day = 29

                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year,
                                                          month=start_datetime_utc_monthly.month+1,
                                                          day=temp_day,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)
                elif start_datetime_utc_monthly.month == 2:
                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year,
                                                          month=start_datetime_utc_monthly.month+1,
                                                          day=31,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)
                elif start_datetime_utc_monthly.month in [3, 5, 8, 10]:
                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year,
                                                          month=start_datetime_utc_monthly.month+1,
                                                          day=30,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)
                elif start_datetime_utc_monthly.month == 7:
                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year,
                                                          month=start_datetime_utc_monthly.month+1,
                                                          day=31,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)
                elif start_datetime_utc_monthly.month in [4, 6, 9, 11]:
                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year,
                                                          month=start_datetime_utc_monthly.month + 1,
                                                          day=31,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)
                elif start_datetime_utc_monthly.month == 12:
                    start_datetime_utc_monthly = datetime(year=start_datetime_utc_monthly.year+1,
                                                          month=1,
                                                          day=31,
                                                          hour=start_datetime_utc_monthly.hour,
                                                          minute=start_datetime_utc_monthly.minute,
                                                          second=start_datetime_utc_monthly.second,
                                                          microsecond=0,
                                                          tzinfo=start_datetime_utc_monthly.tzinfo)

        return rows_monthly

    elif period_type == "yearly":
        start_datetime_utc_yearly = start_datetime_utc

        rows_yearly = list()
        temp_actual_value = Decimal(0.0)
        temp = 0
        for row_hourly in rows_hourly:
            datetime_utc = row_hourly[0]
            actual_value = row_hourly[1]

            datetime_local_str = (datetime_utc +
                                  timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y-%m-%d %H:%M:%S')

            start_datetime_utc_year_str = (start_datetime_utc_yearly +
                                           timedelta(hours=int(config.utc_offset[1:3]))).strftime('%Y')

            if row_hourly == rows_hourly[-1]:
                temp_actual_value += actual_value
                rows_yearly.append((start_datetime_utc_yearly, temp_actual_value))
                break

            if start_datetime_utc_year_str in datetime_local_str:
                temp_actual_value = temp_actual_value + actual_value

            else:
                temp = temp + 1
                rows_yearly.append((start_datetime_utc_yearly, temp_actual_value))
                temp_actual_value = Decimal(0.0)
                temp_actual_value += actual_value
                start_datetime_utc_yearly = datetime(year=start_datetime_utc_yearly.year + 1,
                                                     month=start_datetime_utc_yearly.month,
                                                     day=start_datetime_utc_yearly.day,
                                                     hour=start_datetime_utc_yearly.hour,
                                                     minute=start_datetime_utc_yearly.minute,
                                                     second=start_datetime_utc_yearly.second,
                                                     microsecond=0,
                                                     tzinfo=start_datetime_utc_yearly.tzinfo)

        return rows_yearly


########################################################################################################################
# Get tariffs by energy category
########################################################################################################################
def get_energy_category_tariffs(cost_center_id, energy_category_id, start_datetime_utc, end_datetime_utc):

    # todo: verify parameters
    if cost_center_id is None:
        return dict()

    start_datetime_utc = start_datetime_utc.replace(tzinfo=None)
    end_datetime_utc = end_datetime_utc.replace(tzinfo=None)

    # get timezone offset in minutes, this value will be returned to client
    timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
    if config.utc_offset[0] == '-':
        timezone_offset = -timezone_offset

    tariff_dict = collections.OrderedDict()

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        query_tariffs = (" SELECT t.id, t.valid_from_datetime_utc, t.valid_through_datetime_utc "
                         " FROM tbl_tariffs t, tbl_cost_centers_tariffs cct "
                         " WHERE t.energy_category_id = %s AND "
                         "       t.id = cct.tariff_id AND "
                         "       cct.cost_center_id = %s AND "
                         "       t.valid_through_datetime_utc >= %s AND "
                         "       t.valid_from_datetime_utc <= %s "
                         " ORDER BY t.valid_from_datetime_utc ")
        cursor.execute(query_tariffs, (energy_category_id, cost_center_id, start_datetime_utc, end_datetime_utc,))
        rows_tariffs = cursor.fetchall()
    except Exception as e:
        print(str(e))
        if cnx:
            cnx.disconnect()
        if cursor:
            cursor.close()
        return dict()

    if rows_tariffs is None or len(rows_tariffs) == 0:
        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()
        return dict()

    for row in rows_tariffs:
        tariff_dict[row[0]] = {'valid_from_datetime_utc': row[1],
                               'valid_through_datetime_utc': row[2],
                               'rates': list()}

    try:
        query_timeofuse_tariffs = (" SELECT tariff_id, start_time_of_day, end_time_of_day, price "
                                   " FROM tbl_tariffs_timeofuses "
                                   " WHERE tariff_id IN ( " + ', '.join(map(str, tariff_dict.keys())) + ")"
                                   " ORDER BY tariff_id, start_time_of_day ")
        cursor.execute(query_timeofuse_tariffs, )
        rows_timeofuse_tariffs = cursor.fetchall()
    except Exception as e:
        print(str(e))
        if cnx:
            cnx.disconnect()
        if cursor:
            cursor.close()
        return dict()

    if cursor:
        cursor.close()
    if cnx:
        cnx.disconnect()

    if rows_timeofuse_tariffs is None or len(rows_timeofuse_tariffs) == 0:
        return dict()

    for row in rows_timeofuse_tariffs:
        tariff_dict[row[0]]['rates'].append({'start_time_of_day': row[1],
                                             'end_time_of_day': row[2],
                                             'price': row[3]})

    result = dict()
    for tariff_id, tariff_value in tariff_dict.items():
        current_datetime_utc = tariff_value['valid_from_datetime_utc']
        while current_datetime_utc < tariff_value['valid_through_datetime_utc']:
            for rate in tariff_value['rates']:
                current_datetime_local = current_datetime_utc + timedelta(minutes=timezone_offset)
                seconds_since_midnight = (current_datetime_local -
                                          current_datetime_local.replace(hour=0,
                                                                         second=0,
                                                                         microsecond=0,
                                                                         tzinfo=None)).total_seconds()
                if rate['start_time_of_day'].total_seconds() <= \
                        seconds_since_midnight < rate['end_time_of_day'].total_seconds():
                    result[current_datetime_utc] = rate['price']
                    break

            # start from the next time slot
            current_datetime_utc += timedelta(minutes=config.minutes_to_count)

    return {k: v for k, v in result.items() if start_datetime_utc <= k <= end_datetime_utc}


########################################################################################################################
# Get tariffs by energy item
########################################################################################################################
def get_energy_item_tariffs(cost_center_id, energy_item_id, start_datetime_utc, end_datetime_utc):
    # todo: verify parameters
    if cost_center_id is None:
        return dict()

    start_datetime_utc = start_datetime_utc.replace(tzinfo=None)
    end_datetime_utc = end_datetime_utc.replace(tzinfo=None)

    # get timezone offset in minutes, this value will be returned to client
    timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
    if config.utc_offset[0] == '-':
        timezone_offset = -timezone_offset

    tariff_dict = collections.OrderedDict()

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        query_tariffs = (" SELECT t.id, t.valid_from_datetime_utc, t.valid_through_datetime_utc "
                         " FROM tbl_tariffs t, tbl_cost_centers_tariffs cct, tbl_energy_items ei "
                         " WHERE ei.id = %s AND "
                         "       t.energy_category_id = ei.energy_category_id AND "
                         "       t.id = cct.tariff_id AND "
                         "       cct.cost_center_id = %s AND "
                         "       t.valid_through_datetime_utc >= %s AND "
                         "       t.valid_from_datetime_utc <= %s "
                         " ORDER BY t.valid_from_datetime_utc ")
        cursor.execute(query_tariffs, (energy_item_id, cost_center_id, start_datetime_utc, end_datetime_utc,))
        rows_tariffs = cursor.fetchall()
    except Exception as e:
        print(str(e))
        if cnx:
            cnx.disconnect()
        if cursor:
            cursor.close()
        return dict()

    if rows_tariffs is None or len(rows_tariffs) == 0:
        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()
        return dict()

    for row in rows_tariffs:
        tariff_dict[row[0]] = {'valid_from_datetime_utc': row[1],
                               'valid_through_datetime_utc': row[2],
                               'rates': list()}

    try:
        query_timeofuse_tariffs = (" SELECT tariff_id, start_time_of_day, end_time_of_day, price "
                                   " FROM tbl_tariffs_timeofuses "
                                   " WHERE tariff_id IN ( " + ', '.join(map(str, tariff_dict.keys())) + ")"
                                   " ORDER BY tariff_id, start_time_of_day ")
        cursor.execute(query_timeofuse_tariffs, )
        rows_timeofuse_tariffs = cursor.fetchall()
    except Exception as e:
        print(str(e))
        if cnx:
            cnx.disconnect()
        if cursor:
            cursor.close()
        return dict()

    if cursor:
        cursor.close()
    if cnx:
        cnx.disconnect()

    if rows_timeofuse_tariffs is None or len(rows_timeofuse_tariffs) == 0:
        return dict()

    for row in rows_timeofuse_tariffs:
        tariff_dict[row[0]]['rates'].append({'start_time_of_day': row[1],
                                             'end_time_of_day': row[2],
                                             'price': row[3]})

    result = dict()
    for tariff_id, tariff_value in tariff_dict.items():
        current_datetime_utc = tariff_value['valid_from_datetime_utc']
        while current_datetime_utc < tariff_value['valid_through_datetime_utc']:
            for rate in tariff_value['rates']:
                current_datetime_local = current_datetime_utc + timedelta(minutes=timezone_offset)
                seconds_since_midnight = (current_datetime_local -
                                          current_datetime_local.replace(hour=0,
                                                                         second=0,
                                                                         microsecond=0,
                                                                         tzinfo=None)).total_seconds()
                if rate['start_time_of_day'].total_seconds() <= \
                        seconds_since_midnight < rate['end_time_of_day'].total_seconds():
                    result[current_datetime_utc] = rate['price']
                    break

            # start from the next time slot
            current_datetime_utc += timedelta(minutes=config.minutes_to_count)

    return {k: v for k, v in result.items() if start_datetime_utc <= k <= end_datetime_utc}
