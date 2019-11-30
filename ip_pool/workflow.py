import logging
import common

logger = logging.getLogger('main.ip_pool')
pools_uri = 'api/v2/ippool'
groups_uri_base = 'api/v2/ippool/group'


def create_pools(api, workflow_dict):
    logger.info('ip_pool::create_pools')
    for key, value in workflow_dict.items():

        if 'native' in key:
            _junk, _name, _key = key.split('?')
            workflow_dict.update({_name: {'rows': value}})
            workflow_dict.pop(key, None)

            _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)

            # Cycle through the rows and create entries with 'present' set
            if _name == 'ip_pools':
                for row in workflow_dict['ip_pools']['rows']:
                    if 'present' in row['presence']:
                        row.pop('presence', None)
                        _id = common.get_object_id(_ip_pool_db['response'], _key, row[_key])
                        if _id is not None:
                            logger.info('IP Pool: {} already exists with id: {}'.format(row['ipPoolName'], _id))
                            pass
                        else:
                            logger.info('Creating IP Pool: {}'.format(row['ipPoolName']))
                            result = api.custom_caller.call_api('POST', pools_uri, json=common.dot_to_json(row))
                            if result['executionStatusUrl']:
                                logger.debug(api.custom_caller.call_api('GET', result['executionStatusUrl']))


def create_reservations(api, workflow_dict):
    logger.info('ip_pool::create_reservations')
    for key, value in workflow_dict.items():

        if 'native' in key:
            _junk, _name, _key = key.split('?')
            workflow_dict.update({_name: {'rows': value}})
            workflow_dict.pop(key, None)

            _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
            _sites_db = api.sites.get_site()

            if _name == 'ip_groups':
                for row in workflow_dict['ip_groups']['rows']:
                    if 'present' in row['presence']:
                        row.pop('presence', None)
                        _site_id = common.get_object_id(_sites_db['response'], 'name', row['siteName'])
                        _pool_parent_id = common.get_object_id(_ip_pool_db['response'], 'ipPoolName', row['ipPools.parent'])

                        groups_uri = '{}?siteId={}'.format(groups_uri_base, _site_id)
                        _ip_groups_db = api.custom_caller.call_api('GET', groups_uri)
                        _id = common.get_object_id(_ip_groups_db['response'], _key, row['groupName'])

                        row.update({'siteId': _site_id})
                        row.update({'groupOwner': 'DNAC'})
                        row.update({'ipPools.parentUuid': _pool_parent_id})
                        row.update({'ipPools.ipPoolOwner': 'DNAC'})
                        row.pop('ipPools.parent', None)

                        row = _format_ip_pool(row)
                        if _id is not None:
                            logger.info('Reservation: {} already exists with id: {}'.format(row['groupName'], _id))
                            pass
                        else:
                            logger.info('Creating IP Reservation: {}'.format(row['groupName']))
                            result = api.custom_caller.call_api('POST', groups_uri_base, json=common.dot_to_json(row))
                            if result['executionStatusUrl']:
                                logger.debug(api.custom_caller.call_api('GET', result['executionStatusUrl']))


def delete_reservations(api, delete_workflow_dict):
    logger.info('ip_pool::delete_reservations')
    for key, value in delete_workflow_dict.items():

        if 'native' in key:
            _junk, _name, _key = key.split('?')
            delete_workflow_dict.update({_name: {'rows': value}})
            delete_workflow_dict.pop(key, None)

            _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
            _sites_db = api.sites.get_site()
            logger.debug('******** _ip_pool_db *********')
            logger.debug(_ip_pool_db)
            logger.debug('******** _sites_db *********')
            logger.debug(_sites_db)

            if _name == 'ip_groups':
                for row in delete_workflow_dict['ip_groups']['rows']:
                    if 'absent' in row['presence']:
                        row.pop('presence', None)
                        _site_id = common.get_object_id(_sites_db['response'], 'name', row['siteName'])

                        groups_uri = '{}?siteId={}'.format(groups_uri_base, _site_id)
                        _ip_groups_db = api.custom_caller.call_api('GET', groups_uri)
                        _id = common.get_object_id(_ip_groups_db['response'], _key, row['groupName'])

                        if _id is not None:
                            logger.info('Releasing reservation: {} with id: {}'.format(row['groupName'], _id))
                            delete_uri = '{}/{}'.format(groups_uri_base, _id)
                            result = api.custom_caller.call_api('DELETE', delete_uri)
                            if result['executionStatusUrl']:
                                logger.debug(api.custom_caller.call_api('GET', result['executionStatusUrl']))


def delete_pools(api, delete_workflow_dict):
    logger.info('ip_pool::delete_pools')
    for key, value in delete_workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')
            delete_workflow_dict.update({_name: {'rows': value}})
            delete_workflow_dict.pop(key, None)

            _ip_pool_db = api.custom_caller.call_api('GET', pools_uri)
            logger.debug('******** _ip_pool_db *********')
            logger.debug(_ip_pool_db)

            if _name == 'ip_pools':
                for row in delete_workflow_dict['ip_pools']['rows']:
                    _sites_db = api.sites.get_site()
                    if 'absent' in row['presence']:
                        _id = common.get_object_id(_ip_pool_db['response'], _key, row[_key])
                        if _id is not None:
                            logger.info('Deleting: {} with id: {}'.format(row['ipPoolName'], _id))
                            _delete_uri = '{}/{}'.format(pools_uri, _id)
                            result = api.custom_caller.call_api('DELETE', _delete_uri, json=common.dot_to_json(row))
                            if result['executionStatusUrl']:
                                logger.debug(api.custom_caller.call_api('GET', result['executionStatusUrl']))

        else:
            continue


# Local functions
def _format_ip_pool(record):
    record['ipPools.dhcpServerIps'] = record['ipPools.dhcpServerIps'].split(',') if record['ipPools.dhcpServerIps'] else []
    record['ipPools.dnsServerIps'] = record['ipPools.dnsServerIps'].split(',') if record['ipPools.dnsServerIps'] else []
    record['ipPools.gateways'] = record['ipPools.gateways'].split(',') if record['ipPools.gateways'] else []
    record = common.dot_to_json(record)
    # print(record['ipPools'])
    record['ipPools'] = [record['ipPools']]
    # print(record)
    return record


