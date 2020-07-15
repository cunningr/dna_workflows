import pytest
import dna_workflows
import logging
import inspect

level = logging.getLevelName('DEBUG')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level)


class TestModuleCreate:
    def test_create_module(self):
        dna_workflows.create_module_skeleton.input = lambda: 'example_module'
        dna_workflows.create_module_skeleton()
        LOGGER.debug('Workbook is type {}'.format(type(_wb)))


if __name__ == '__main__':
    pytest.main()
