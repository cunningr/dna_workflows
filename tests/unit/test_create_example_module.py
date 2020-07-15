import pytest
from dna_workflows import wf_client
import logging
import io
import os
import shutil
import pkgutil

level = logging.getLevelName('DEBUG')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level)


class TestModuleCreate:
    def test_create_module(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO('example_module\ncunningr@gmail.com'))
        wf_client.create_module_skeleton()
        LOGGER.debug('Assert isdir: {}'.format('example_module'))
        assert os.path.isdir('example_module')
        LOGGER.debug('Assert ismodule: {}'.format('example_module'))
        assert pkgutil.find_loader('example_module')
        assert os.path.isfile('manifest.yml')

    def test_build_xlsx(self, monkeypatch):
        monkeypatch.setattr('sys.argv', ['dna_workflows', '--build-xlsx', 'example.xlsx'])
        wf_client.main()
        LOGGER.debug('Assert isfile: {}'.format('example.xlsx'))
        assert os.path.isfile('example.xlsx')
        LOGGER.debug('Assert isfile: {}'.format('example.xlsx'))
        os.remove('example.xlsx')
        LOGGER.debug('Assert isfile: {} FALSE'.format('example.xlsx'))
        assert os.path.isdir('example.xlsx') is False

    def test_cleanup(self):
        assert os.path.isdir('example_module')
        LOGGER.debug('Cleanup module: {}'.format('example_module'))
        shutil.rmtree('example_module')
        assert os.path.isdir('example_module') is False
        assert os.path.isfile('manifest.yml')
        LOGGER.debug('Assert isfile: {}'.format('manifest.yml'))
        os.remove('manifest.yml')
        LOGGER.debug('Assert isfile: {} FALSE'.format('manifest.yml'))
        assert os.path.isdir('manifest.yml') is False


if __name__ == '__main__':
    pytest.main()
