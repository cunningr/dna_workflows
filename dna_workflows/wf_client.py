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
from tabulate import tabulate

sys.path.append(os.getcwd())
module_file_path = './.modules'


def main(_args=None):

    # If we are being called from a test framework
    if _args is not None:
        args = parse_args(_args)
    else:
        args = parse_args(sys.argv[1:])

    if args.host:
        exec_wfaas(args)
    else:
        exec_wflocal(args)


def exec_wflocal(args):

    if args.job_status or args.job_files:
        print('args --job-status and --job-files require the --host param')
        return

    if args.build_xlsx:
        from dna_workflows import schema_tools
        from dna_workflows import package_tools
        modules = package_tools.build_module_list()
        wb = schema_tools.create_new_workbook()
        wb = schema_tools.build_module_schema(wb, modules, user_data={})
        wb = schema_tools.build_workflow_task_sheet(wb, modules)
        wb.save(args.build_xlsx)
        return

    if args.build_test_xlsx:
        from dna_workflows import schema_tools
        from dna_workflows import package_tools
        modules = package_tools.build_module_list()
        wb = schema_tools.create_new_workbook()
        wb = schema_tools.build_module_schema(wb, modules)
        wb = schema_tools.build_workflow_task_sheet(wb, modules)
        wb.save(args.build_test_xlsx)
        return

    if args.update_xlsx_schema:
        from dna_workflows import schema_tools
        from dna_workflows import package_tools
        new_file = args.update_xlsx_schema
        backup_file = 'save.{}'.format(args.update_xlsx_schema)
        try:
            copyfile(args.update_xlsx_schema, backup_file)
        except OSError as e:
            print('ERROR: could not create db backup file {}: {}'.format(backup_file, e))
            return
        modules = package_tools.build_module_list()
        _workflow_db = schema_tools.load_xl_wf_db(args.update_xlsx_schema, flatten=True, fill_empty=True)
        wb = schema_tools.create_new_workbook()
        wb = schema_tools.build_module_schema(wb, modules, user_data=_workflow_db)
        wb = schema_tools.build_workflow_task_sheet(wb, modules, user_data=_workflow_db)
        wb.save(new_file)
        return

    if args.install:
        from dna_workflows import package_tools
        return package_tools.install_manifest()

    if args.install_url:
        from dna_workflows import package_tools
        return package_tools.install_package_from_url(args.install_url)

    if args.install_zip:
        from dna_workflows import package_tools
        return package_tools.install_package_from_zip(args.install_zip)

    if args.add_module_skeleton:
        create_module_skeleton()
        return

    workflow_db = compile_workflow(args)
    if workflow_db is None:
        return None

    if args.validate:
        if args.db or args.yaml_db:
            from dna_workflows import schema_tools
            _result = schema_tools.validate_module_schema(workflow_db, stdout=True)
            return _result
        else:
            print('--validate requires that you specify a valid workflow DB via --db or --yaml-db')
            return None

    results = wf_engine.run_wf(workflow_db)
    print_workflow_results(results)

    return results


def exec_wfaas(args):

    workflow_db = compile_workflow(args)
    if workflow_db is None:
        return None

    if args.job_status:
        _job_id = args.job_status
        url = 'http://{}/job/status/{}'.format(workflow_db['options']['host'], _job_id)
        r = requests.get(url)
        job_status = r.json()
        print('\nWorkflow Report:')
        print(tabulate([
            ['Job ID:', job_status['id']],
            ['Start time:', job_status['details']['start_time']],
            ['End time:', job_status['details']['end_time']],
            ['Status:', job_status['details']['status']]
        ],
            tablefmt="pretty",
            colalign=("left", "left")
        ))
        if 'results' in job_status['details'].keys():
            print_workflow_results(job_status['details']['results'])

        return job_status

    elif args.job_files:
        _job_id = args.job_files
        url = 'http://{}/job/files/{}'.format(workflow_db['options']['host'], _job_id)
        r = requests.get(url)
        if r.status_code == 404:
            _error = r.json()
            print('ERROR: 404 Not found: {}'.format(_error['error']))
        elif r.status_code == 200:
            _save_file = 'results_{}.zip'.format(_job_id)
            file = open(_save_file, "wb")
            file.write(r.content)
            file.close()
            print('Saved job files to: {}'.format(_save_file))

    elif args.build_xlsx:
        _save_file = args.build_xlsx
        url = 'http://{}/schema/xlsx'.format(workflow_db['options']['host'])
        r = requests.get(url)
        if r.status_code == 404:
            _error = r.json()
            print('ERROR: 404 Not found: dna_workflows.xlsx: {}'.format(_error['error']))
        elif r.status_code == 200:
            file = open(_save_file, "wb")
            file.write(r.content)
            file.close()
            print('Saved schema file to: {}'.format(_save_file))

    elif args.build_test_xlsx:
        _save_file = args.build_test_xlsx
        url = 'http://{}/schema/xlsx'.format(workflow_db['options']['host'])
        r = requests.get(url)
        if r.status_code == 404:
            _error = r.json()
            print('ERROR: 404 Not found: dna_workflows.xlsx: {}'.format(_error['error']))
        elif r.status_code == 200:
            file = open(_save_file, "wb")
            file.write(r.content)
            file.close()
            print('Saved schema file to: {}'.format(_save_file))
    else:
        url = 'http://{}/workflow'.format(workflow_db['options']['host'])
        r = requests.post(url, data=json.dumps(workflow_db))
        job_urls = json.loads(r.json())

        print(tabulate([
            ['Job ID:', job_urls['id']],
            ['Status URL:', job_urls['job_status']],
            ['Files URL:', job_urls['job_files']]
        ],
            headers=['Item', 'URL'],
            tablefmt="pretty",
            colalign=("left", "left")
        ))

    return "UNKNOWN"


def parse_args(args):
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--db", help=".xlsx file to use as the db")
    group.add_argument("--yaml-db", help=".yaml file to use as the db")
    parser.add_argument("--profile", help="Use this credentials profile")
    parser.add_argument("--build-xlsx", help="Builds a Excel workflow db based on the module manifest")
    parser.add_argument("--build-test-xlsx", help="Builds a Excel workflow db based on the module manifest with "
                                                  "prepopulated test data")
    # Needs review/fixing
    # parser.add_argument("--manifest", help="Used to specify a manifest file when building an xlsx schema.  Note that "
    #                                        "the modules must already be installed or available from the current "
    #                                        "working directory")
    parser.add_argument("--install", action='store_true', help="Install packages using a manifest from the current "
                                                               "working directory")
    parser.add_argument("--install-url", help="Install packages directly from URL. The URL must provide a "
                                              ".zip archive for the package.")
    parser.add_argument("--install-zip", help="Install packages directly from a .zip archive.")
    parser.add_argument("--update-xlsx-schema", help="Takes an existing Excel workflow DB and tries to update the "
                                                     "schema based on the latest module definition")
    parser.add_argument("--validate", action='store_true', help="Request DB schema schema validation")
    parser.add_argument("--noop", action='store_true', help="Run the scheduling logic but do not execute any workflows")
    parser.add_argument("--offline", action='store_true',
                        help="Creates a 'dummy' api object, useful for workflow development")
    parser.add_argument("--dump-db-to-yaml", help="Creates an yaml file from provided *.xlsx workbook")
    parser.add_argument("--debug", action='store_true', help="Enable debug level messages mode")
    parser.add_argument("--add-module-skeleton", action='store_true', help="Create a DNA Workflows module template")
    parser.add_argument("--host", help="Specify a host running the DNA Workflows Web App")
    parser.add_argument("--job-status", help="Retrieves the job status from DNAWFaaS given the job <id>.  Requires "
                                             "the --host argument.")
    parser.add_argument("--job-files", help="Retrieves the job files from DNAWFaaS given the job <id>.  Requires "
                                            "the --host argument.")

    return parser.parse_args(args)


def compile_workflow(args):

    # Load the workflow DB
    if args.db and args.yaml_db:
        print('WARNING: Only single source of data is allowed. YAML db file will be used.')
    if args.yaml_db:
        try:
            _workflow_db = yaml.load(open(args.yaml_db, 'r'), Loader=yaml.SafeLoader)
        except Exception as e:
            print('Unable to load YAML file {}'.format(args.yaml_db))
            print(e)
            return None
    elif args.db:
        try:
            _workflow_db = schema_tools.load_xl_wf_db(args.db, flatten=True)
        except Exception as e:
            print('Unable to load YAML file {}'.format(args.yaml_db))
            print(e)
            return None
    else:
        _workflow_db = {'workflow': [{'stage': '1', 'module': 'noop', 'task': 'noop', 'api': 'noop'}]}

    # Dump the workflow DB to Yaml
    if args.dump_db_to_yaml:
        with open(args.dump_db_to_yaml, 'w') as file:
            yaml.dump(_workflow_db, file)

    # Try to load credentials
    if args.offline:
        _workflow_db.update({'api_creds': {'offline': True}})
    else:
        if args.profile:
            api_creds = load_credentials(profile=args.profile)
        else:
            api_creds = load_credentials()

        _workflow_db.update({'api_creds': api_creds})

    # Add workflow options
    options = {}
    if args.debug: options.update({'logging': 'DEBUG'})
    if args.noop: options.update({'noop': True})
    if args.host: options.update({'host': args.host})

    _workflow_db.update({'options': options})

    return _workflow_db


def load_credentials(profile=None):
    _home_creds = '{}/.dna_workflows/credentials'.format(str(Path.home()))

    if os.path.isfile('./credentials'):
        _creds = yaml.load(open('./credentials', 'r'), Loader=yaml.SafeLoader)
        # return _creds
    elif os.path.isfile(_home_creds):
        _creds = yaml.load(open(_home_creds, 'r'), Loader=yaml.SafeLoader)
        # return _creds
    else:
        print('FATAL: Unable to find credentials in either ./credentials or ~/.dna_workflows/credentials')
        exit()

    if profile is not None:
        if profile in _creds.keys():
            _pcreds = _creds[profile]
            return _pcreds
        else:
            print('profile "{}" not found. Using default profile'.format(profile))
            return _creds
    else:
        return _creds


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

    _manifest = {'manifest': {_module['module']: {'type': 'module'}}}
    with open('manifest.yaml', 'w') as file:
        yaml.dump(_manifest, file)

    return


def write_to_file(path, file, data):
    _path_to_file = '{}/{}'.format(path, file)
    f = open(_path_to_file, "w")
    f.write(data)
    f.close()


def print_workflow_results(_results):
    _fresults = []
    for _task in _results:
        _fresults.append(
            ['Stage {}'.format(_task['stage']), _task['task'], _task['result']]
        )
    print('\nTask Report:')
    print(tabulate(
        _fresults,
        headers=['Stage', 'Task', 'Result'],
        tablefmt="pretty",
        colalign=("left", "left",)),
    )
    print('')


if __name__ == "__main__":
    main()
