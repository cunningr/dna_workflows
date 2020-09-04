import pytest
from unittest.mock import patch
from dna_workflows import wf_client
import logging
import io
import os
import shutil
import sys
import pkgutil
import yaml

try:
    sys.path.index('../')
except ValueError:
    sys.path.append('../')

level = logging.getLevelName('DEBUG')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level)

file_manifest = 'manifest.yml'
file_db = 'example'
test_module_name = 'example_module'


class TestModuleCreate:
    def test_create_module(self):
        _input = '{}\ncunningr@gmail.com'.format(test_module_name)
        with patch('sys.stdin', io.StringIO(_input)):
            wf_client.create_module_skeleton()
        LOGGER.debug('Assert isdir: {}'.format(test_module_name))
        assert os.path.isdir(test_module_name)
        LOGGER.debug('Assert ismodule: {}'.format(test_module_name))
        assert pkgutil.find_loader(test_module_name)
        assert os.path.isfile(file_manifest)

    def test_build_xlsx(self):
        _xlsx_db = '{}.xlsx'.format(file_db)
        with patch('sys.argv', ['dna_workflows', '--build-xlsx', _xlsx_db]):
            wf_client.main()
        LOGGER.debug('Assert isfile: {}'.format(_xlsx_db))
        assert os.path.isfile(_xlsx_db)

    def test_build_test_xlsx(self):
        _xlsx_db = 'test_{}.xlsx'.format(file_db)
        with patch('sys.argv', ['dna_workflows', '--build-test-xlsx', _xlsx_db]):
            wf_client.main()
        LOGGER.debug('Assert isfile: {}'.format(_xlsx_db))
        assert os.path.isfile(_xlsx_db)

    def test_update_xlsx(self):
        _xlsx_db = 'test_{}.xlsx'.format(file_db)
        _xlsx_db_save = 'save.test_{}.xlsx'.format(file_db)
        with patch('sys.argv', ['dna_workflows', '--update-xlsx-schema', _xlsx_db]):
            wf_client.main()
        LOGGER.debug('Assert isfile: {}'.format(_xlsx_db))
        LOGGER.debug('Assert isfile: {}'.format(_xlsx_db_save))
        assert os.path.isfile(_xlsx_db)
        assert os.path.isfile(_xlsx_db_save)

    def test_run_workflow_no_creds(self, capsys):
        _xlsx_db = '{}.xlsx'.format(file_db)
        with patch('sys.argv', ['dna_workflows', '--db', _xlsx_db]):
            wf_client.main()
        captured = capsys.readouterr()
        LOGGER.debug('OUTPUT: {}'.format(captured.out))
        LOGGER.debug('ERROR: {}'.format(captured.err))
        assert 'Unable to find credentials' in captured.out

    def test_yaml_dump(self):
        _xlsx_db = '{}.xlsx'.format(file_db)
        _yaml_db = '{}.yaml'.format(file_db)
        with patch('sys.argv', [
            'dna_workflows',
            '--db', _xlsx_db,
            '--dump-db-to-yaml', _yaml_db,
            '--offline'
        ]):
            wf_client.main()
        LOGGER.debug('Assert isfile: {}'.format(_yaml_db))
        assert os.path.isfile(_yaml_db)
        _workflow_db = yaml.load(open(_yaml_db, 'r'), Loader=yaml.SafeLoader)
        # Add more tests here for schema content
        LOGGER.debug('{}'.format(_workflow_db.keys()))

    def test_cleanup(self):
        _xlsx_db = '{}.xlsx'.format(file_db)
        _test_xlsx_db = 'test_{}.xlsx'.format(file_db)
        _xlsx_db_save = 'save.test_{}.xlsx'.format(file_db)
        _yaml_db = '{}.yaml'.format(file_db)

        LOGGER.debug('Cleanup module: {}'.format(test_module_name))
        shutil.rmtree(test_module_name)
        assert os.path.isdir(test_module_name) is False

        LOGGER.debug('Assert isfile: {} FALSE'.format(file_manifest))
        os.remove(file_manifest)
        assert os.path.isdir(file_manifest) is False

        LOGGER.debug('Assert isfile: {} FALSE'.format(_xlsx_db))
        os.remove(_xlsx_db)
        assert os.path.isdir(_xlsx_db) is False

        LOGGER.debug('Assert isfile: {} FALSE'.format(_test_xlsx_db))
        os.remove(_test_xlsx_db)
        assert os.path.isdir(_test_xlsx_db) is False

        LOGGER.debug('Assert isfile: {} FALSE'.format(_xlsx_db_save))
        os.remove(_xlsx_db_save)
        assert os.path.isdir(_xlsx_db_save) is False

        LOGGER.debug('Assert isfile: {} FALSE'.format(_yaml_db))
        os.remove(_yaml_db)
        assert os.path.isdir(_yaml_db) is False


if __name__ == '__main__':
    pytest.main()
