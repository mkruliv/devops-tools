# ControlByTag
Script for controlling AWS EC and RDS instances (start/stop) by AWS Environment tag

### Usage: 
```
controlbytag.py [-h] --region REGION --env_tag ENV_TAG
           [--type {EC2,RDS,All}] [-start] [-stop] [-showvpc]

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       AWS region
  --env_tag ENV_TAG     AWS resources Environment tag
  --type {EC2,RDS,All}  Instance Type
  -start                Start tagged instances.
  -stop                 Stop tagged instances.
  -showvpc              Show information about tagged vpc.
```