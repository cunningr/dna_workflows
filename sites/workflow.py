import logging
import common
import requests
import json
from sites import payload_templates as templates

logger = logging.getLogger('main.sites')


def create(api, workflow_dict):
    logger.info('sites::create')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _workflow_name, _table_name = key.split('?')

            _sites_db = api.sites.get_site()

            if _table_name == 'areas':
                _create_areas(api, _sites_db['response'], _table_name, value)
            elif _table_name == 'buildings':
                _create_buildings(api, _sites_db['response'], _table_name, value)
            elif _table_name == 'floors':
                _create_floors(api, _sites_db['response'], _table_name, value)


def _create_areas(api, sites_db, table_name, value):

    _table_key = 'name'

    # Cycle through the rows and create entries with 'present' set
    for row in value:
        if 'present' in row['presence']:
            row.pop('presence', None)
            site_name_hierarchy = '{}/{}'.format(row['parentName'], row['name'])
            _id = common.get_object_id(sites_db, siteNameHierarchy=site_name_hierarchy)
            if _id is not None:
                logger.info('Site: {}/{} already exists with id: {}'.format(row['parentName'], row[_table_key], _id))
            else:
                logger.info('Creating site: {}/{}'.format(row['parentName'], row[_table_key]))

                data = templates.area

                data['site']['area']['name'] = row['name']
                data['site']['area']['parentName'] = row['parentName']

                logger.debug('Site payload: {}'.format(data))
                result = api.sites.create_site(payload=data)
                common.wait_for_task_completion(api, result)


def _create_buildings(api, sites_db, table_name, value):
    _table_key = 'name'

    # Cycle through the rows and create entries with 'present' set
    for row in value:
        if 'present' in row['presence']:
            row.pop('presence', None)
            site_name_hierarchy = '{}/{}'.format(row['parentName'], row['name'])
            _id = common.get_object_id(sites_db, siteNameHierarchy=site_name_hierarchy)
            if _id is not None:
                logger.info('Building: {}/{} already exists with id: {}'.format(row['parentName'], row[_table_key], _id))
            else:
                logger.info('Creating building: {}/{}'.format(row['parentName'], row[_table_key]))

                data = templates.building

                data['site']['building']['name'] = row['name']
                data['site']['building']['parentName'] = row['parentName']
                data['site']['building']['address'] = '{}, {}, {}'.format(
                    row['street'],
                    row['city'],
                    row['country']
                )

                location = _address_lookup(row['street'], row['city'], row['country'])
                if location is not None:
                    logger.info('Address lookup: SUCCESS')
                    data['site']['building']['address'] = location['address']
                    data['site']['building']['longitude'] = float(location['lon'])
                    data['site']['building']['latitude'] = float(location['lat'])
                else:
                    logger.info('Address lookup: FAILURE')

                logger.debug('Building payload: {}'.format(data))
                result = api.sites.create_site(payload=data)
                common.wait_for_task_completion(api, result)


def _create_floors(api, sites_db, table_name, value):
    _table_key = 'name'

    # Cycle through the rows and create entries with 'present' set
    for row in value:
        if 'present' in row['presence']:
            row.pop('presence', None)
            site_name_hierarchy = '{}/{}'.format(row['parentName'], row['name'])
            _id = common.get_object_id(sites_db, siteNameHierarchy=site_name_hierarchy)
            if _id is not None:
                logger.info('Floor: {}/{} already exists with id: {}'.format(row['parentName'], row[_table_key], _id))
            else:
                logger.info('Creating floor: {}/{}'.format(row['parentName'], row[_table_key]))

                data = templates.floor

                data['site']['floor']['name'] = row['name']
                data['site']['floor']['parentName'] = row['parentName']
                data['site']['floor']['rfModel'] = row['rfModel']

                logger.debug('Building payload: {}'.format(data))
                result = api.sites.create_site(payload=data)
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
                    site_name_hierarchy = '{}/{}'.format(row['parentName'], row['name'])
                    _id = common.get_object_id(_sites_db['response'], siteNameHierarchy=site_name_hierarchy)
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
            _child_name = site['siteNameHierarchy']
            # _child_name = site['name']

            site_tuple = (_child_name, _child_id, _child_depth)
            _site_tuple_list.append(site_tuple)

    return sorted(_site_tuple_list, key=lambda tup: tup[2], reverse=True)


def _address_lookup(street, city, country):
    maps_url = 'https://nominatim.openstreetmap.org/search?format=json&'
    search_string = 'street={}&city={}&country={}'.format(street, city, country)

    search_url = '{}&{}'.format(maps_url, search_string)
    try:
        response = requests.get(search_url)
    except requests.exceptions.Timeout:
        logger.error('GET towards OSM timeout')
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    search_result = json.loads(response.text)
    if len(search_result) == 1:
        location = {
            'address': search_result[0]['display_name'],
            'lat': search_result[0]['lat'],
            'lon': search_result[0]['lon']
        }
        return location
    else:
        return None

