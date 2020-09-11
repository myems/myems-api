import falcon
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
import combinedequipment
import contact
import costcenter
import datasource
import distributioncircuit
import distributionsystem
import emailmessage
import emailserver
import energycategory
import energyflowdiagram
import energyitem
import equipment
import gateway
import gsmmodem
import knowledgefile
import meter
import offlinemeter
import offlinemeterfile
import point
import privilege
import rule
import sensor
import shopfloor
import space
import store
import storetype
import tariff
import tenant
import tenanttype
import textmessage
import timezone
import user
import virtualmeter
import webmessage
import wechatmessage
import version
from reports import meterenergy
########################################################################################################################
# BEGIN imports for Enterprise Version
########################################################################################################################

########################################################################################################################
# END imports for Enterprise Version
########################################################################################################################


# https://github.com/lwcolton/falcon-cors
# https://github.com/yohanboniface/falcon-multipart
cors = CORS(allow_all_origins=True,
            allow_credentials_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True)
api = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])


########################################################################################################################
# Routes for System Configuration
########################################################################################################################

api.add_route('/combinedequipments',
              combinedequipment.CombinedEquipmentCollection())
api.add_route('/combinedequipments/{id_}',
              combinedequipment.CombinedEquipmentItem())
api.add_route('/combinedequipments/{id_}/equipments',
              combinedequipment.CombinedEquipmentEquipmentCollection())
api.add_route('/combinedequipments/{id_}/equipments/{eid}',
              combinedequipment.CombinedEquipmentEquipmentItem())
api.add_route('/combinedequipments/{id_}/meters',
              combinedequipment.CombinedEquipmentMeterCollection())
api.add_route('/combinedequipments/{id_}/meters/{mid}',
              combinedequipment.CombinedEquipmentMeterItem())
api.add_route('/combinedequipments/{id_}/offlinemeters',
              combinedequipment.CombinedEquipmentOfflineMeterCollection())
api.add_route('/combinedequipments/{id_}/offlinemeters/{mid}',
              combinedequipment.CombinedEquipmentOfflineMeterItem())
api.add_route('/combinedequipments/{id_}/parameters',
              combinedequipment.CombinedEquipmentParameterCollection())
api.add_route('/combinedequipments/{id_}/parameters/{pid}',
              combinedequipment.CombinedEquipmentParameterItem())
api.add_route('/combinedequipments/{id_}/virtualmeters',
              combinedequipment.CombinedEquipmentVirtualMeterCollection())
api.add_route('/combinedequipments/{id_}/virtualmeters/{mid}',
              combinedequipment.CombinedEquipmentVirtualMeterItem())

api.add_route('/contacts',
              contact.ContactCollection())
api.add_route('/contacts/{id_}',
              contact.ContactItem())

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

api.add_route('/distributioncircuits',
              distributioncircuit.DistributionCircuitCollection())
api.add_route('/distributioncircuits/{id_}',
              distributioncircuit.DistributionCircuitItem())
api.add_route('/distributioncircuits/{id_}/points',
              distributioncircuit.DistributionCircuitPointCollection())
api.add_route('/distributioncircuits/{id_}/points/{pid}',
              distributioncircuit.DistributionCircuitPointItem())

api.add_route('/distributionsystems',
              distributionsystem.DistributionSystemCollection())
api.add_route('/distributionsystems/{id_}',
              distributionsystem.DistributionSystemItem())
api.add_route('/distributionsystems/{id_}/distributioncircuits',
              distributionsystem.DistributionSystemDistributionCircuitCollection())

api.add_route('/emailmessages/from/{startdate}/to/{enddate}',
              emailmessage.EmailMessageCollection())
api.add_route('/emailmessages/{id_}',
              emailmessage.EmailMessageItem())

api.add_route('/emailservers',
              emailserver.EmailServerCollection())
api.add_route('/emailservers/{id_}',
              emailserver.EmailServerItem())

api.add_route('/energycategories',
              energycategory.EnergyCategoryCollection())
api.add_route('/energycategories/{id_}',
              energycategory.EnergyCategoryItem())

api.add_route('/energyflowdiagrams',
              energyflowdiagram.EnergyFlowDiagramCollection())
api.add_route('/energyflowdiagrams/{id_}',
              energyflowdiagram.EnergyFlowDiagramItem())
api.add_route('/energyflowdiagrams/{id_}/links',
              energyflowdiagram.EnergyFlowDiagramLinkCollection())
api.add_route('/energyflowdiagrams/{id_}/links/{lid}',
              energyflowdiagram.EnergyFlowDiagramLinkItem())
api.add_route('/energyflowdiagrams/{id_}/nodes',
              energyflowdiagram.EnergyFlowDiagramNodeCollection())
api.add_route('/energyflowdiagrams/{id_}/nodes/{nid}',
              energyflowdiagram.EnergyFlowDiagramNodeItem())

api.add_route('/energyitems',
              energyitem.EnergyItemCollection())
api.add_route('/energyitems/{id_}',
              energyitem.EnergyItemItem())

api.add_route('/equipments',
              equipment.EquipmentCollection())
api.add_route('/equipments/{id_}',
              equipment.EquipmentItem())
api.add_route('/equipments/{id_}/meters',
              equipment.EquipmentMeterCollection())
api.add_route('/equipments/{id_}/meters/{mid}',
              equipment.EquipmentMeterItem())
api.add_route('/equipments/{id_}/offlinemeters',
              equipment.EquipmentOfflineMeterCollection())
api.add_route('/equipments/{id_}/offlinemeters/{mid}',
              equipment.EquipmentOfflineMeterItem())
api.add_route('/equipments/{id_}/parameters',
              equipment.EquipmentParameterCollection())
api.add_route('/equipments/{id_}/parameters/{pid}',
              equipment.EquipmentParameterItem())
api.add_route('/equipments/{id_}/virtualmeters',
              equipment.EquipmentVirtualMeterCollection())
api.add_route('/equipments/{id_}/virtualmeters/{mid}',
              equipment.EquipmentVirtualMeterItem())

api.add_route('/gateways',
              gateway.GatewayCollection())
api.add_route('/gateways/{id_}',
              gateway.GatewayItem())
api.add_route('/gateways/{id_}/datasources',
              gateway.GatewayDataSourceCollection())

api.add_route('/gsmmodems',
              gsmmodem.GSMModemCollection())
api.add_route('/gsmmodems/{id_}',
              gsmmodem.GSMModemItem())

api.add_route('/knowledgefiles',
              knowledgefile.KnowledgeFileCollection())
api.add_route('/knowledgefiles/{id_}',
              knowledgefile.KnowledgeFileItem())
api.add_route('/knowledgefiles/{id_}/restore',
              knowledgefile.KnowledgeFileRestore())

api.add_route('/meters',
              meter.MeterCollection())
api.add_route('/meters/{id_}',
              meter.MeterItem())
api.add_route('/meters/{id_}/children',
              meter.MeterChildrenCollection())
api.add_route('/meters/{id_}/points',
              meter.MeterPointCollection())
api.add_route('/meters/{id_}/points/{pid}',
              meter.MeterPointItem())

api.add_route('/offlinemeters',
              offlinemeter.OfflineMeterCollection())
api.add_route('/offlinemeters/{id_}',
              offlinemeter.OfflineMeterItem())

api.add_route('/offlinemeterfiles',
              offlinemeterfile.OfflineMeterFileCollection())
api.add_route('/offlinemeterfiles/{id_}',
              offlinemeterfile.OfflineMeterFileItem())

api.add_route('/points',
              point.PointCollection())
api.add_route('/points/{id_}',
              point.PointItem())

api.add_route('/privileges',
              privilege.PrivilegeCollection())
api.add_route('/privileges/{id_}',
              privilege.PrivilegeItem())

api.add_route('/rules',
              rule.RuleCollection())
api.add_route('/rules/{id_}',
              rule.RuleItem())

api.add_route('/sensors',
              sensor.SensorCollection())
api.add_route('/sensors/{id_}',
              sensor.SensorItem())
api.add_route('/sensors/{id_}/points',
              sensor.SensorPointCollection())
api.add_route('/sensors/{id_}/points/{pid}',
              sensor.SensorPointItem())

api.add_route('/shopfloors',
              shopfloor.ShopfloorCollection())
api.add_route('/shopfloors/{id_}',
              shopfloor.ShopfloorItem())
api.add_route('/shopfloors/{id_}/equipments',
              shopfloor.ShopfloorEquipmentCollection())
api.add_route('/shopfloors/{id_}/equipments/{eid}',
              shopfloor.ShopfloorEquipmentItem())
api.add_route('/shopfloors/{id_}/meters',
              shopfloor.ShopfloorMeterCollection())
api.add_route('/shopfloors/{id_}/meters/{mid}',
              shopfloor.ShopfloorMeterItem())
api.add_route('/shopfloors/{id_}/offlinemeters',
              shopfloor.ShopfloorOfflineMeterCollection())
api.add_route('/shopfloors/{id_}/offlinemeters/{mid}',
              shopfloor.ShopfloorOfflineMeterItem())
api.add_route('/shopfloors/{id_}/points',
              shopfloor.ShopfloorPointCollection())
api.add_route('/shopfloors/{id_}/points/{pid}',
              shopfloor.ShopfloorPointItem())
api.add_route('/shopfloors/{id_}/sensors',
              shopfloor.ShopfloorSensorCollection())
api.add_route('/shopfloors/{id_}/sensors/{sid}',
              shopfloor.ShopfloorSensorItem())
api.add_route('/shopfloors/{id_}/virtualmeters',
              shopfloor.ShopfloorVirtualMeterCollection())
api.add_route('/shopfloors/{id_}/virtualmeters/{mid}',
              shopfloor.ShopfloorVirtualMeterItem())

api.add_route('/spaces',
              space.SpaceCollection())
api.add_route('/spaces/{id_}',
              space.SpaceItem())
api.add_route('/spaces/{id_}/children',
              space.SpaceChildrenCollection())
api.add_route('/spaces/{id_}/combinedequipments',
              space.SpaceCombinedEquipmentCollection())
api.add_route('/spaces/{id_}/combinedequipments/{eid}',
              space.SpaceCombinedEquipmentItem())
api.add_route('/spaces/{id_}/equipments',
              space.SpaceEquipmentCollection())
api.add_route('/spaces/{id_}/equipments/{eid}',
              space.SpaceEquipmentItem())
api.add_route('/spaces/{id_}/meters',
              space.SpaceMeterCollection())
api.add_route('/spaces/{id_}/meters/{mid}',
              space.SpaceMeterItem())
api.add_route('/spaces/{id_}/offlinemeters',
              space.SpaceOfflineMeterCollection())
api.add_route('/spaces/{id_}/offlinemeters/{mid}',
              space.SpaceOfflineMeterItem())
api.add_route('/spaces/{id_}/points',
              space.SpacePointCollection())
api.add_route('/spaces/{id_}/points/{pid}',
              space.SpacePointItem())
api.add_route('/spaces/{id_}/sensors',
              space.SpaceSensorCollection())
api.add_route('/spaces/{id_}/sensors/{sid}',
              space.SpaceSensorItem())
api.add_route('/spaces/{id_}/shopfloors',
              space.SpaceShopfloorCollection())
api.add_route('/spaces/{id_}/shopfloors/{sid}',
              space.SpaceShopfloorItem())
api.add_route('/spaces/{id_}/stores',
              space.SpaceStoreCollection())
api.add_route('/spaces/{id_}/stores/{tid}',
              space.SpaceStoreItem())
api.add_route('/spaces/{id_}/tenants',
              space.SpaceTenantCollection())
api.add_route('/spaces/{id_}/tenants/{tid}',
              space.SpaceTenantItem())
api.add_route('/spaces/{id_}/virtualmeters',
              space.SpaceVirtualMeterCollection())
api.add_route('/spaces/{id_}/virtualmeters/{mid}',
              space.SpaceVirtualMeterItem())
api.add_route('/spaces/tree',
              space.SpaceTreeCollection())

api.add_route('/stores',
              store.StoreCollection())
api.add_route('/stores/{id_}',
              store.StoreItem())
api.add_route('/stores/{id_}/meters',
              store.StoreMeterCollection())
api.add_route('/stores/{id_}/meters/{mid}',
              store.StoreMeterItem())
api.add_route('/stores/{id_}/offlinemeters',
              store.StoreOfflineMeterCollection())
api.add_route('/stores/{id_}/offlinemeters/{mid}',
              store.StoreOfflineMeterItem())
api.add_route('/stores/{id_}/points',
              store.StorePointCollection())
api.add_route('/stores/{id_}/points/{pid}',
              store.StorePointItem())
api.add_route('/stores/{id_}/sensors',
              store.StoreSensorCollection())
api.add_route('/stores/{id_}/sensors/{sid}',
              store.StoreSensorItem())
api.add_route('/stores/{id_}/virtualmeters',
              store.StoreVirtualMeterCollection())
api.add_route('/stores/{id_}/virtualmeters/{mid}',
              store.StoreVirtualMeterItem())

api.add_route('/storetypes',
              storetype.StoreTypeCollection())
api.add_route('/storetypes/{id_}',
              storetype.StoreTypeItem())

api.add_route('/tariffs',
              tariff.TariffCollection())
api.add_route('/tariffs/{id_}',
              tariff.TariffItem())

api.add_route('/tenants',
              tenant.TenantCollection())
api.add_route('/tenants/{id_}',
              tenant.TenantItem())
api.add_route('/tenants/{id_}/meters',
              tenant.TenantMeterCollection())
api.add_route('/tenants/{id_}/meters/{mid}',
              tenant.TenantMeterItem())
api.add_route('/tenants/{id_}/offlinemeters',
              tenant.TenantOfflineMeterCollection())
api.add_route('/tenants/{id_}/offlinemeters/{mid}',
              tenant.TenantOfflineMeterItem())
api.add_route('/tenants/{id_}/points',
              tenant.TenantPointCollection())
api.add_route('/tenants/{id_}/points/{pid}',
              tenant.TenantPointItem())
api.add_route('/tenants/{id_}/sensors',
              tenant.TenantSensorCollection())
api.add_route('/tenants/{id_}/sensors/{sid}',
              tenant.TenantSensorItem())
api.add_route('/tenants/{id_}/virtualmeters',
              tenant.TenantVirtualMeterCollection())
api.add_route('/tenants/{id_}/virtualmeters/{mid}',
              tenant.TenantVirtualMeterItem())

api.add_route('/tenanttypes',
              tenanttype.TenantTypeCollection())
api.add_route('/tenanttypes/{id_}',
              tenanttype.TenantTypeItem())

api.add_route('/textmessages/from/{startdate}/to/{enddate}',
              textmessage.TextMessageCollection())
api.add_route('/textmessages/{id_}',
              textmessage.TextMessageItem())

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

api.add_route('/webmessages/from/{startdate}/to/{enddate}',
              webmessage.WebMessageCollection())
api.add_route('/webmessagesnew',
              webmessage.WebMessageStatusNewCollection())
api.add_route('/webmessages/{id_}',
              webmessage.WebMessageItem())

api.add_route('/wechatmessages/from/{startdate}/to/{enddate}',
              wechatmessage.WechatMessageCollection())
api.add_route('/wechatmessages/{id_}',
              wechatmessage.WechatMessageItem())

api.add_route('/version',
              version.VersionItem())


########################################################################################################################
# Routes for Reporting
########################################################################################################################
api.add_route('/reports/meterenergy',
              meterenergy.Reporting())

########################################################################################################################
# BEGIN Routes for Enterprise Version
########################################################################################################################

########################################################################################################################
# END Routes for Enterprise Version
########################################################################################################################


# from waitress import serve
# serve(api, host='0.0.0.0', port=8886)
