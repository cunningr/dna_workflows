
import logging
from jinja2 import Template
import ipaddress
import common

logger = logging.getLogger('main.border_handoff')


def get_borders(api, workflow_dict):
    logger.info('reports::get_borders')

    for key, value in workflow_dict.items():
        if 'native' in key:
            _junk, _name, _key = key.split('?')

            if _name == 'border_handoff':

                # Why call one API when you can call three!!
                uri = '/api/v2/data/customer-facing-service/VirtualNetwork'
                vn_db = api.custom_caller.call_api('GET', uri)
                uri = '/api/v2/data/customer-facing-service/virtualnetworkcontext'
                vn_ctx_db = api.custom_caller.call_api('GET', uri)

                for row in value:

                    logger.info('Looking for IP Transit Border Handoff for: {}'.format(row['border_ip']))
                    uri = '/dna/intent/api/v1/business/sda/border-device?deviceIPAddress={}'.format(row['border_ip'])
                    # print(api.fabric_wired.gets_border_device_details_from_sda_fabric(row['border_ip']))
                    response = api.custom_caller.call_api('GET', uri)
                    logger.info('Our AS: AS{}'.format(response['deviceSettings']['internalDomainProtocolNumber']))
                    local_as = response['deviceSettings']['internalDomainProtocolNumber']
                    for extConn in response['deviceSettings']['extConnectivitySettings']:
                        if extConn['externalDomainProtocolNotation'] == 'ASPLAIN':
                            remote_as = extConn['externalDomainProtocolNumber']
                            local_intf = extConn['interfaceUuid']
                            peer_dict = {extConn['interfaceUuid']: []}
                            logger.info('Found IP Transit: AS{}, Interface: {}'.format(
                                remote_as,
                                local_intf
                            ))
                            for transit in extConn['l3Handoff']:

                                vn_name = get_vn_name_by_idref(
                                    vn_db['response'],
                                    vn_ctx_db['response'],
                                    transit['virtualNetwork']['idRef']
                                )
                                logger.info('Building BGP peer for VN: {} on {}'.format(vn_name, local_intf))

                                local_ip_addr = get_ip_address(transit['localIpAddress'])
                                local_ip_subnet = get_ip_subnet(transit['localIpAddress'])
                                remote_ip_addr = get_ip_address(transit['remoteIpAddress'])
                                remote_ip_subnet = get_ip_subnet(transit['remoteIpAddress'])

                                peer_dict[extConn['interfaceUuid']].append({
                                    'remote_as': extConn['externalDomainProtocolNumber'],
                                    'local_as': local_as,
                                    'vlan': transit['vlanId'],
                                    'local_ip': '{} {}'.format(local_ip_addr, local_ip_subnet),
                                    'remote_ip': '{} {}'.format(remote_ip_addr, remote_ip_subnet),
                                    'vn_name': vn_name,
                                    'description': 'To {} - {}'.format(row['hostname'], extConn['interfaceUuid'])
                                })
                    # logger.info('{}'.format(peer_dict))

                    for interface, peers in peer_dict.items():
                        print()
                        print('***** Peering config for device connected to {} - {} ******'.format(row['hostname'], interface))
                        for peer in peers:
                            tm = Template(template_vn_peer)
                            config = tm.render(peer)
                            print(config)
                            print('********************************************************')


def get_vn_name_by_idref(vn_db, vn_ctx_db, id_ref):
    for vn in vn_db:
        if vn['id'] == id_ref:
            vn_context_id = vn['virtualNetworkContextId']

    for vn in vn_ctx_db:
        if vn['id'] == vn_context_id:
            vn_name = vn['name']

    return vn_name


def get_ip_address(addr):
    """Get ipv4 address within given subnet.

    Args:
        addr: ipv4 address in prefix format

    Returns:
        ipv4 address

    """
    addr = ipaddress.ip_interface(addr)

    return str(addr.ip)


def get_ip_subnet(addr):
    """Get subnet mask of ipv4 in prefix format

    Args:
        addr:   ipv4 address in prefix format

    Returns:
        subnet mask

    """
    addr = ipaddress.IPv4Network(addr, strict=False)
    return str(addr.netmask)


template_vn_peer = """
vlan {{ vlan }}
  name {{ vn_name }}_TRANSIT_VLAN
!
interface Vlan{{ vlan }}
  description {{ description }}
  vrf forwarding {{ vn_name }}
  ip address {{ remote_ip }}
  no ip redirects
  no ip proxy-arp
!
router bgp {{ remote_as }}
  address-family ipv4 vrf {{ vn_name }}
    neighbor {{ local_ip }} remote-as {{ local_as }}
    neighbor {{ local_ip }} activate
  exit-address-family
!
"""
