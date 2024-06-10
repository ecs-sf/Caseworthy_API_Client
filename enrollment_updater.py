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
outputs = open('outputs.csv', 'w')
writer = csv.writer(outputs)
with open('sanctuary_exits_20240209.csv', encoding="utf-8-sig") as csvfile:
    clientreader = csv.DictReader(csvfile)
    counter = 0
    for row in clientreader:
        enrollmentid=row['EnrollmentID']
        clientid = row['EntityID']
        enroll = session.GetEnrollment(enrollmentid)
        enrollmember = enroll['EnrollmentMembers'][0]
        enroll['EndDate'] = row['EndDate']
        enroll['Status'] = 200
        #enrollmember['ClientID'] = row['Client ID']
        #enrollmember['BeginDate'] = row['BeginDate']
        if int(enrollmember['ClientID']) == int(clientid):
            print('ClientIDMatches, Update EndDate')
            enrollmember['EndDate'] = row['EndDate']
        else:
            print('Client ID Non-Match', clientid, enrollmember['ClientID'])
        enrollmemberlist = [enrollmember]
        enroll['EnrollmentMembers'] = enrollmemberlist
        for item in enroll['CustomFields']:
            if item['Name'] == 'X_Subtype' and (item['Value']== '' or item['Value']=='0'):
                print('Update Subtype')
                item['Value'] = '205'
        try:
            patchedenroll = session.CreateEnrollment(enroll)
            print('Enrollment Created')
            writer.writerow([row['EntityID'], patchedenroll['ID']])
            #print(enroll)
        except:
            print('Enrollment not created')
            print(enroll)
            writer.writerow(enrollmentid, 'Error')
        counter += 1
        record = None
outputs.close()