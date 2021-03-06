import re
import time
from util import cmd_util
from itertools import groupby

# match v2ray StatsService.GetStats 一个 stat 输出的正则表达式
_traffic_pattern = re.compile(
  'stat:\s*<\\n\s*name:\s*\"(?P<id_type>inbound|user)>>>(?P<tag>\w+)>>>traffic>>>(?P<traffice_type>uplink|downlink)\"(\\n\s*value:\s*(?P<value>\d+)\\n>)?'
)

# stats default: 'pattern', other values 'name', ''
def get_v2ray_api_cmd(service='StatsService',
                      method='QueryStats',
                      stats='pattern',
                      pattern='',
                      reset='false'):
    if stats == 'name':
        cmd = '/usr/bin/v2ray/v2ctl api --server=127.0.0.1:8080 %s.%s \'name: "%s" reset: %s\''\
          % (service, method, pattern, reset)
    elif stats == 'pattern':
        cmd = '/usr/bin/v2ray/v2ctl api --server=127.0.0.1:8080 %s.%s \'pattern: "" reset: %s\''\
          % (service, method, reset)
    else:
        cmd = '/usr/bin/v2ray/v2ctl api --server=127.0.0.1:8080 %s.%s \'\''\
          % (service, method)
    return cmd

def key_for_sort(each):
    return each['tag']

# 返回一个数组, [{'id_type': 'inbound', 'tag': 'ray', 'traffice_type': 'uplink', 'value': 17963776},{'id_type': 'inbound', 'tag': 'kay', 'traffice_type': 'downlink', 'value': 0}]
def get_traffic(isreset='true'):

    traffics = []
    raw_traffics = []

    moment = str(int(time.time()))
    results, code = cmd_util.exec_cmd(get_v2ray_api_cmd(reset = isreset))
    if code != 0:
        return []
    for match in _traffic_pattern.finditer(results):
        # inbound, user
        id_type = match.group('id_type')
        # email, api, ray
        tag = match.group('tag')
        # uplink, downlink
        traffice_type = match.group('traffice_type')
        # 流量
        value = match.group('value')

        if not value:
            value = 0
        else:
            value = int(value)

        raw_traffics.append({
            'id_type': id_type,
            'tag': tag,
            'traffice_type': traffice_type,
            'value': value
        })

    raw_traffics.sort(key = key_for_sort)
    raw_traffics = groupby(raw_traffics, key = key_for_sort)

    groups = []
    for key, traffic in raw_traffics:
        groups.append(list(traffic))

    for i in groups:
        traffics.append({
            'id_type': i[0]['id_type'],
            'tag': i[0]['tag'],
            i[0]['traffice_type']: i[0]['value'],
            i[1]['traffice_type']: i[1]['value']
        })

    return traffics, moment
