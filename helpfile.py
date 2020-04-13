import urllib
import falcon
import json
import mysql.connector
import config
import uuid
from datetime import datetime, timezone
import os
import shutil


class HelpFileCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_user_db)
        cursor = cnx.cursor()

        query = (" SELECT uuid, display_name "
                 " FROM tbl_users ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        user_dict = dict()
        if rows is not None and len(rows) > 0:
            for row in rows:
                user_dict[row[0]] = row[1]

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, file_name, uuid, upload_datetime_utc, user_uuid "
                 " FROM tbl_help_files "
                 " ORDER BY upload_datetime_utc desc ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                upload_datetime = row[3]
                upload_datetime = upload_datetime.replace(tzinfo=timezone.utc)
                meta_result = {"id": row[0],
                               "file_name": row[1],
                               "uuid": row[2],
                               "upload_datetime": upload_datetime.timestamp() * 1000,
                               "user_display_name": user_dict.get(row[4], None)}
                result.append(meta_result)

        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp):
        """Handles POST requests"""
        try:
            upload = req.get_param('file')
            # Read upload file as binary
            raw_blob = upload.file.read()
            # Retrieve filename
            filename = upload.filename

            # Define file_path
            file_path = os.path.join('/usr/share/nginx/html/upload/', filename)

            # Write to a temporary file to prevent incomplete files from
            # being used.
            temp_file_path = file_path + '~'

            # Finally write the data to a temporary file
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(raw_blob, output_file)

            # Now that we know the file has been fully saved to disk
            # move it into place.
            os.rename(temp_file_path, file_path)
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.ERROR', description=ex)

        # Verify User Session
        cookies = req.headers['SET-COOKIE'].split('=')
        if 'user_uuid' not in cookies or 'token' not in cookies:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COOKIES_PLEASE_RE_LOGIN')

        cnx = mysql.connector.connect(**config.myems_user_db)
        cursor = cnx.cursor()
        query = (" SELECT utc_expires "
                 " FROM tbl_sessions "
                 " WHERE user_uuid = %s AND token = %s")
        cursor.execute(query, (cookies[1], cookies[3],))
        row = cursor.fetchone()

        if row is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COOKIES_PLEASE_RE_LOGIN')
        else:
            utc_expires = row[0]
            if datetime.utcnow() > utc_expires:
                cursor.close()
                cnx.disconnect()
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.USER_SESSION_TIMEOUT')

        cursor.execute(" SELECT id "
                       " FROM tbl_users "
                       " WHERE uuid = %s ",
                       (cookies[1],))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COOKIES_PLEASE_RE_LOGIN')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        file_uuid = str(uuid.uuid4())

        add_values = (" INSERT INTO tbl_help_files "
                      " (file_name, uuid, upload_datetime_utc, user_uuid, file_object ) "
                      " VALUES (%s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (filename,
                                    file_uuid,
                                    datetime.utcnow(),
                                    cookies[1],
                                    raw_blob))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/helpfiles/' + str(new_id)


class HelpFileItem:
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
                                   description='API.INVALID_HELP_FILE_ID')

        cnx = mysql.connector.connect(**config.myems_user_db)
        cursor = cnx.cursor()

        query = (" SELECT uuid, display_name "
                 " FROM tbl_users ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.disconnect()

        user_dict = dict()
        if rows is not None and len(rows) > 0:
            for row in rows:
                user_dict[row[0]] = row[1]

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, file_name, uuid, upload_datetime_utc, user_uuid "
                 " FROM tbl_help_files "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()

        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.HELP_FILE_NOT_FOUND')

        upload_datetime = row[3]
        upload_datetime = upload_datetime.replace(tzinfo=timezone.utc)

        result = {"id": row[0],
                  "file_name": row[1],
                  "uuid": row[2],
                  "upload_datetime": upload_datetime.timestamp() * 1000,
                  "user_display_name": user_dict.get(row[4], None)}
        resp.body = json.dumps(result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_OFFLINE_COST_FILE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT id FROM tbl_help_files WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404,
                                   title='API.NOT_FOUND',
                                   description='API.OFFLINE_COST_FILE_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_help_files WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_204


class HelpFileDownload:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.INVALID_HELP_FILE_ID')
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        query = (" SELECT file_name, file_object "
                 " FROM tbl_help_files "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()
        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404,
                                   title='API.NOT_FOUND',
                                   description='API.HELP_FILE_NOT_FOUND')

        file_name = urllib.parse.quote(row[0])
        disposition = 'attachment; filename*=%s; filename="%s"' % (file_name, file_name)
        # resp.content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        resp.append_header('Content-Disposition', disposition)
        resp.body = row[1]
