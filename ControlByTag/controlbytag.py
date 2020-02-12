#!/usr/bin/python3
"""
Script for controlling AWS EC and RDS instances (start/stop) by AWS Environment tag
usage: control.py [-h] --region REGION --env_tag ENV_TAG
                  [--type {EC2,RDS,All}] [-start] [-stop] [-showvpc]

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       AWS region
  --env_tag ENV_TAG     AWS resources Environment tag
  --type {EC2,RDS,All}  Instance Type
  -start                Start tagged instances.
  -stop                 Stop tagged instances.
  -showvpc              Show information about tagged vpc.
"""
import sys
import json
import boto3
import time
from botocore.exceptions import ClientError
import argparse

#Get tags for RDS Database
def get_tags_for_db(db):
    instance_arn = db['DBInstanceArn']
    instance_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
    return instance_tags['TagList']

def start_instances(instance_type):
    if instance_type == 'RDS' or instance_type == 'All':
        print("Start DB instances")
        for rds_instance in rdsinstances:        
            db_tags = get_tags_for_db(rds_instance)
            if db_tags[0]["Value"] == env_tag and rds_instance['DBInstanceStatus'] == 'stopped':
                response = rds.start_db_instance(DBInstanceIdentifier=rds_instance['DBInstanceIdentifier'])
                print(response)
        #Wait 1m until DB started and run instances after
        print("Wait until DB started") 
        time.sleep(60)
    if instance_type == 'EC2' or instance_type == 'All':
        print("Start EC2 Instances")
        for instance in ec2.instances.filter(Filters=filters):            
            if instance.state['Name'] ==  'stopped':
                try:
                    client.start_instances(InstanceIds=[instance.id], DryRun=True)
                except ClientError as e:
                    if 'DryRunOperation' not in str(e):
                        raise
                # Dry run succeeded, run start_instances without dryrun
                try:
                    response = client.start_instances(InstanceIds=[instance.id], DryRun=False)
                    print(response)
                except ClientError as e:
                    print(e)

def stop_instances(instance_type):
    if instance_type == 'EC2' or instance_type == 'All':
        print("Stop EC2 instances")
        for instance in ec2.instances.filter(Filters=filters):            
            if instance.state['Name'] ==  'running':
                # Do a dryrun first to verify permissions
                try:
                    client.stop_instances(InstanceIds=[instance.id], DryRun=True)
                except ClientError as e:
                    if 'DryRunOperation' not in str(e):
                        raise

                # Dry run succeeded, call stop_instances without dryrun
                try:
                    response = client.stop_instances(InstanceIds=[instance.id], DryRun=False)
                    print(response)
                except ClientError as e:
                    print(e)
    if instance_type == 'RDS' or instance_type == 'All':
        print("Stop RDS instances")
        for rds_instance in rdsinstances:        
            db_tags = get_tags_for_db(rds_instance)
            if db_tags[0]["Value"] == env_tag and rds_instance['DBInstanceStatus'] == 'available':
                response = rds.stop_db_instance(DBInstanceIdentifier=rds_instance['DBInstanceIdentifier'])
                print(response)
#Show information about VPC            
def show_vpc_info():
    vpcs = list(ec2.vpcs.filter(Filters=filters))
    for vpc in vpcs:
        response = client.describe_vpcs(
            VpcIds=[
                vpc.id,
            ]
        )
        print(json.dumps(response, sort_keys=True, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control AWS EC and RDS instances (start/stop) by environment tag.', add_help=True)
    parser.add_argument('--region', type=str,  help="AWS region", required=True)
    parser.add_argument('--env_tag', type=str,  help="AWS resources tag", required=True)
    parser.add_argument('--type', help = "Instance Type", choices=['EC2', 'RDS', 'All'], default='All')    
    parser.add_argument('-start', dest='start', action='store_true', help="Start tagged instances.")
    parser.add_argument('-stop', dest='stop', action='store_true', help="Stop tagged instances.")
    parser.add_argument('-showvpc', dest='showvpc', action='store_true', help="Show information about tagged vpc.")
    
    cmdargs = parser.parse_args()
    args = vars(parser.parse_args())
    if not any(args.values()):
        parser.error('No arguments provided.')
    region = cmdargs.region
    #VPC environment tag
    env_tag = cmdargs.env_tag
    #Tagged instance type
    instance_type = cmdargs.type
    #Add filter for Environment 
    filters = [{'Name':'tag:Environment', 'Values':[env_tag]}]
    #Action for the instances from the command line - stop or start

    ec2 = boto3.resource('ec2', region_name=region)
    client = boto3.client('ec2')

    rds = boto3.client('rds', region_name=region)
    rdsinstances = rds.describe_db_instances()['DBInstances']
    
    if cmdargs.start is False and cmdargs.stop is False:
        print("At least one action is required -stop or -start")
    if cmdargs.showvpc:        
        show_vpc_info()
    if cmdargs.start:
        start_instances(instance_type)
    if cmdargs.stop:
        stop_instances(instance_type)