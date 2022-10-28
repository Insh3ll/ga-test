#!/usr/bin/env python3

from ast import Try
import requests

tailscale_derp_server = "https://controlplane.tailscale.com/derpmap/default"


def getDerpMap():
    try:
        resp = requests.get(tailscale_derp_server)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(e)

    return None


def parseDerpMapForAddress(derpMap):
    ipv4List, ipv6List = [], []

    if derpMap is not None:
        regions = derpMap.get('Regions')
        for r, v in regions.items():
            for node in v.get('Nodes'):
                ipv4List.append(node.get('IPv4')) if node.get('IPv4') else None
                ipv6List.append(node.get('IPv6')) if node.get('IPv6') else None

    return ipv4List, ipv6List


def generateRsc(ipv4List, ipv6List):
    if len(ipv4List) > 0 or len(ipv6List) > 0:
        with open('tsDerp.rsc', 'w') as fo:
            if len(ipv4List) > 0:
                fo.write('/log info "Loading tailscale derp ipv4 address list"\n')
                fo.write(
                    '/ip firewall address-list remove [/ip firewall address-list find list=tsDerp]\n')
                fo.write('/ip firewall address-list\n')
                for ipv4 in ipv4List:
                    fo.write(
                        ':do { add address=%s/32 list=tsDerp } on-error={}\n' % ipv4)

            if len(ipv6List) > 0:
                fo.write('/log info "Loading tailscale derp ipv6 address list"\n')
                fo.write(
                    '/ipv6 firewall address-list remove [/ipv6 firewall address-list find list=tsDerp]\n')
                fo.write('/ipv6 firewall address-list\n')
                for ipv6 in ipv6List:
                    fo.write(
                        ':do { add address=%s/128 list=tsDerp } on-error={}\n' % ipv6)


if __name__ == '__main__':
    derp_map = getDerpMap()
    ipv4List, ipv6List = parseDerpMapForAddress(derp_map)
    generateRsc(ipv4List, ipv6List)
