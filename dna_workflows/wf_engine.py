import cx_usage_stats
import yaml
import copy
import urllib3
from dnacentersdk import DNACenterAPI
import logging
import json
import sys
import pkgutil

# Settings
urllib3.disable_warnings()
logger = logging.getLogger('main')
module_file_path = './.modules'


def get_module_definition():
    data = pkgutil.get_data(__package__, 'module')
    return yaml.load(data, Loader=yaml.SafeLoader)


def run_wf(_workflow_db):
    api = run_setup(_workflow_db)
    # workflow_mods = []

    wf_tasks = _workflow_db['workflow']

    execution_schedule = build_workflow_schedule(wf_tasks)
    for _task in execution_schedule:
        execute_workflow(_task, api, _workflow_db)

    if not get_options(_workflow_db, 'incognito'):
        usage, stats = build_usage_stats(wf_tasks, '')
        post_tool_stats(usage, stats)


def build_usage_stats(tasks, statistics):
    logger.debug('RAW FUNCTIONS DAT:')
    logger.debug(tasks)

    usage = []
    for row in tasks:
        task = '{}::{}'.format(row['module'], row['task'])
        usage.append({task: 'ENABLED'})

    stats = {'summary_count': '0'}
    return usage, stats


def post_tool_stats(usage, stats):
    tool_usage_url = "http://cx-emear-tools-stats.cisco.com/submit_tool_usage"
    submit_result = cx_usage_stats.submit_usage_data("DnaWorkflows", tool_usage_url, usage, stats)

    logger.debug(submit_result)

    if submit_result["upload_status"] == "Success":
        message = "Usage statistics successfully submitted"
        logger.info(message)
    else:
        message = "Failure during submission of usage statistics (can safely be ignored)"
        logger.info(message)


def build_workflow_schedule(wf_tasks):
    _func_tuple_list = []

    for _func in wf_tasks:
        if 'task' in _func.keys():
            _func_tuple = (_func['stage'], _func['module'], _func['task'])

        _func_tuple_list.append(_func_tuple)

    return sorted(_func_tuple_list, key=lambda tup: tup[0])


def execute_workflow(_task, api, _workflow_db):
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

    if 'noop' in options.keys() or api is None:
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

    if 'dnacentersdk' in _workflow_db['api_creds'].keys():
        username = _workflow_db['api_creds']['dnacentersdk']['username']
        password = _workflow_db['api_creds']['dnacentersdk']['password']
        base_url = _workflow_db['api_creds']['dnacentersdk']['base_url']
        version = _workflow_db['api_creds']['dnacentersdk']['api_version']
        verify = str(_workflow_db['api_creds']['dnacentersdk']['verify']).lower() in ['true']

    if 'offline' in _workflow_db['api_creds'].keys():
        api = None
    else:
        api = DNACenterAPI(base_url=base_url, version=version, username=username, password=password, verify=verify)

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
