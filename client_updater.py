import configparser
import argparse
from cw_api import CWSession, CWObjects
import json

#Grab command line arguments if present
parser = argparse.ArgumentParser()
parser.add_argument('-m','--mode', required=False, help="Choose mode between Train, UAT, and Prod", default='UAT')
parser.add_argument('-o','--organization', required=True, help='Declare a default organization id for this session')
parser.add_argument('-p','--provider',required=True,help='Declare a default provider id for this session')
args = parser.parse_args()

#Pull secrets from config file
config = configparser.ConfigParser()
config.read('config.txt',encoding='utf-8')
TestClient = 24575
ProviderID = args.provider
OrganizationID = args.organization
if args.mode == 'Train':
    print('Runing against train DB')
    AccessKey = config.get('Train','AccessKey')
    Secret = config.get('Train','Secret')
    Mode = 'Train'
elif args.mode == 'UAT':
    print('Runing against UAT DB')
    AccessKey = config.get('UAT','AccessKey')
    Secret = config.get('UAT','Secret')
    Mode = 'UAT'
elif args.mode == 'Prod':
    print('Runing against Prod DB')
    AccessKey = config.get('Prod','AccessKey')
    Secret = config.get('Prod','Secret')
    Mode = 'Prod'
else:
    raise RuntimeError('Failure Parsing Configuration')

#Establish session and run basic functionality checks
session = CWSession(AccessKey, Secret, Mode, OrganizationID, ProviderID, TestClient)

#Read update csv
import csv
inputfile = 'GetCareIDs.csv'
outputs = open(inputfile+'_results.csv', 'w')
writer = csv.writer(outputs)
with open(inputfile, encoding="utf-8-sig") as csvfile:
    clientreader = csv.DictReader(csvfile)
    counter = 0
    for row in clientreader:
        clientid = row['EntityID']
        rtz_id = row['GC_ID']
        patch_dict = {'X_RTZAge': rtz_id}
        try:
            updated_client = session.UpdateClient(clientid, patch_dict, OrganizationID, ProviderID)
            print('Client Updated')
            writer.writerow([clientid, rtz_id])
            #print(enroll)
        except:
            print('not updated')
            writer.writerow(enrollmentid, 'Error')
        counter += 1
        record = None
outputs.close()