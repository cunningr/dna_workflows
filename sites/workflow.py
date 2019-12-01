import logging
import common

logger = logging.getLogger('main.sites')


def create(api, workflow_dict):
    logger.info('sites::create')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            _sites_db = api.sites.get_site()

            # Cycle through the rows and create entries with 'present' set
            for row in value:
                if 'present' in row['presence']:
                    row.pop('presence', None)
                    _id = common.get_object_id(_sites_db['response'], 'name', row[_key])
                    if _id is not None:
                        logger.info('Site: {} already exists with id: {}'.format(row[_key], _id))
                    else:
                        logger.info('Creating site: {}'.format(row[_key]))
                        logger.debug('Site payload: {}'.format(common.dot_to_json(row)))
                        result = api.sites.create_site(payload=common.dot_to_json(row))
                        common.wait_for_task_completion(api, result)


def delete(api, delete_workflow_dict):
    logger.info('sites::delete')
    for key, value in delete_workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            # _sites_db = api.sites.get_site()

            for row in value:
                _sites_db = api.sites.get_site()
                _deleted_sites = []
                if 'absent' in row['presence']:
                    _id = common.get_object_id(_sites_db['response'], 'name', row[_key])
                    if _id is not None:
                        # When deleting a site we need to figure out the children and delete in reverse
                        _child_list_sorted = _get_sorted_child_list(_sites_db['response'], _id)
                        for _child in _child_list_sorted:
                            logger.info('Deleting site: {}'.format(_child[0]))
                            logger.debug('Deleting: {} with id: {}'.format(_child[0], _child[1]))
                            if _child[1] not in _deleted_sites:
                                result = api.sites.delete_site(site_id=_child[1])
                                common.wait_for_task_completion(api, result)
                                _deleted_sites.append(_child[1])

        else:
            continue


# Internal functions


def _get_sorted_child_list(site_db, _id):
    # Find our site and get the siteHierarchy
    _site_tuple_list = []
    for site in site_db:
        if _id == site['id']:
            _site_hierarchy = site['siteHierarchy']

    for site in site_db:
        if _site_hierarchy in site['siteHierarchy']:
            _child_id = site['id']
            _child_depth = len(site['siteHierarchy'].split('/'))
            _child_name = site['name']

            site_tuple = (_child_name, _child_id, _child_depth)
            _site_tuple_list.append(site_tuple)

    return sorted(_site_tuple_list, key=lambda tup: tup[2], reverse=True)
