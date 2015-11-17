#!/usr/bin/env python
"""
starts a really cheap and small instance for testing
"""

from datetime import datetime, timedelta

#configuration options:
ami_id = "ami-81f7e8b1" # PV amazon linux (TODO: select required virtualization kind based on cheapest instance)
group_name = "cheapdebug" #will only run one of these
keypair_name = "spark-tests" #TODO check for existence of key pair
group_description = "ssh acccess for cheapdebug systems"
instance_types = ["t1.micro", 'm4.large']
price_delta = 0.0001 #delta to increase the price by
# interactive = True
interactive = False
sec_group_rules = [{ 'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'tcp', 'IpRanges': [ {'CidrIp': "0.0.0.0/0"}] }]
instance_settings = {
    'InstanceCount': 1,
    # 'ClientToken': group_name, #does this need to be more unique?
    'Type': 'one-time', #could also be 'persistent'
    'ValidUntil' : datetime.utcnow() + timedelta(hours=2),
    'LaunchSpecification': {
        'ImageId': ami_id,
        'KeyName': keypair_name,
        'SecurityGroups': [group_name],
        #'InstanceType': ..., # set by the thing that finds the cheapest instance
        'Placement': {},
        'BlockDeviceMappings': [], #use if you want an EBS?
        'Monitoring': {'Enabled''': False},
    },

}

###
import boto3
import botocore
import pandas as pd #for the cheapest
from pprint import pprint
from datetime import datetime, timedelta
import itertools
import sys

client = boto3.client('ec2')
res = boto3.resource('ec2')

def get(client, name, opts):
    return client.get_paginator(name).paginate(**opts)

def get_filter(filterfunc, filters):
        filters = [ {'Name':k, 'Values':v} for k,v in filters.iteritems() ]
        return filterfunc( Filters=filters )

def get_filter_all(func, filters):
    return list(get_filter(func, filters).all())

def get_cheapest_spot_instance(client):
    prices = get(client, 'describe_spot_price_history', 
            {'InstanceTypes': instance_types,
             'StartTime' : datetime.now() - timedelta(days=1)
            })

    #convert the list of lists into a list of prices
    prices = list(itertools.chain(*[pl['SpotPriceHistory'] for pl in prices] ))

    #prices = list(prices)
    prices_df = pd.DataFrame.from_dict(prices)
    prices_df = prices_df[ prices_df.ProductDescription == 'Linux/UNIX' ]

    grouped = prices_df.groupby(['AvailabilityZone', 'InstanceType', 'ProductDescription'])
    first = grouped.first()
    first.sort_values(by=["SpotPrice"], inplace=True)

    first.reset_index(inplace=True)
    print first
    return first.to_dict(orient='records')

cheapest_instance = get_cheapest_spot_instance(client)
#lowest_price = float(cheapest_instance['SpotPrice']) + price_delta

def get_create_security_group(res, default_rules):
    sgs = get_filter_all(res.security_groups.filter, {'group-name': [group_name]} )
    sg = None
    if len(sgs) == 0:
        #create a new security group  
        print "Making new security group"
        sg = res.create_security_group(GroupName=group_name, Description=group_description)
    else:
        sg = sgs[0]

    try:
        sg.authorize_ingress( DryRun=False, IpPermissions = default_rules )
    except botocore.exceptions.ClientError as e:
        code = e.response['Error'].get('Code', 'Unknown')
        if code == "InvalidPermission.Duplicate":
            print("duplicate security entry already present!")
        else:
            #not sure what this was, so raise it up
            raise e

    print sg.ip_permissions

#### main

print "Cheapest instance found:"
print cheapest_instance
# print "Going to pay: %s" % lowest_price

"""
if interactive:
    raw_input("Proceed? Ctrl+C to stop")

instances  = get_filter_all(res.instances.filter, {'group-name': [group_name]})
if len(instances):
    print "Existing instance found with name: %s" % group_name
    #is it turned on??
    pprint(list(existing_instance.all()))
    sys.exit()
else:
    #need to create instance, let's start with making sure the security group is setup
    sg = get_create_security_group(res, sec_group_rules )
    instance_settings['SpotPrice'] = str(lowest_price)
    instance_settings['LaunchSpecification']['InstanceType'] = cheapest_instance['InstanceType'] 
    instance_settings['LaunchSpecification']['Placement']['AvailabilityZone'] = cheapest_instance['AvailabilityZone']
    # instance_settings['DryRun'] = True
    print instance_settings
    spot_requests = client.request_spot_instances(**instance_settings)
    print spot_requests 
    spot_ids = [k['SpotInstanceRequestId'] for k in spot_requests['SpotInstanceRequests']]
    waiter = client.get_waiter('spot_instance_request_fulfilled')
    print "Waiting for spot request to be fulfilled: %s" % spot_ids
    try:
        waiter.wait(SpotInstanceRequestIds=spot_ids)
    except Exception as e:
        print "something went wrong"
        print e
        print "Cancelling spot requests"
        client.cancel_spot_instance_requests(SpotInstanceRequestIds=spot_ids)

    print "Spot requests fulfilled!"
"""
