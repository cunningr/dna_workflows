# DNA Workflows

This is the DNA Workflows project for the ```dna_workflows.py``` client and workflow engine code.  It provides a wrapper for publicly available Cisco SDKs and python libraries allowing users to develop 'Task' libraries and execute them using a simple linear workflow engine.

An example module providing a few sample tasks using the [dnacentersdk](https://dnacentersdk.readthedocs.io/en/latest/#) can be found in (TBD).

Currently integrated SDKs

 * [dnacentersdk](https://dnacentersdk.readthedocs.io/en/latest/#)

**The code is published here for demo purposes only and has had very little scrutiny for quality or security posture.**

## DNA Workflows Quick Start

You can install DNA Workflows using ```pip3```

```
pip3 install dna_workflows
```

A workflow is a user defined sequence of tasks and associated data passed to the workflow engine for execution.  For convenience, a workflow and all of its input data can be provided via an Excel workbook which is the recommended way to get started.  Workflows can also converted from Excel to YAML to be maintained and executed directly in this format.

After installing DNA Workflows you should be able to use the script directly by typing ```dna_workflows -h``` in your shell;

```
# dna_workflows -h
usage: dna_workflows [-h] (--db DB | --yaml-db YAML_DB | --build-xlsx BUILD_XLSX) [--dump-db-to-yaml DUMP_DB_TO_YAML] [--debug] [--noop] [--offline] [--persist-module-manifest] [--incognito] [--host HOST]

optional arguments:
  -h, --help            show this help message and exit
  --db DB               .xlsx file to use as the db
  --yaml-db YAML_DB     .yaml file to use as the db
  --build-xlsx BUILD_XLSX
                        Builds a Excel workflow db based on the module manifest
  --dump-db-to-yaml DUMP_DB_TO_YAML
                        Creates an yaml file from provided *.xlsx workbook
  --debug               Enable debug level messages mode
  --noop                Run the scheduling logic but do not execute any workflows
  --offline             Creates a 'dummy' api object, useful for workflow development
  --persist-module-manifest
                        Do not clean up the .modules manifest
  --incognito           Disable sending of usage statistics
  --host HOST           Specify a host running the DNA Workflows Web App
```

The next thing you will need is a ```credentials``` file to tell DNA Workflows how to configure the SDK and connect to your systems;

```
dnacentersdk:
    api_version: "1.3.0"
    base_url: "https://10.0.0.1"
    username: "admin"
    password: "Cisco123"
    verify: False
```

Note that the ```credentials``` file needs to be valid YAML.  Once you have updated the ```credentials``` file you can either put it in the directory where you will load/execute the module code, ```./``` or you can put it in a folder in your home dir ```~/.dna_workflows/credentials```.  We recommend the later and to adjust the permissions on the file appropriately (E.g. ```chmod 600```)

At this point you should be able to test connectivity to your API endpoint;

```
# dna_workflows --noop
2020-06-04 09:26:58,114 - main - INFO - API connectivity established with dnacentersdk
2020-06-04 09:26:58,123 - main - INFO - Executing STAGE-1 workflow: noop::noop
```

---

For this Quick Start guide you will need to ```cd``` into this git repo in order to execute the script.

Next, copy or move the template ```dna_workflow_db.xlsx.org``` file to ```dna_workflow_db.xlsx```, open it up and view the sample data.  Make changes to the contents of the data tables in each worksheet module and update the enable/disable status of the tasks on the 'workflows' worksheet.  For the first run we strongly recommend executing the script in ```--noop``` mode.

```
python3 ./dna_workflows.py --noop
```

Running in ```--noop``` mode will attempt to authenticate with your DNA Center system but it will send or receive any other data.  Instead it will provide you a report on the status of each task in the workflow database.

When you are confident that the workflow database is configured how you want it, you can rerun the ```dna_workflows.py``` script without the ```--noop``` option.

If you wish to save a snapshot of your workflow database you can dump the contents out to a YAML file like so;

```
python3 ./dna_workflows.py --noop --dump-db-to-yaml my_workflow_db.yml
```

and then to replay your workflow using a YAML file as your ingress database you can do;

```
python3 ./dna_workflows.py --yaml-db my_workflow_db.yml
```
 