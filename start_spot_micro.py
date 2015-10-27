#!/usr/bin/env python
"""
starts a really cheap and small instance for testing
"""

ami_id = ""
group_name = "cheapdebug" #will only run one of these
instance_types = ["t1.micro", 'm4.large']
price_delta = 0.0001 #delta to increase the price by
interactive = True

import boto3
import pandas as pd #for the cheapest
from pprint import pprint
from datetime import datetime, timedelta
import itertools

client = boto3.client('ec2')
#ec2 = boto3.resource('ec2')

def get_spot_price(client, **kwargs):
    page = client.get_paginator('describe_spot_price_history')
    return page.paginate(**kwargs)
    #prices = ec2.describe_spot_price_history()
    #pprint(prices)
    #for p in prices:
        #pprint(p)

def get_cheapest_spot_instance(client):
    prices = get_spot_price(client, InstanceTypes=instance_types,
                StartTime = datetime.now() - timedelta(days=1)    
            )

    #convert the list of lists into a list of prices
    prices = list(itertools.chain(*[pl['SpotPriceHistory'] for pl in prices] ))

    #prices = list(prices)
    prices_df = pd.DataFrame.from_dict(prices)
    prices_df = prices_df[ prices_df.ProductDescription == 'Linux/UNIX' ]

    grouped = prices_df.groupby(['AvailabilityZone', 'InstanceType', 'ProductDescription'])
    first = grouped.first()
    first.sort_values(by=["SpotPrice"], inplace=True)

    first.reset_index(inplace=True)
    return first.to_dict(orient='records')[0]

def get_instances(client, **kwargs):
    page = client.get_paginator('describe_spot_price_history')
    return page.paginate(**kwargs)

def get_instances_by_groupname(client, group_name):
    return get_instances(client, Filters=[
        {'Name': 'group-name', 'Values': [group_name]}
    ]

cheapest_instance = get_cheapest_spot_instance(client)
lowest_price = float(cheapest_instance['SpotPrice']) + price_delta

if interactive:
    print "Cheapest instance found:"
    print cheapest_instance
    print "Going to pay: %s" % lowest_price
    raw_input("Proceed? Ctrl+C to stop")




