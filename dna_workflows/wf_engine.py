import yaml
import copy
import urllib3
import logging
import json
import sys
import pkgutil
from dnacentersdk import DNACenterAPI
from ise import ERS

# Settings
urllib3.disable_warnings()
logger = logging.getLogger('main')
module_file_path = './.modules'


def get_module_definition():
    data = pkgutil.get_data(__package__, 'module')
    return yaml.load(data, Loader=yaml.SafeLoader)


def run_wf(_workflow_db):
    apis = run_setup(_workflow_db)

    wf_tasks = _workflow_db['workflow']

    execution_schedule = build_workflow_schedule(wf_tasks)
    for _task in execution_schedule:
        _task_api = _task[3]
        if _task_api in apis.keys():
            api = apis[_task_api]
            execute_task(_task, api, _workflow_db)
        elif 'noop' in _task_api:
            api = 'noop'
            execute_task(_task, api, _workflow_db)
        elif 'offline' in apis.keys():
            api = 'offline'
            execute_task(_task, api, _workflow_db)
        else:
            logger.error('api: {} not found.  Please check your credentials file'.format(_task_api))
            exit()


def build_workflow_schedule(wf_tasks):
    _func_tuple_list = []

    for _func in wf_tasks:
        if 'task' in _func.keys():
            _func_tuple = (_func['stage'], _func['module'], _func['task'], _func['api'])

        _func_tuple_list.append(_func_tuple)

    return sorted(_func_tuple_list, key=lambda tup: tup[0])


def execute_task(_task, api, _workflow_db):
    # Only modules and tasks defined in the module manifest will be loaded/executed
    try:
        with open(module_file_path) as json_file:
            modules = json.load(json_file)
    except FileNotFoundError:
        logger.error('FATAL {} file not found'.format(module_file_path))
        exit()

    _task_stage = _task[0]
    _task_workflow = _task[1]
    _workflow_db.pop('workflow', None)
    _workflow_dict = _workflow_db
    _task_name = _task[2]

    if 'options' in _workflow_db.keys():
        options = _workflow_db['options']
    else:
        options = {}

    if 'noop' in _task_workflow or 'offline' == api:
        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_task_stage, _task_workflow, _task_name))
    else:

        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_task_stage, _task_workflow, _task_name))

        _import = 'import {}'.format(_task_workflow)
        _task_exec = '{}.{}(api, copy.deepcopy({}))'.format(_task_workflow, _task_name, _workflow_dict)

        if _task_workflow in sys.modules:
            pass
        elif _task_workflow in modules['modules'].keys():
            logger.info('Loading module {}'.format(_task_workflow))
            exec(_import, globals())
        else:
            logger.error('Workflow module with name {} is not loaded'.format(_task_workflow))
            return

        if _task_name in modules['modules'][_task_workflow]:
            exec(_task_exec)
        else:
            logger.error('Task {} from workflow module {} is not loaded'.format(_task_name, _task_workflow))
            return


def run_setup(_workflow_db):
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

    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False

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

        # If we didn't find and SDK then exit
        if nosdk:
            logger.error('No valid SDK credentials found')
            exit()

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
