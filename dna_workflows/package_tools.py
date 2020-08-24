import sys
import logging
from pathlib import Path
import copy

logger = logging.getLogger('package_tools')
home = str(Path.home())
install_dir = '{}/.dna_workflows/install'.format(home)


def load_manifest():
    _manifest = {'modules':{'dnawf_dnac.sites': ['create', 'delete'], 'sites': ['create', 'delete']}}
    return _manifest


def load_module(_module):
    try:
        sys.path.index(install_dir)
    except ValueError:
        sys.path.append(install_dir)

    _manifest = load_manifest()
    _import = 'import {}'.format(_module)

    if _module in globals():
        logger.debug('Module {} is already loaded'.format(_module))
    elif _module in _manifest['modules'].keys():
        logger.info('Loading module {}'.format(_module))
        exec(_import, globals())
    else:
        logger.error('Workflow module with name {} is not loaded'.format(_module))
        return -1

    return


def execute_task(api, _module, _task, _workflow_dict):
    _manifest = load_manifest()
    _task_exec = '{}.{}(api, copy.deepcopy({}))'.format(_module, _task, _workflow_dict)

    if _task in _manifest['modules'][_module]:
        exec(_task_exec)
    else:
        logger.error('Task {} from workflow module {} is not loaded'.format(_task, _module))
        return -1

    return
