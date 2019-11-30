
import logging
import common

logger = logging.getLogger('main.discovery')


def create_global_credentials(api, workflow_dict):
    logger.info('discovery::create_global_credentials')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            for row in value:
                if 'present' in row['presence'] and 'writeCommunity' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('SNMPV2_WRITE_COMMUNITY')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('SNMPV2_WRITE_COMMUNITY exists with id: {}'.format(_id))
                    else:
                        result = api.network_discovery.create_snmp_write_community(payload=[common.dot_to_json(row)])
                        logger.debug(api.custom_caller.call_api('GET', result['response']['url']))
                elif 'present' in row['presence'] and 'readCommunity' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('SNMPV2_READ_COMMUNITY')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('SNMPV2_READ_COMMUNITY exists with id: {}'.format(_id))
                    else:
                        result = api.network_discovery.create_snmp_read_community(payload=[common.dot_to_json(row)])
                        logger.debug(api.custom_caller.call_api('GET', result['response']['url']))
                elif 'present' in row['presence'] and 'username' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('CLI')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('CLI exists with id: {}'.format(_id))
                    else:
                        result = api.network_discovery.create_cli_credentials(payload=[common.dot_to_json(row)])
                        logger.debug(api.custom_caller.call_api('GET', result['response']['url']))


def delete_global_credentials(api, workflow_dict):
    logger.info('discovery::delete_global_credentials')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            for row in value:
                if 'absent' in row['presence'] and 'writeCommunity' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('SNMPV2_WRITE_COMMUNITY')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('Deleting SNMPV2_WRITE_COMMUNITY with id: {}'.format(_id))
                        api.network_discovery.delete_global_credentials_by_id(_id)
                    else:
                        logger.info('SNMPV2_WRITE_COMMUNITY with description "{}" does not exist'.format(_id))
                elif 'absent' in row['presence'] and 'readCommunity' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('SNMPV2_READ_COMMUNITY')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('Deleting SNMPV2_READ_COMMUNITY with id: {}'.format(_id))
                        api.network_discovery.delete_global_credentials_by_id(_id)
                    else:
                        logger.info('SNMPV2_READ_COMMUNITY with description "{}" does not exist'.format(_id))
                elif 'absent' in row['presence'] and 'username' in row.keys():
                    _creds = api.network_discovery.get_global_credentials('CLI')
                    _id = common.get_object_id(_creds['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('Deleting CLI with id: {}'.format(_id))
                        api.network_discovery.delete_global_credentials_by_id(_id)
                    else:
                        logger.info('CLI with description "{}" does not exist'.format(_id))


def run_discovery(api, workflow_dict):
    logger.info('discovery::run_discovery')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            for row in value:
                if 'present' in row['presence'] and _name == 'discovery':
                    # logger.info(row)
                    _creds = []

                    _cli = api.network_discovery.get_global_credentials('CLI')
                    _id = common.get_object_id(_cli['response'], 'description', row['cli'])
                    _creds.append(_id)

                    _cli = api.network_discovery.get_global_credentials('SNMPV2_READ_COMMUNITY')
                    _id = common.get_object_id(_cli['response'], 'description', row['snmp_ro'])
                    _creds.append(_id)

                    _cli = api.network_discovery.get_global_credentials('SNMPV2_WRITE_COMMUNITY')
                    _id = common.get_object_id(_cli['response'], 'description', row['snmp_rw'])
                    _creds.append(_id)

                    _discovery_range = '{}-{}'.format(row['startIp'], row['endIp'])

                    _discovery = {
                        "discoveryType": row['discoveryType'],
                        "preferredMgmtIPMethod": row['preferredMgmtIPMethod'],
                        "ipAddressList": _discovery_range,
                        "protocolOrder": "ssh",
                        "timeout": 5,
                        "retry": 3,
                        "globalCredentialIdList": _creds,
                        "name": row['name']
                    }

                    logger.info('Adding discovery ... ')
                    result = api.network_discovery.start_discovery(payload=_discovery)
                    logger.info(result)


def delete_discovery(api, workflow_dict):
    logger.info('discovery::delete_discovery')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            # Cycle through the rows and create entries with 'present' set
            for row in value:
                logger.info(_name)
                if 'absent' in row['presence'] and _name == 'discovery':
                    _discovery = api.custom_caller.call_api('GET', '/api/v1/discovery/1/10')
                    _id = common.get_object_id(_discovery['response'], _key, row[_key])
                    if _id is not None:
                        logger.info('Deleting discovery with id: {}'.format(_id))
                        api.network_discovery.delete_discovery_by_id(_id)
                    else:
                        logger.info('Discovery with name "{}" does not exist'.format(_id))
