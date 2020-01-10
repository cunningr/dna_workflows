import logging
import common
from time import sleep
from common import report_task_completion
from ip_pool import payload_templates as templates

logger = logging.getLogger('main.ip_pool')
pools_uri = 'api/v2/ippool'
groups_uri_base = 'api/v2/ippool/group'


def create_pools(api, workflow_dict):
    logger.info('ip_pool::create_pools')
    for key, value in workflow_dict.items():

        if 'native' in key:
            _junk, _workflow_name, _table_name = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            if _table_name == 'ip_pools':

                _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)

                for row in value:
                    if 'present' in row['presence']:
                        _id = common.get_object_id(_ip_pool_db['response'], ipPoolName=row['ipPoolName'])
                        if _id is not None:
                            logger.info('IP Pool: {} already exists with id: {}'.format(row['ipPoolName'], _id))
                            pass
                        else:
                            logger.info('Creating IP Pool: {}'.format(row['ipPoolName']))
                            data = templates.ip_pool
                            data['ipPoolName'] = row['ipPoolName']
                            data['ipPoolCidr'] = row['ipPoolCidr']

                            result = api.custom_caller.call_api('POST', pools_uri, json=data)
                            logger.debug(result)
                            if result.response.taskId:
                                common.wait_for_task_completion(api, result.response)


def create_reservations(api, workflow_dict):
    logger.info('ip_pool::create_reservations')
    for key, value in workflow_dict.items():

        if 'native' in key:
            _junk, _workflow_name, _table_name = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            if _table_name == 'ip_reservations':

                _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
                _sites_db = api.sites.get_site()

                for row in value:
                    if 'present' in row['presence']:

                        _site_id = common.get_object_id(_sites_db['response'], siteNameHierarchy=row['siteName'])
                        _pool_parent_id = common.get_object_id(_ip_pool_db['response'], ipPoolName=row['ipPoolsParent'])

                        groups_uri = '{}?siteId={}'.format(groups_uri_base, _site_id)
                        _ip_groups_db = api.custom_caller.call_api('GET', groups_uri)
                        _id = common.get_object_id(_ip_groups_db['response'], groupName=row['groupName'])

                        data = templates.ip_reservation
                        data['siteId'] = _site_id
                        data['ipPools'][0]['parentUuid'] = _pool_parent_id
                        data['groupName'] = row['groupName']
                        data['type'] = row['type']
                        data['ipPools'][0]['ipPoolCidr'] = row['ipReservation']
                        data['ipPools'][0]['parent'] = row['ipPoolsParent']
                        data['ipPools'][0]['dhcpServerIps'] = row['dhcpServerIps'].split(',') if row['dhcpServerIps'] else []
                        if len(data['ipPools'][0]['dhcpServerIps']) > 0:
                            data['ipPools'][0]['configureExternalDhcp']: True
                        data['ipPools'][0]['dnsServerIps'] = row['dnsServerIps'].split(',') if row['dnsServerIps'] else []
                        data['ipPools'][0]['gateways'] = row['gateways'].split(',') if row['gateways'] else []

                        if _id is not None:
                            logger.info('Reservation: {} already exists with id: {}'.format(row['groupName'], _id))
                            pass
                        else:
                            logger.info('Creating IP Reservation: {}'.format(row['groupName']))
                            result = api.custom_caller.call_api('POST', groups_uri_base, json=data)
                            logger.debug(result)
                            if result.response.taskId:
                                common.wait_for_task_completion(api, result.response)


def delete_reservations(api, delete_workflow_dict):
    logger.info('ip_pool::delete_reservations')
    for key, value in delete_workflow_dict.items():

        if 'native' in key:
            _junk, _workflow_name, _table_name = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            if _table_name == 'ip_reservations':

                _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
                _sites_db = api.sites.get_site()
                logger.debug('******** _ip_pool_db *********')
                logger.debug(_ip_pool_db)
                logger.debug('******** _sites_db *********')
                logger.debug(_sites_db)

                for row in value:
                    if 'absent' in row['presence']:
                        _site_id = common.get_object_id(_sites_db['response'], siteNameHierarchy=row['siteName'])

                        groups_uri = '{}?siteId={}'.format(groups_uri_base, _site_id)
                        _ip_groups_db = api.custom_caller.call_api('GET', groups_uri)
                        _id = common.get_object_id(_ip_groups_db['response'], groupName=row['groupName'])

                        if _id is not None:
                            logger.info('Releasing reservation: {} with id: {}'.format(row['groupName'], _id))
                            delete_uri = '{}/{}'.format(groups_uri_base, _id)
                            result = api.custom_caller.call_api('DELETE', delete_uri)
                            logger.debug(result)
                            if result.response.taskId:
                                common.wait_for_task_completion(api, result.response)


def delete_pools(api, workflow_dict):
    logger.info('ip_pool::delete_pools')
    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _workflow_name, _table_name = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            if _table_name == 'ip_pools':

                _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
                logger.debug(_ip_pool_db)

                for row in value:
                    _sites_db = api.sites.get_site()
                    if 'absent' in row['presence']:
                        _id = common.get_object_id(_ip_pool_db['response'], ipPoolName=row['ipPoolName'])
                        if _id is not None:
                            logger.info('Deleting: {} with id: {}'.format(row['ipPoolName'], _id))
                            _delete_uri = '{}/{}'.format(pools_uri, _id)
                            result = api.custom_caller.call_api('DELETE', _delete_uri, json=common.dot_to_json(row))

                            if result.response.taskId:
                                common.wait_for_task_completion(api, result.response)
            else:
                continue


# Local functions
