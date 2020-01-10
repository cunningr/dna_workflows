

ip_pool = {
    'ipPoolName': '$string',
    'ipPoolCidr': '$ip_prefix',
    'gateways': None,
    'dhcpServerIps': None,
    'dnsServerIps': None
}

ip_reservation = {
    'groupName': '$string',
    'type': 'generic',
    'siteId': '$string',
    'groupOwner': 'DNAC',
    'ipPools': [{
        'ipPoolCidr': '$ipv4_prefix',
        'parent': '$string',
        'dhcpServerIps': '$string',
        'dnsServerIps': None,
        'gateways': '$string',
        'parentUuid': '$string',
        'ipPoolOwner': 'DNAC',
        'shared': True
    }]
}
