import sys
import traceback
import logging
from pathlib import Path
import os
import shutil
import yaml
import requests
import zipfile
import io
import copy

logger = logging.getLogger('package_tools')
home = str(Path.home())
install_dir = '{}/.dna_workflows/install'.format(home)


# def load_manifest():
#     _manifest = {'modules':{'dnawf_dnac.sites': ['create', 'delete'], 'sites': ['create', 'delete']}}
#     return _manifest


def install_manifest():
    Path(install_dir).mkdir(parents=True, exist_ok=True)

    _package_manifest = Path('manifest.yaml')
    if _package_manifest.is_file():
        try:
            _manifest = yaml.load(open(_package_manifest, 'r'), Loader=yaml.SafeLoader)
        except Exception as e:
            print('Unable to load manifest {}.  Please check this valid YAML'.format(_package_manifest))
            print(e)
            return
    else:
        print('ERROR: manifest file {} not found'.format(_package_manifest))
        return

    if 'manifest' not in _manifest.keys():
        logger.error('Error parsing manifest: BAD FORMAT {}'.format(_manifest))
        return -1

    # Copy the package files to the install_dir
    for _package_name, _package_meta in _manifest['manifest'].items():
        if os.path.isdir(_package_name):
            to_path = '{}/{}'.format(install_dir, _package_name)
            copy_and_overwrite(_package_name, to_path)
        else:
            logger.error('Could not find directory {}'.format(_package_name))
            return -1

    _install_manifest = load_install_manifest()
    _install_manifest['manifest'].update(_manifest['manifest'])

    # Write out install manifest
    _manifest_file = '{}/manifest.yaml'.format(install_dir)
    with open(_manifest_file, 'w') as file:
        yaml.dump(_install_manifest, file)


def load_install_manifest():
    _manifest_file = '{}/manifest.yaml'.format(install_dir)
    if os.path.isfile(_manifest_file):
        try:
            _manifest = yaml.load(open(_manifest_file, 'r'), Loader=yaml.SafeLoader)
        except Exception as e:
            print('Unable to load install manifest {}.  Please check this valid YAML'.format(_manifest_file))
            print(e)
            return
    else:
        _manifest = {'manifest': {}}

    return _manifest


def load_module(_module):
    try:
        sys.path.index(install_dir)
    except ValueError:
        sys.path.append(install_dir)

    _manifest = build_module_list()
    _import = 'import {}'.format(_module)

    if _module in globals():
        logger.debug('Module {} is already loaded'.format(_module))
    elif _module in _manifest:
        logger.debug('Loading module {}'.format(_module))
        exec(_import, globals())
    else:
        logger.error('Workflow module with name {} is not loaded'.format(_module))
        return -1

    return


def execute_task(api, _module, _task, _workflow_dict):
    _manifest = build_method_list(name_only_fully_qualified=True)
    _func = '{}.{}'.format(_module, _task)
    _task_exec = '{}(api, copy.deepcopy({}))'.format(_func, _workflow_dict)
    if _func in _manifest:
        exec(_task_exec)
    else:
        logger.error('Task {} from workflow module {} is not loaded'.format(_task, _module))
        return -1

    return


def build_module_list():
    _install_manifest = load_install_manifest()
    _module_list = []
    for _package_name, _package_meta in _install_manifest['manifest'].items():
        if _package_meta['type'] == 'module':
            _module_list.append(_package_name)
        elif _package_meta['type'] == 'bundle':
            for _bundle_module in _package_meta['provides']:
                _module = '{}.{}'.format(_package_name, _bundle_module)
                _module_list.append(_module)

    return _module_list


def build_method_list(name_only=False, name_only_fully_qualified=False):
    _methods = []
    for _module in build_module_list():
        module_doc = get_module_doc(_module)

        for m in module_doc['module']['methods']:
            if name_only:
                _methods.append(m['task'])
            elif name_only_fully_qualified:
                _task = '{}.{}'.format(_module, m['task'])
                _methods.append(_task)
            else:
                _methods.append(m)

    return _methods


def get_module_doc(_module):
    load_module(_module)
    exec_str = '{}.get_module_definition()'.format(_module)
    _module_doc = eval(exec_str)

    return _module_doc


def install_package_from_zip(file):
    extract_path = './.package'
    Path(extract_path).mkdir(parents=True, exist_ok=True)

    z = zipfile.ZipFile(file)
    z.extractall(extract_path)

    file_list = os.listdir(extract_path)
    archive_root = '{}/{}'.format(extract_path, file_list[0])
    if len(file_list) == 1 and os.path.isdir(archive_root):
        logger.info('Archive extracted OK to path: {}'.format(archive_root))
        pass
    else:
        logger.error('Fatal error extracting package.  Archive should contain a single root dir: {}'.format(file_list))
        return -1

    # Get the current working dir, do the install then remove the download
    cwd = os.getcwd()
    os.chdir(archive_root)
    install_manifest()
    os.chdir(cwd)
    shutil.rmtree(extract_path)


def install_package_from_url(url):
    save_path = './package.zip'
    chunk_size = 128

    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    install_package_from_zip(save_path)


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)
