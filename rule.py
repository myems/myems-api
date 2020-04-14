import falcon
import json
import mysql.connector
import config
import uuid
from datetime import datetime, timedelta, timezone


class RuleCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_fdd_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, channel, expression, message, is_enabled, "
                 "        mute_start_datetime_utc, mute_end_datetime_utc "
                 " FROM tbl_rules "
                 " ORDER BY id ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                mute_start_datetime = row[7].replace(tzinfo=timezone.utc).timestamp() * 1000 if row[7] else None
                mute_end_datetime = row[8].replace(tzinfo=timezone.utc).timestamp() * 1000 if row[8] else None

                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "channel": row[3], "expression": row[4], "message": row[5].replace("<br>", ""),
                               "is_enabled": bool(row[6]),
                               "mute_start_datetime": mute_start_datetime,
                               "mute_end_datetime": mute_end_datetime}
                result.append(meta_result)

        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.EXCEPTION', description=ex)

        new_values = json.loads(raw_json, encoding='utf-8')
        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_RULE_NAME')
        name = str.strip(new_values['data']['name'])

        if 'channel' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['channel'], str) or \
                len(str.strip(new_values['data']['channel'])) == 0 or \
                str.strip(new_values['data']['channel']) not in ('call', 'sms', 'email', 'wechat', 'web'):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_CHANNEL')
        channel = str.strip(new_values['data']['channel'])

        if 'expression' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['expression'], str) or \
                len(str.strip(new_values['data']['expression'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_EXPRESSION')
        expression = str.strip(new_values['data']['expression'])

        if 'message' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['message'], str) or \
                len(str.strip(new_values['data']['message'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_MESSAGE')
        message = str.strip(new_values['data']['message'])

        if 'is_enabled' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['is_enabled'], bool):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_ENABLED')
        is_enabled = new_values['data']['is_enabled']

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        if 'mute_start_datetime' in new_values['data'].keys() and \
                isinstance(new_values['data']['mute_start_datetime'], str) and \
                len(str.strip(new_values['data']['mute_start_datetime'])) > 0:
            mute_start_datetime = str.strip(new_values['data']['mute_start_datetime'])
            mute_start_datetime = datetime.strptime(mute_start_datetime, '%Y-%m-%dT%H:%M:%S')
            mute_start_datetime = mute_start_datetime.replace(tzinfo=timezone.utc)
            mute_start_datetime -= timedelta(minutes=timezone_offset)
        else:
            mute_start_datetime = None

        if 'mute_end_datetime' in new_values['data'].keys() and \
                isinstance(new_values['data']['mute_end_datetime'], str) and \
                len(str.strip(new_values['data']['mute_end_datetime'])) > 0:
            mute_end_datetime = str.strip(new_values['data']['mute_end_datetime'])
            mute_end_datetime = datetime.strptime(mute_end_datetime, '%Y-%m-%dT%H:%M:%S')
            mute_end_datetime = mute_end_datetime.replace(tzinfo=timezone.utc)
            mute_end_datetime -= timedelta(minutes=timezone_offset)
        else:
            mute_end_datetime = None

        if (mute_start_datetime is None and mute_end_datetime is not None) or \
                (mute_start_datetime is not None and mute_end_datetime is None):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MUTE_DATETIME_RANGE')

        if mute_start_datetime is not None and \
            mute_end_datetime is not None and \
                mute_start_datetime >= mute_end_datetime:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MUTE_DATETIME_RANGE')

        cnx = mysql.connector.connect(**config.myems_fdd_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_rules "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.BAD_REQUEST',
                                   description='API.RULE_NAME_IS_ALREADY_IN_USE')

        add_row = (" INSERT INTO tbl_rules "
                   "             (name, uuid, channel, expression, message, is_enabled, "
                   "              mute_start_datetime_utc, mute_end_datetime_utc) "
                   " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_row, (name,
                                 str(uuid.uuid4()),
                                 channel,
                                 expression,
                                 message,
                                 is_enabled,
                                 mute_start_datetime,
                                 mute_end_datetime))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/rules/' + str(new_id)


class RuleItem:
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
                                   description='API.INVALID_RULE_ID')

        cnx = mysql.connector.connect(**config.myems_fdd_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, "
                 "        channel, expression, message, is_enabled, "
                 "        mute_start_datetime_utc, mute_end_datetime_utc "
                 " FROM tbl_rules "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()
        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.RULE_NOT_FOUND')

        mute_start_datetime = row[7].replace(tzinfo=timezone.utc).timestamp() * 1000 if row[7] else None
        mute_end_datetime = row[8].replace(tzinfo=timezone.utc).timestamp() * 1000 if row[8] else None

        result = {"id": row[0], "name": row[1], "uuid": row[2],
                  "channel": row[3], "expression": row[4], "message": row[5].replace("<br>", ""),
                  "is_enabled": bool(row[6]),
                  "mute_start_datetime": mute_start_datetime,
                  "mute_end_datetime": mute_end_datetime}
        resp.body = json.dumps(result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_RULE_ID')

        cnx = mysql.connector.connect(**config.myems_fdd_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT id "
                       " FROM tbl_rules "
                       " WHERE id = %s ",
                       (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.RULE_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_rules WHERE id = %s ", (id_,))
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
                                   description='API.INVALID_RULE_ID')

        new_values = json.loads(raw_json, encoding='utf-8')
        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_RULE_NAME')
        name = str.strip(new_values['data']['name'])

        if 'channel' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['channel'], str) or \
                len(str.strip(new_values['data']['channel'])) == 0 or \
                str.strip(new_values['data']['channel']) not in ('call', 'sms', 'email', 'wechat', 'web'):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_CHANNEL')
        channel = str.strip(new_values['data']['channel'])

        if 'expression' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['expression'], str) or \
                len(str.strip(new_values['data']['expression'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_EXPRESSION')
        expression = str.strip(new_values['data']['expression'])

        if 'message' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['message'], str) or \
                len(str.strip(new_values['data']['message'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_MESSAGE')
        message = str.strip(new_values['data']['message'])

        if 'is_enabled' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['is_enabled'], bool):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_ENABLED')
        is_enabled = new_values['data']['is_enabled']

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        if 'mute_start_datetime' in new_values['data'].keys() and \
                isinstance(new_values['data']['mute_start_datetime'], str) and \
                len(str.strip(new_values['data']['mute_start_datetime'])) > 0:
            mute_start_datetime = str.strip(new_values['data']['mute_start_datetime'])
            mute_start_datetime = datetime.strptime(mute_start_datetime, '%Y-%m-%dT%H:%M:%S')
            mute_start_datetime = mute_start_datetime.replace(tzinfo=timezone.utc)
            mute_start_datetime -= timedelta(minutes=timezone_offset)
        else:
            mute_start_datetime = None

        if 'mute_end_datetime' in new_values['data'].keys() and \
                isinstance(new_values['data']['mute_end_datetime'], str) and \
                len(str.strip(new_values['data']['mute_end_datetime'])) > 0:
            mute_end_datetime = str.strip(new_values['data']['mute_end_datetime'])
            mute_end_datetime = datetime.strptime(mute_end_datetime, '%Y-%m-%dT%H:%M:%S')
            mute_end_datetime = mute_end_datetime.replace(tzinfo=timezone.utc)
            mute_end_datetime -= timedelta(minutes=timezone_offset)
        else:
            mute_end_datetime = None

        if (mute_start_datetime is None and mute_end_datetime is not None) or \
                (mute_start_datetime is not None and mute_end_datetime is None):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MUTE_DATETIME_RANGE')

        if mute_start_datetime is not None and \
            mute_end_datetime is not None and \
                mute_start_datetime >= mute_end_datetime:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MUTE_DATETIME_RANGE')

        cnx = mysql.connector.connect(**config.myems_fdd_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT id "
                       " FROM tbl_rules "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.RULE_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_rules "
                       " WHERE name = %s AND id != %s ", (name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.BAD_REQUEST',
                                   description='API.RULE_NAME_IS_ALREADY_IN_USE')

        update_row = (" UPDATE tbl_rules "
                      " SET name = %s, channel = %s, expression = %s, message = %s, is_enabled = %s, "
                      "     mute_start_datetime_utc = %s, mute_end_datetime_utc = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    channel,
                                    expression,
                                    message,
                                    is_enabled,
                                    mute_start_datetime,
                                    mute_end_datetime,
                                    id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_200
