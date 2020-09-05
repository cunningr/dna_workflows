import yaml
import traceback
import copy
import urllib3
import logging
import coloredlogs
import json
import sys
import pkgutil
from dnacentersdk import DNACenterAPI
from dna_workflows import package_tools
from ise import ERS

# Settings
urllib3.disable_warnings()
logger = logging.getLogger('main')
module_file_path = './.modules'


def get_module_definition():
    data = pkgutil.get_data(__package__, 'module')
    return yaml.load(data, Loader=yaml.SafeLoader)


def run_wf(_workflow_db, headless=False):
    apis = run_setup(_workflow_db, headless=headless)

    wf_tasks = _workflow_db['workflow']

    execution_schedule = build_workflow_schedule(wf_tasks)
    _report = []
    for _task in execution_schedule:
        _task_api = _task[3]
        _mod_task = '{}.{}'.format(_task[1], _task[2])
        if _task_api in apis.keys():
            api = apis[_task_api]
            try:
                _result = execute_task(_task, api, _workflow_db)
                # _mod_task = '{}.{}'.format(_task[1], _task[2])
                if _result in ['FAILURE', 'SUCCESS', 'ERROR', 'PARTIAL_FAILURE', 'NOOP']:
                    _report.append({'stage': _task[0], 'task': _mod_task, 'result': _result})
                else:
                    _report.append({'stage': _task[0], 'task': _mod_task, 'result': 'UNKNOWN'})
            except Exception as e:
                logger.error('TASK EXCEPTION: API {}, Task {}'.format(_task_api, _task))
                logger.error('**** TRACEBACK ***\n\n {}'.format(traceback.format_exc()))
        # elif 'noop' in _task_api:
        #     api = 'noop'
        #     execute_task(_task, api, _workflow_db)
        elif 'offline' in apis.keys():
            api = 'offline'
            _result = execute_task(_task, api, _workflow_db)
            _report.append({'stage': 0, 'task': _mod_task, 'result': _result})
        else:
            logger.error('api: {} not found.  Please check your credentials file'.format(_task_api))
            exit()

    return _report


def build_workflow_schedule(wf_tasks):
    _func_tuple_list = []

    for _func in wf_tasks:
        if 'task' in _func.keys():
            _func_tuple = (_func['stage'], _func['module'], _func['task'], _func['api'])

        _func_tuple_list.append(_func_tuple)

    return sorted(_func_tuple_list, key=lambda tup: tup[0])


def execute_task(_task, api, _workflow_db):

    _stage = _task[0]
    _module = _task[1]
    _workflow_dict = _workflow_db
    _task = _task[2]

    if 'options' in _workflow_db.keys():
        options = _workflow_db['options']
    else:
        options = {}

    if 'noop' in _workflow_db['options'] or 'offline' == api:
        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_stage, _module, _task))
        return 'NOOP'
    else:

        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_stage, _module, _task))

        return package_tools.execute_task(api, _module, _task, _workflow_dict)


def run_setup(_workflow_db, headless=True):
    global logger

    if 'options' in _workflow_db.keys():
        options = _workflow_db['options']
    else:
        options = {}

    # Setup logging
    if 'logging' in options.keys():
        user_level = options['logging'].upper()
        level = logging.getLevelName(user_level)
    else:
        level = logging.getLevelName('INFO')

    coloredlogs.install(level=level, logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        field_styles={'asctime': {'color': 'green'}, 'hostname': {'color': 'magenta'},
                                        'levelname': {'bold': True, 'color': 'black'}, 'name': {'color': 'yellow'},
                                        'programname': {'color': 'cyan'}, 'username': {'color': 'yellow'}})

    if headless:
        logger.info('DNA Workflow running in HEADLESS mode')
        fh = logging.FileHandler('workflow.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(level)
        logging.getLogger().addHandler(fh)

    api = {}
    if 'offline' in _workflow_db['api_creds'].keys():
        api = {'offline': True}
    else:
        nosdk = True
        if 'dnacentersdk' in _workflow_db['api_creds'].keys():
            _sdk = sdk_setup_dnacentersdk(_workflow_db['api_creds'])
            api.update({'dnacentersdk': _sdk})
            nosdk = False
        if 'isepac' in _workflow_db['api_creds'].keys():
            _sdk = sdk_setup_isepac(_workflow_db['api_creds'])
            api.update({'isepac': _sdk})
            nosdk = False

        # If we didn't find an SDK then exit
        if nosdk:
            logger.error('No valid SDK credentials found')
            exit()

    _workflow_db['workflow'] = package_tools.transform_wf_tasks(_workflow_db)

    return api


def get_options(_workflow_db, option):

    if 'options' in _workflow_db.keys():
        options = _workflow_db['options']
    else:
        return None

    if option in options.keys():
        return options[option]
    else:
        return None


def sdk_setup_dnacentersdk(api_creds):
    try:
        username = api_creds['dnacentersdk']['username']
        password = api_creds['dnacentersdk']['password']
        base_url = api_creds['dnacentersdk']['base_url']
        version = api_creds['dnacentersdk']['api_version']
        verify = str(api_creds['dnacentersdk']['verify']).lower() in ['true']
        api = DNACenterAPI(base_url=base_url, version=version, username=username, password=password, verify=verify)
        logger.info('API connectivity established with dnacentersdk')
        return api
    except Exception as e:
        logger.error('error connecting to dnacentersdk.  Please verify connectivity, username and password')
        logger.error(e)
        exit()


def sdk_setup_isepac(api_creds):
    try:
        username = api_creds['isepac']['username']
        password = api_creds['isepac']['password']
        host = api_creds['isepac']['host']
        verify = str(api_creds['isepac']['verify']).lower() in ['true']
        disable_warnings = str(api_creds['isepac']['disable_warnings']).lower() in ['true']
        api = ERS(ise_node=host, ers_user=username, ers_pass=password, verify=verify, disable_warnings=disable_warnings)
        logger.info('API connectivity established with isepac')
        return api
    except Exception as e:
        logger.error('error connecting to isepac.  Please verify connectivity, username and password')
        logger.error(e)
        exit()
