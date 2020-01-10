# DNA Workflows

First things first; ***We accept no responsibility for any kind of loss or damage caused by using this arrangement of software code.  We also do not provide any promises or commitment of support for said code.  It is pretty much all on you.***

DNA Workflows provides a framework for packaging and running DNA Center workflows and is loosely based on the python [dnacentersdk](https://dnacentersdk.readthedocs.io/en/latest/#) package.

Workflows are written in python and added to the workflows DB (Excel workbook) where workflow input data and scheduling can be managed.

## Getting Started

The first thing you will need to do is clone this git repository and install the requirements using pip (Note: DNA Workflows requires Python 3).

```
pip3 install -r requirements.txt
```

The ```requirements.txt``` contains the requirements need to run the workflows included with this repository.  However it is possible that new or custom workflows will require additional packages.

Once you have cloned this repo, open up the ```dna_workflow_db.xlsx``` workflow DB.  The first sheet **workflows** is the master workflow control sheet.  The first table defines the credentials of the DNA Center that you will be working with.  The second table is a list of 'workflows', each one referencing another workflow sheet in the workbook.  Setting the status of the workflows to ```disabled``` in this second table will ... well, disable the execution of that workflow.

![DNA Workflows - Workflow worksheet](images/workflow_screenshot.png)  

There is also a worksheet called ```control``` that is used to define lists for data validation.

The remaining worksheets define the individual workflows and the workflow sub-tasks.  The example below shows the ```sites``` workflow.

![DNA Workflows - sites workflow worksheet](./images/sites_screnshot.png)

A key thing to note is that all data in the DNA Workflows DB is defined in Excel tables, and each table has a name that uniquely identifies that data set within the workbook.  If you highlight any cell in a table, the 'Table' menu appears at the top of the Excel window.  Selecting this menu, you will be able to see the table name.

![DNA Workflows - Excel Tables Demo](./images/tables_screnshot.png)

When creating new workflows, it is probably good practice to use a fixed naming scheme for your tables especially if you want to be able to identify specific data schema in your workflows, but this is not a hard and fast rule so feel free to experiment.

We try to stick to the following naming schema;

```<type>?<description>?<keyColumn>```

Ok, so lets jump to getting DNA Workflows running:

 1. The first thing you will need to do is update the credentials in the ```workflows``` worksheet and save the workbook.
 2. Assuming that you have already installed the python requirements, you can run the workflows in No Operation mode (noop) like so;

```python3 dna_workflows.py --noop```

This will test connectivity to your DNA Center but will not execute any of the workflows.  Instead it will just log to console, letting you know which workflows are enabled on the master ```workflow``` worksheet.

```
CUNNINGR-M-X436:dna_workflows cunningr$ python3 dna_workflows.py --noop
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-1 workflow: sites::create
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-1 workflow: ip_pool::create_pools
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-1 workflow: discovery::create_global_credentials
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-1 workflow: discovery::delete_global_credentials
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-1 workflow: border_handoff::get_borders
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-2 workflow: ip_pool::create_reservations
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-2 workflow: reports::hello_world
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-2 workflow: discovery::run_discovery
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-2 workflow: discovery::delete_discovery
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-3 workflow: ip_pool::delete_reservations
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-4 workflow: ip_pool::delete_pools
2019-11-30 15:48:10,460 - main - INFO - Executing STAGE-10 workflow: sites::delete
2019-11-30 15:48:10,461 - main - INFO - Executing STAGE-10 workflow: reports::create_reports
```

Take this opportunity to disable any of the workflows that may do things that you do want to do right now.  Again, we take no responsibility for any bad things may happen.

Something you may notice from the logging output is the ```Executing STAGE-X``` log message.  Since many workflows that we want to automate when deploying DNA Center have a strict order of dependancy, the DNA Workflows framework allows you to 'schedule' workflow sub-tasks in a specified order.  Now you know what the 'Stage' column does in a workflow control table (see example screenshot above).

The 'Stage' is really just an arbitrary integer so you can choose what you like and the workflow scheduling engine will simply execute the tasks in the DB in staged order (lowest first).  The default workflows are pre-configured to execute in the correct order.

## What does DNA Workflows provide?

In summary;

 * A workflow execution and scheduling engine.
 * A common logging framework.
 * Some common helper code that can be reused in your workflows.
 * A workflow database (Excel) used to control and provide external, structured data to your workflows.
 * Several example DNA Center workflows useful for common deployment and operations tasks.
 * Simple handing of API calls via the integrated [dnacentersdk](https://dnacentersdk.readthedocs.io/en/latest/#).
 * Script to automate adding of new workflows to your workflow DB.

Plans for the future (contributions appreciated);

 * Enhance the ```add_workflow.py``` to include import and export of workflows.

## Documentation

### Running Workflows

You can run ```dna_workflows.py``` with the following options;

 * Run with NoOp mode (testing): ```--noop```
 * Enable debugging level logs: ```--debug``` 
 * Run with a different workflow DB: ```--db <file>``` (default is dna_workflow_db.xlsx)

### Developing Workflows

You can add a new workflow to the (default) DB using the script ```workflow_manager.py```

 * Create a new workflow template: ```--add-workflow <workflow-name>```
 * Delete a workflow from the DB: ```--delete-workflow <workflow-name>```
 * Delete a workflow from the DB and remove the python module: ```--delete-workflow-and-clean <workflow-name>```
 * Export a workflow to a .tar.gz file: ```--export-workflow```
 * Export a workflow to a new workflow DB ready to run locally: ```--export-workflow```
 * Import a workflow from a .tar.gz file: ```--import-workflow``` (not yet implemented)

When you add a new workflow using the script, you will see;

 1. A new row in the master ```workflows``` worksheet.
 2. A new worksheet for the added workflow with a new 'control' table.
 3. A new folder with basic 'Hello-World' workflow code.

Immediately after adding a new workflow, you should be able to execute ```python3 dna_workflows.py --noop``` and see your new workflow being staged for execution.

### Passing data to your Workflow

Data is automatically extracted from the workflow DB and passed into your workflow for you along with the authenticated dnacentersdk api class instance.

Each workflow in the DB has its own worksheet which must, at a minimum, contain the control table.

**Note: Tables in Excel are a named range of cells**

So see the name of a table in Excel, click anywhere in the table and then navigate to the *Table* menu option (this option only appears when you highlight a cell within a defined table).

![DNA Workflows - Excel Tables Demo](./images/tables_screnshot.png)

To create a new table, simply define you data in a new area of the worksheet, highlight all the cells and then do *Insert -> Table*.  You will need to provide headers for each of your columns as the column names will provide the dictionary *key* for each row when the table is imported into DNA Workflows.

Each of your tables will be identified using a dictionary key equal to the Excel table name.

Sample Code: Finding each table in the workflow_db

```
import logging
import common

logger = logging.getLogger('main.passing_data')


def hello_world(api, workflow_dict):
    logger.info('passing_data::hello_world')
    for key, value in workflow_dict.items():
        logger.info('Found table: {} with rows: '.format(key))
        for row in value:
            logger.info('{}'.format(row))
```

![DNA Workflows - Excel Tables Demo](./images/table_demo.png)

Sample output:

```
2019-12-19 08:53:55,583 - main - INFO - Executing STAGE-1 workflow: passing_data::hello_world
2019-12-19 08:53:55,587 - main.passing_data - INFO - passing_data::hello_world
2019-12-19 08:53:55,587 - main.passing_data - INFO - Found table: control?passing_data?Function with rows:
2019-12-19 08:53:55,587 - main.passing_data - INFO - {'Stage': 1, 'Status': 'enabled', 'Function': 'hello_world', 'Documentation': 'Prints Hello World!!', 'workflow': 'passing_data'}
2019-12-19 08:53:55,587 - main.passing_data - INFO - Found table: native?test_data?key1 with rows:
2019-12-19 08:53:55,588 - main.passing_data - INFO - {'key1': 'row1', 'key2': 'row1', 'key3': 'row1', 'key4': 'row1'}
2019-12-19 08:53:55,588 - main.passing_data - INFO - {'key1': 'row2', 'key2': 'row2', 'key3': 'row2', 'key4': 'row2'}
2019-12-19 08:53:55,588 - main.passing_data - INFO - {'key1': 'row3', 'key2': 'row3', 'key3': 'row3', 'key4': 'row3'}
2019-12-19 08:53:55,588 - main.passing_data - INFO - {'key1': 'row4', 'key2': 'row4', 'key3': 'row4', 'key4': 'row4'}
```

### How it works

The workflow engine ```dna_workflows.py``` and the workflow manager ```workflow_manager.py``` are intended to be generic code and should not need to be modified by workflow developers.

When you run  ```dna_workflows.py```, it does the following;

 1. Looks in the ```workflow``` worksheet/table, scans the rows and tries to import a local python module by the name specified in the ```Name``` column.
 2. At the same time as importing the workflow python module, ```dna_workflows.py``` will look in the workbook for a worksheet with the same ```Name``` and load any tables into a python dictionary specific for that particular workflow.
 3. Every workflow worksheet defined in the workflow DB must have a ```control``` table that lists out the 'tasks' (python functions) available in that workflow, along with the ```Status``` and ```Stage``` it needs to be run in (if ```Status``` == enabled).
 4. Next, ```dna_workflows.py``` will build a list of all the workflow 'tasks' according to their ```Status``` that should be executed and sort them in order using the ```Stage``` value assigned to each task.
 5. Finally, ```dna_workflows.py``` will execute each workflow task passing it exactly two arguments ```api``` and ```workflow_dict``` which contain the authenticated dnacentersdk api object and a list of dictionaries each containing the rows of data from the workflow worksheet respectively.

The workflow developer can leverage the dnacentersdk, the data they have defined in any tables within their workflow worksheet, and common logging and helper functions in order to build a new workflow.  Task execution is controlled via the workflow DB.

**All workflow code must be written inside a python function, except for the initial workflow logging setup and any global workflow variable definitions.**

To create a new workflow simply run;

```workflow_manager.py --add-workflow <workflow-name>```

This will do all the basic setup for you.  Just start writing your new workflow code in ```<workflow-name>/workflow.py``` file.

