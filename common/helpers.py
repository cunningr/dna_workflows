"""
Common helper functions
"""
import logging
import functools
import time

logger = logging.getLogger('main.helpers')


def dot_to_json(a):
    output = {}
    for key, value in a.items():
        path = key.split('.')
        if path[0] == 'json':
            path = path[1:]
        target = functools.reduce(lambda d, k: d.setdefault(k, {}), path[:-1], output)
        target[path[-1]] = value
    return output


def get_object_id(object_list, key_name, key_value):
    for item in object_list:
        if item[key_name] == key_value:
            logger.debug('{}'.format(item))
            return item['id']

    return None


def wait_for_task_completion(api, task, timeout=10):

    if task['executionStatusUrl']:
        _exec_url = task['executionStatusUrl']

    _result = api.custom_caller.call_api('GET', _exec_url)

    t = timeout
    while True:
        if _result['status'] == 'IN_PROGRESS':
            logger.debug(_result)
            logger.debug('sleeping for 2 seconds ...')
            time.sleep(2)
            _result = api.custom_caller.call_api('GET', _exec_url)
            logger.debug(_result)
            t = t - 2
        else:
            logger.info('Task "{}" with execution id: {} status: {}'.format(
                _result['bapiName'], _result['bapiExecutionId'], _result['status']))
            logger.debug(_result)
            break

        if t < 1:
            logger.info('Timeout waiting for task to complete')
            logger.debug(_result)
            break

    return _result
