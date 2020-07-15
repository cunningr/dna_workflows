import pytest
from dna_workflows import schema_tools
import logging
import inspect

level = logging.getLevelName('DEBUG')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level)


class TestSchemaTools:
    def test_create_workbook(self):
        _wb = schema_tools.create_new_workbook()
        LOGGER.debug('Workbook is type {}'.format(type(_wb)))
        assert inspect.isclass(type(_wb))

    def test_load_table_data(self):
        _wb = 'tests/data/test.xlsx'
        _dict = schema_tools.load_xl_wf_db(_wb)
        LOGGER.debug('Return object is type {}'.format(type(_dict)))
        LOGGER.debug('{}'.format(_dict))
        assert type(_dict) is dict


if __name__ == '__main__':
    pytest.main()
