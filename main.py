import asyncio
import logging
import os

import requests
import boto3

CONSUL_API_URL = os.getenv('CONSUL_API_URL', 'http://localhost:8500')
CONSUL_ROUTE53_ZONE_ID = os.getenv('CONSUL_ROUTE53_ZONE_ID', 'ZXXXXXXXXXX')

@asyncio.coroutine
def watch_healthy_services():
    while True:
        try:
            services = requests.get(
                '%s%s' % (CONSUL_API_URL,'/v1/catalog/services')
            ).json().keys()
            for service in services:
                ips = [node['Node']['Address'] for node in requests.get(
                    '%s%s' % (CONSUL_API_URL,'/v1/health/service/%s?passing' % service)
                ).json()]
                ips = list(set(ips))
                update_route53_zone(service, ips)
                clean_old_entries(services)
            yield from asyncio.sleep(2)
        except Exception as e:
            pass
            #print("Something went wrong %s" % e)

def clean_old_entries(services):
    client = boto3.client("route53")
    zone = list(filter(
        lambda x: x['Id']=='/hostedzone/%s' % CONSUL_ROUTE53_ZONE_ID,
        client.list_hosted_zones()['HostedZones']
    ))[0]
    for record in client.list_resource_record_sets(
        HostedZoneId=CONSUL_ROUTE53_ZONE_ID
    )['ResourceRecordSets']:
        if record['Type'] == 'A' and not any(record['Name'].startswith(service) for service in services):
            #print('Deleting stale record for service %s' % record['Name'].split('.')[0])
            response_delete = client.change_resource_record_sets(
                HostedZoneId=CONSUL_ROUTE53_ZONE_ID,
                ChangeBatch={
                    'Comment': 'Updating Resource Record set',
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': record
                    }]
                }
            )

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
        ips_changed = not (set(ips) == set(
            [record.get('Value') for record in service_record_set[0]['ResourceRecords']]
        ))

    if not service_record_set or ips_changed:
        #print('Updating service %s with new ips %s' % (service, ips))
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
try:
    loop.run_until_complete(watch_healthy_services())
finally:
    loop.close()
