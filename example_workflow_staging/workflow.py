
import logging
import common

logger = logging.getLogger('main.workflow_staging')


def Task_A(api, workflow_dict):
    logger.info('workflow_staging::Task_A')


def Task_B(api, workflow_dict):
    logger.info('workflow_staging::Task_B')


def Task_C(api, workflow_dict):
    logger.info('workflow_staging::Task_C')


def Task_D(api, workflow_dict):
    logger.info('workflow_staging::Task_D')


def Task_E(api, workflow_dict):
    logger.info('workflow_staging::Task_E')
