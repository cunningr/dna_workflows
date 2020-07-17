module_j2 = '''
---
module:
  name: &module "{{ item.module }}"     # Module name
  author: &author "{{ item.email }}"    # Authors email
  # A description of the module will be inserted at the top of the Excel worksheet
  description: "This is default module description for {{ item.module }}"
  # A list of provided public functions (Tasks).  These are inserted into the 'workflow' table
  methods:
    - {"status": "enabled", "task": "hello_world", "stage": 1, "module": *module, "api": "dnacentersdk",
       "author": *author,
       "description": "Runs the hello world task!"
    }
  # A dictionary of table schemas describing the table column names.
  # These will appear on the '<module-name>' worksheet and will create basic data validations
  # Table names take the form <schema-name>.schema.<module-name>
  # see https://github.com/cunningr/sdtables
  schemas:
    hello_world:
      description: "Used by: hello_world"
      properties:
        presence:
          type: string
          enum: ['present', 'absent']
          default: 'present'
        key1:
          type: string
          enum: ['value1', 'value2', 'value3']
          default: 'value1'
        key2:
          type: boolean
          default: False
        example_tref:
          type: string
          tref: 'INDIRECT("another_table.schema.{{ item.module }}[testCol1]")'
        example_default:
          type: string
          default: '=hello_world.schema.{{ item.module }}[[#This Row],[key1]]&"/"&hello_world.schema.{{ item.module }}[[#This Row],[key2]]'
    another_table:
      description: "A test reference table"
      properties:
        testCol1:
          type: string
        testCol2:
          type: string
  # Example data to populate the above schema.
  # In addition the data is also validated against the schema
  data:
    hello_world:
      - {'presence': 'present', 'key1': 'value2', 'key2': True, 'example_tref': 'TWO'}
    another_table:
      - {'testCol1': 'ONE', 'testCol2': 'AAAA'}
      - {'testCol1': 'TWO', 'testCol2': 'BBBB'}
      - {'testCol1': 'THREE', 'testCol2': 'CCCC'}
'''

workflow_j2 = '''
import logging
from {{ item.module }} import payload_templates as templates
import yaml
import pkgutil

logger = logging.getLogger('main.{{ item.module }}')


def get_module_definition():
    data = pkgutil.get_data(__package__, 'module')
    return yaml.load(data, Loader=yaml.SafeLoader)


def hello_world(api, workflow_dict):
    """ Prints hello_world and some test data from example schema.

    :param api: An instance of the XYZ SDK class
    :param workflow_dict: A dictionary containing rows of example data (see module);

    :returns: Nothing """
    
    _schema = 'hello_world.schema.{{ item.module }}'
    logger.info('{{ item.module }}::hello_world')
    logger.debug('schema: {}'.format(_schema))

    print(_schema)
    if _schema in workflow_dict.keys():
        table_data = workflow_dict[_schema]

        for row in table_data:
            print(row)

'''

init_j2 = '''
"""
This is a python init file generated from template.  Replace this text with your workflow description
"""

__version__ = "0.0.1"

from .workflow import *
'''

payload_templates_j2 = '''
a_jinja_template_j2 = """
"aValue": {{ aParameter }}
"""
'''