import asyncio
import os

import requests
import boto3

CONSUL_API_URL = os.getenv('CONSUL_API_URL', 'http://localhost:8500')
CONSUL_ROUTE53_ZONE_ID = os.getenv('CONSUL_ROUTE53_ZONE_ID', 'Z1D8B4ETKDC02C')

@asyncio.coroutine
def watch_healthy_services():
    while True:
        services = requests.get(
            '%s%s' % (CONSUL_API_URL,'/v1/catalog/services')
        ).json().keys()
        for service in services:
            ips = [node['Address'] for node in requests.get(
                '%s%s' % (CONSUL_API_URL,'/v1/catalog/service/%s' % service)
            ).json()]
            print('Found service:%s with ips:%s' % (service, ips))
            update_route53_zone(service, ips)


def update_route53_zone(service, ips):
    client = boto3.client("route53")
    zone = list(filter(
        lambda x: x['Id']=='/hostedzone/%s' % CONSUL_ROUTE53_ZONE_ID,
        client.list_hosted_zones()['HostedZones']
    ))[0]
    service_record_name = '%s.%s' % (service, zone['Name'])
    service_record_set = list(filter(
        lambda x: x['Name'] == service_record_name,
        client.list_resource_record_sets(HostedZoneId=CONSUL_ROUTE53_ZONE_ID)['ResourceRecordSets']
    ))
    if service_record_set:
        print(service_record_set[0])
        ips_changed = not (set(ips) == set(
            [record['Value'] for record in service_record_set[0]['ResourceRecords']]
        ))
    if not service_record_set or ips_changed:
        response_create = client.change_resource_record_sets(
            HostedZoneId=CONSUL_ROUTE53_ZONE_ID,
            ChangeBatch={
                'Comment': 'Updating Resource Record set',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                    'Name': service_record_name[:-1],
                    'Type': 'A',
                    'TTL': 0,
                    'ResourceRecords': [{'Value': ip} for ip in ips]
                }
                }]
            }

        )
    return

loop = asyncio.get_event_loop()
asyncio.async(watch_healthy_services())
loop.run_forever()

