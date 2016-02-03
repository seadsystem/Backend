import re
from urllib.parse import urlparse, parse_qs


def parse(url):
    """
    Match the URL against a set of routing rules

    :param url: The path from the request
    :return: Array of URL parameters
    """
    url_components = urlparse(url)
    path = url_components.path
    params = parse_qs(url_components.query)
    query_options = {
        'device_id': None,
        'start_time': None,
        'end_time': None,
        'subset': None,
        "limit": None,
        "json": False,
        "reverse": False,
        "device": None,
        "diff": False,
        "total_energy": False,
        "label"
        "list_format": None,
        "granularity": None,
        "events": None
    }

    ''' Extract device_id from URL '''
    device_id_only = re.match('^/(?P<device_id>\d+$)', path)
    if device_id_only:
        query_options['device_id'] = int(device_id_only.group('device_id'))

    '''Extract total_energy from URL'''
    total_energy = re.match('^/(?P<device_id>\d+)/total_energy$', path)
    if total_energy:
        query_options['device_id'] = int(total_energy.group('device_id'))
        query_options['total_energy'] = True

    if 'events' in params.keys():  # Cast float parameters
        print(params['events'])
        query_options['events'] = float(params['events'][0])

    ''' Iterate over possible parameters and set query options accordingly '''
    for param in ['start_time', 'end_time', 'subset', 'limit',
                  'granularity']:  # Cast integer parameters
        if param in params.keys():
            query_options[param] = int(params[param][0])

    # Set string parameters
    for param in ['type', 'device', 'list_format']:
        if param in params.keys():
            query_options[param] = params[param][0]

    # Set boolean parameters
    for param in ['json', 'reverse', 'classify', 'diff']:
        if param in params.keys():
            query_options[param] = True

    # Serial number required
    if not query_options['device_id']:
        raise Exception("Not Found")

    return query_options
