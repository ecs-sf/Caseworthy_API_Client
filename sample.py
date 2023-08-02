import configparser
import argparse
from cw_api import CWSession, CWObjects
import json
import csv 

#Grab command line arguments if present
parser = argparse.ArgumentParser()
parser.add_argument('-m','--mode', required=False, help="Choose mode between Train, UAT, and Prod", default='UAT')
parser.add_argument('-s','--source', required=True, help="Relative Path to Source File")
parser.add_argument('-o','--output', required=False, help="Relative Path to Output File", default='Output.csv')
args = parser.parse_args()
outputpath = args.output
sourcepath = args.source

#Pull secrets from config file
config = configparser.ConfigParser()
config.read('config.txt',encoding='utf-8')
if args.mode == 'Train':
    print('Runing against train DB')
    AccessKey = config.get('Train','AccessKey')
    Secret = config.get('Train','Secret')
    Mode = 'Train'
    TestClient = 24575
    defaultOrg = config.get('UAT','DefaultOrg')
    defaultProvider = config.get('UAT','DefaultProvider')
elif args.mode == 'UAT':
    print('Runing against UAT DB')
    AccessKey = config.get('UAT','AccessKey')
    Secret = config.get('UAT','Secret')
    Mode = 'UAT'
    TestClient = 24575
    defaultOrg = config.get('UAT','DefaultOrg')
    defaultProvider = config.get('UAT','DefaultProvider')
elif args.mode == 'Prod':
    print('Runing against Prod DB')
    AccessKey = config.get('Prod','AccessKey')
    Secret = config.get('Prod','Secret')
    Mode = 'Prod'
    TestClient = 24575
    defaultOrg = config.get('UAT','DefaultOrg')
    defaultProvider = config.get('UAT','DefaultProvider')
else:
    raise RuntimeError('Failure Parsing Configuration')

#Establish session and run basic functionality checks
session = CWSession(AccessKey, Secret, Mode, defaultOrg, defaultProvider, TestClient)

outputs = open(outputpath, 'w')
writer = csv.writer(outputs)
with open(sourcepath, encoding="utf-8-sig") as csvfile:
    clientreader = csv.DictReader(csvfile)
    counter = 0
    #Do something with CSV contents