import logging
import common

logger = logging.getLogger('main.reports')


def create_reports(api, workflow_dict):
    logger.info('reports::create_pools')
    for key, value in workflow_dict.items():

        if 'native' in key:
            _junk, _name, _key = key.split('?')
            workflow_dict.update({_name: {'rows': value}})
            workflow_dict.pop(key, None)

            # Cycle through the rows and create entries with 'present' set
            if _name == 'reports':
                for row in workflow_dict['reports']['rows']:
                    if row['presence'] == 'present':
                        if row['report'] == 'dnac_versions':
                            _create_dnac_versions_report(api)
                        if row['report'] == 'dnac_device_inventory':
                            _create_dnac_inventory_report(api)


def hello_world(api, workflow_dict):
    logger.info('reports::hello_world')
    for key, value in workflow_dict.items():
        logger.info('Found table: {} with rows: '.format(key))
        for row in value:
            logger.info('{}'.format(row))


# Reports
def _create_dnac_versions_report(api):
    logger.info('Generating report: reports::dnac_versions')


def _create_dnac_inventory_report(api):
    logger.info('Generating report: reports::dnac_device_inventory')

