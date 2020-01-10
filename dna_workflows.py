import tables
import copy
import urllib3
import argparse
from dnacentersdk import DNACenterAPI
import logging
import common

# Settings
urllib3.disable_warnings()


def main():

    workflow_funcs = []
    for workflow in workflow_db['workflows']['workflow']:
        if 'enabled' in workflow['Status']:
            for key, value in workflow_db[workflow['Name']].items():
                if 'control' in key:
                    for _func in value:
                        _func.update({'workflow': workflow['Name']})
                        workflow_funcs.append(_func)

    execution_schedule = build_workflow_schedule(workflow_funcs)
    for _task in execution_schedule:
        execute_workflow(_task)


def build_workflow_schedule(workflow_func):

    _func_tuple_list = []

    for _func in workflow_func:
        if 'Function' in _func.keys():
            logger.warning(
                'key "Function" use in workflow control table "{}" will be deprecated.  Please use "Task" instead.'.format(_func['workflow'])
            )
            _func_tuple = (_func['Stage'], _func['Status'], _func['workflow'], _func['Function'])
        elif 'Task' in _func.keys():
            _func_tuple = (_func['Stage'], _func['Status'], _func['workflow'], _func['Task'])

        _func_tuple_list.append(_func_tuple)

    return sorted(_func_tuple_list, key=lambda tup: tup[0])


def execute_workflow(_task):

    if args.noop:
        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_task[0], _task[2], _task[3]))
    elif _task[1] == 'enabled':
        logger.info('Executing STAGE-{} workflow: {}::{}'.format(_task[0], _task[2], _task[3]))
        _import = 'import {}'.format(_task[2])
        exec(_import, globals())
        _workflow_name = _task[2]
        _workflow_dict = workflow_db[_workflow_name]
        _workflow_func = _task[3]
        _workflow = '{}.{}(api, copy.deepcopy({}))'.format(_workflow_name, _workflow_func, _workflow_dict)
        exec(_workflow)


# Check for args
parser = argparse.ArgumentParser()
parser.add_argument("--db", help=".xlsx file to use as the db")
parser.add_argument("--debug", action='store_true', help="Enable debug level messages mode")
parser.add_argument("--noop", action='store_true', help="Run the scheduling logic but do not execute any workflows")
parser.add_argument("--offline", action='store_true', help="Creates a 'dummy' api object, useful for workflow development")
args = parser.parse_args()

# Set db file
if args.db:
    workflow_db = tables.load_xl_db(args.db)
else:
    workflow_db = tables.load_xl_db('dna_workflow_db.xlsx')

# Setup logging
if args.debug:
    level = logging.getLevelName('DEBUG')
else:
    level = logging.getLevelName('INFO')

logger = logging.getLogger('main')
logger.setLevel(level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

username = workflow_db['workflows']['api_creds'][0]['username']
password = workflow_db['workflows']['api_creds'][0]['password']
base_url = workflow_db['workflows']['api_creds'][0]['base_url']
version = workflow_db['workflows']['api_creds'][0]['api_version']
verify = workflow_db['workflows']['api_creds'][0]['verify']

if args.offline:
    api = None
else:
    api = DNACenterAPI(base_url=base_url, version=version, username=username, password=password, verify=verify)


if __name__ == "__main__":
    main()
