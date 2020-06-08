#!/usr/bin/env python3

import sys
import yaml
from jinja2 import Template
import json
import argparse
import os
from shutil import copyfile
import requests
from pathlib import Path
from dna_workflows import wf_engine
from dna_workflows import schema_tools

sys.path.append(os.getcwd())
module_file_path = './.modules'


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--db", help=".xlsx file to use as the db")
    group.add_argument("--yaml-db", help=".yaml file to use as the db")
    parser.add_argument("--build-xlsx", help="Builds a Excel workflow db based on the module manifest")
    parser.add_argument("--update-xlsx-schema", help="Takes an existing Excel workflow DB and tries to update the "
                                                     "schema based on the latest module definition")
    parser.add_argument("--noop", action='store_true', help="Run the scheduling logic but do not execute any workflows")
    parser.add_argument("--offline", action='store_true',
                        help="Creates a 'dummy' api object, useful for workflow development")
    parser.add_argument("--dump-db-to-yaml", help="Creates an yaml file from provided *.xlsx workbook")
    parser.add_argument("--debug", action='store_true', help="Enable debug level messages mode")
    parser.add_argument("--persist-module-manifest", action='store_true', help="Do not clean up the .modules manifest")
    parser.add_argument("--incognito", action='store_true', help="Disable sending of usage statistics")
    parser.add_argument("--add-module-skeleton", action='store_true', help="Create a DNA Workflows module template")
    parser.add_argument("--host", help="Specify a host running the DNA Workflows Web App")
    args = parser.parse_args()

    if args.build_xlsx:
        from dna_workflows import schema_tools
        manifest = 'manifest.yml'
        schema = yaml.load(open(manifest, 'r'), Loader=yaml.SafeLoader)
        wb = schema_tools.create_new_workbook()
        wb = schema_tools.build_module_schema(wb, schema)
        wb = schema_tools.build_workflow_task_sheet(wb, schema)
        wb.save(args.build_xlsx)
        exit()

    if args.update_xlsx_schema:
        from dna_workflows import schema_tools
        manifest = 'manifest.yml'
        new_file = args.update_xlsx_schema
        backup_file = 'save.{}'.format(args.update_xlsx_schema)
        try:
            copyfile(args.update_xlsx_schema, backup_file)
        except OSError as e:
            print('ERROR: could not create db backup file {}: {}'.format(backup_file, e))
            exit()
        schema = yaml.load(open(manifest, 'r'), Loader=yaml.SafeLoader)
        _workflow_db = schema_tools.load_xl_wf_db(args.update_xlsx_schema, flatten=True, fill_empty=True)
        wb = schema_tools.create_new_workbook()
        wb = schema_tools.build_module_schema(wb, schema, user_data=_workflow_db)
        wb = schema_tools.build_workflow_task_sheet(wb, schema, user_data=_workflow_db)
        wb.save(new_file)
        exit()

    if args.add_module_skeleton:
        create_module_skeleton()
        exit()

    workflow_db = compile_workflow(args)
    workflow_db['workflow'] = [_row for _row in workflow_db['workflow'] if _row.get('status', 'enabled') == 'enabled']
    for _row in workflow_db['workflow']:
        _row.pop('status', None)
        _row.pop('minimum_versions', None)
        _row.pop('author', None)
        _row.pop('documentation', None)

    if args.dump_db_to_yaml:
        with open(args.dump_db_to_yaml, 'w') as file:
            yaml.dump(workflow_db, file)

    write_modules_manifest(workflow_db)

    if 'host' in workflow_db['options'].keys():
        url = 'http://{}/workflow'.format(workflow_db['options']['host'])
        r = requests.post(url, data=json.dumps(workflow_db))
    else:
        wf_engine.run_wf(workflow_db)

    if not args.persist_module_manifest:
        if os.path.isfile(module_file_path):
            os.remove(module_file_path)


def compile_workflow(args):

    # Set db file
    options = {}
    if args.db and args.yaml_db:
        print('WARNING: Only single source of data is allowed. YAML db file will be used.')

    if args.yaml_db:
        _workflow_db = yaml.load(open(args.yaml_db, 'r'), Loader=yaml.SafeLoader)
    elif args.db:
        _workflow_db = schema_tools.load_xl_wf_db(args.db, flatten=True)
    else:
        _workflow_db = {'workflow': [{'stage': '1', 'module': 'noop', 'task': 'noop', 'api': 'noop'}]}

    # Build options for workflow_db
    if args.offline:
        _workflow_db.update({'api_creds': {'offline': True}})
    else:
        api_creds = load_credentials()
        _workflow_db.update({'api_creds': api_creds})

    if args.debug: options.update({'logging': 'DEBUG'})
    if args.noop: options.update({'noop': True})
    if args.incognito: options.update({'incognito': True})
    if args.host: options.update({'host': args.host})
    _workflow_db.update({'options': options})

    # if args.dump_db_to_yaml:
    #     with open(args.dump_db_to_yaml, 'w') as file:
    #         yaml.dump(_workflow_db, file)

    return _workflow_db


def write_modules_manifest(_workflow_db):
    wf_modules = {'modules': {}}
    for task in _workflow_db['workflow']:
        if task['module'] not in wf_modules['modules'].keys():
            wf_modules['modules'].update({task['module']: []})
        wf_modules['modules'][task['module']].append(task['task'])

    with open(module_file_path, 'w') as modules:
        modules.write(json.dumps(wf_modules, indent=4))


def load_credentials():
    _home_creds = '{}/.dna_workflows/credentials'.format(str(Path.home()))

    if os.path.isfile('./credentials'):
        _creds = yaml.load(open('./credentials', 'r'), Loader=yaml.SafeLoader)
        return _creds
    elif os.path.isfile(_home_creds):
        _creds = yaml.load(open(_home_creds, 'r'), Loader=yaml.SafeLoader)
        return _creds
    else:
        print('Unable to find credentials in either ./credentials or ~/.dna_workflows/credentials')
        exit()


def create_module_skeleton():
    from dna_workflows import payload_templates
    _module = {}
    _module.update({'module': input('Module name: ')})
    _module.update({'email': input('email: ')})

    # Create module directory
    try:
        os.mkdir(_module['module'])
    except OSError as e:
        print('Creation of the directory {} failed: {}'.format(_module['module'], e))
    else:
        print('Successfully created the directory {}'.format(_module['module']))

    # Write module template files
    tm = Template(payload_templates.workflow_j2)
    output = tm.render(item=_module)
    write_to_file(_module['module'], 'workflow.py', output)

    tm = Template(payload_templates.module_j2)
    output = tm.render(item=_module)
    write_to_file(_module['module'], 'module', output)

    tm = Template(payload_templates.payload_templates_j2)
    output = tm.render()
    write_to_file(_module['module'], 'payload_templates.py', output)

    tm = Template(payload_templates.init_j2)
    output = tm.render()
    write_to_file(_module['module'], '__init__.py', output)

    return


def write_to_file(path, file, data):
    _path_to_file = '{}/{}'.format(path, file)
    f = open(_path_to_file, "w")
    f.write(data)
    f.close()


if __name__ == "__main__":
    main()
