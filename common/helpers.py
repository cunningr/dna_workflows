"""
Common helper functions
"""
import logging
import functools
import time
import threading

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


def get_object_id(object_list, **kwargs):
    """Get object id

    Args:
        object_list: A list of json objects
        **kwargs: a list of filters to search the object list for

    Returns:
        The value of the json key 'id' or 'None' is no object is found

    """
    for item in object_list:
        _match = 0
        for key, value in kwargs.items():
            if item[key] == value:
                logger.debug('{}'.format(item))
                _match = 1
            else:
                _match = 0
                break

        if _match:
            return item['id']

    return None


def wait_for_task_completion(api, task, timeout=10):

    if task['executionStatusUrl']:
        _exec_url = task['executionStatusUrl']
        _intent_api = 1
    elif task['url']:
        _intent_api = 0
        _exec_url = task['url']

    _result = api.custom_caller.call_api('GET', _exec_url)

    t = timeout
    while True:
        if _intent_api:
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
        else:
            if not _result['response']['endTime']:
                logger.debug(_result)
                logger.debug('sleeping for 2 seconds ...')
                time.sleep(2)
                _result = api.custom_caller.call_api('GET', _exec_url)
                logger.debug(_result)
                t = t - 2
            else:
                logger.info('Task status: "{}", Error status: {}'.format(
                    _result['response']['progress'], _result['response']['isError']))
                logger.debug(_result)
                break

            if t < 1:
                logger.info('Timeout waiting for task to complete')
                logger.debug(_result)
                break

    return _result


def monitor_task_status(api, taskId, taskName, interval):
    """
        Thread to monitor task status.
    """
    
    logger.info("In monitoring task ..." + taskName)
    
    taskStatus = api.task.get_task_by_id(task_id=taskId)
    logger.info(taskStatus)
    
    while taskStatus.response.endTime is None:
        time.sleep(interval)
        logger.info("Another run task ...")
        taskStatus = api.task.get_task_by_id(task_id=taskId)
        logger.info(taskStatus)
    
    if taskStatus.response.isError == True:
        logText = taskName + ' Task has finished with error: ' + str(taskStatus.response.failureReason)
    else:
        logText = taskName + ' Task has finished successfully.'
        
    logger.info(logText)
    return


def report_task_completion(api, taskId, taskName, interval=10):
    """
        Get task, create worker that will monitor it and report its completion.
    """
    
    logger.info("Entering task completion monitoring ...")
    
    worker = threading.Thread(target=monitor_task_status(api=api, taskId=taskId, taskName=taskName, interval=interval))
    worker.setDaemon(True)
    worker.start()
    
    return
    