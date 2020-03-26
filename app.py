import falcon
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
import costcenter
import datasource
import energycategory
import meter
import offlinemeter
import privilege
import point
import tariff
import timezone
import user
import virtualmeter


# https://github.com/lwcolton/falcon-cors
# https://github.com/yohanboniface/falcon-multipart
cors = CORS(allow_all_origins=True,
            allow_credentials_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True)
api = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])

api.add_route('/costcenters',
              costcenter.CostCenterCollection())
api.add_route('/costcenters/{id_}',
              costcenter.CostCenterItem())
api.add_route('/costcenters/{id_}/tariffs',
              costcenter.CostCenterTariffCollection())
api.add_route('/costcenters/{id_}/tariffs/{tid}',
              costcenter.CostCenterTariffItem())

api.add_route('/datasources',
              datasource.DataSourceCollection())
api.add_route('/datasources/{id_}',
              datasource.DataSourceItem())
api.add_route('/datasources/{id_}/points',
              datasource.DataSourcePointCollection())
api.add_route('/datasources/status',
              datasource.DataSourceStatusCollection())

api.add_route('/energycategories',
              energycategory.EnergyCategoryCollection())
api.add_route('/energycategories/{id_}',
              energycategory.EnergyCategoryItem())

api.add_route('/meters',
              meter.MeterCollection())
api.add_route('/meters/{id_}',
              meter.MeterItem())
api.add_route('/meters/{id_}/points',
              meter.MeterPointCollection())
api.add_route('/meters/{id_}/points/{pid}',
              meter.MeterPointItem())

api.add_route('/offlinemeters',
              offlinemeter.OfflineMeterCollection())
api.add_route('/offlinemeters/{id_}',
              offlinemeter.OfflineMeterItem())

api.add_route('/points',
              point.PointCollection())
api.add_route('/points/{id_}',
              point.PointItem())

api.add_route('/privileges',
              privilege.PrivilegeCollection())
api.add_route('/privileges/{id_}',
              privilege.PrivilegeItem())

api.add_route('/tariffs',
              tariff.TariffCollection())
api.add_route('/tariffs/{id_}',
              tariff.TariffItem())

api.add_route('/timezones',
              timezone.TimezoneCollection())
api.add_route('/timezones/{id_}',
              timezone.TimezoneItem())

api.add_route('/users',
              user.UserCollection())
api.add_route('/users/{id_}',
              user.UserItem())
api.add_route('/users/login',
              user.UserLogin())
api.add_route('/users/logout',
              user.UserLogout())
api.add_route('/users/resetpassword',
              user.ResetPassword())
api.add_route('/users/changepassword',
              user.ChangePassword())

api.add_route('/virtualmeters',
              virtualmeter.VirtualMeterCollection())
api.add_route('/virtualmeters/{id_}',
              virtualmeter.VirtualMeterItem())

# from waitress import serve
# serve(api, host='0.0.0.0', port=8886)
