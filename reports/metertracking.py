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
    # Step 2: query the meters
    # Step 3: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        print(req.params)
        space_id = req.params.get('spaceid')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if space_id is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_SPACE_ID')
        else:
            space_id = str.strip(space_id)
            if not space_id.isdigit() or int(space_id) <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_SPACE_ID')

        ################################################################################################################
        # Step 2: query the meters
        ################################################################################################################
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)
        meter_list = list()

        cursor.execute(" SELECT m.id, m.name AS meter_name, s.name AS space_name, "
                       "        cc.name AS cost_center_name, ec.name AS energy_category_name, "
                       "         m.description "
                       " FROM tbl_spaces s, tbl_spaces_meters sm, tbl_meters m, tbl_cost_centers cc, "
                       "      tbl_energy_categories ec "
                       " WHERE s.id = %s AND sm.space_id = s.id AND sm.meter_id = m.id "
                       "       AND m.cost_center_id = cc.id AND m.energy_category_id = ec.id ", (space_id,))
        rows_meters = cursor.fetchall()
        if rows_meters is not None and len(rows_meters) > 0:
            for row in rows_meters:
                meter_list.append({"id": row['id'],
                                   "meter_name": row['meter_name'],
                                   "space_name": row['space_name'],
                                   "cost_center_name": row['cost_center_name'],
                                   "energy_category_name": row['energy_category_name'],
                                   "description": row['description']})

        if cursor:
            cursor.close()
        if cnx:
            cnx.disconnect()

        ################################################################################################################
        # Step 5: construct the report
        ################################################################################################################

        resp.body = json.dumps(meter_list)
