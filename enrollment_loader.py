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
inputfile = 'NewGetCareEnrollmentsv2.csv'
outputs = open(inputfile+'_results.csv', 'w')
writer = csv.writer(outputs)
with open(inputfile, encoding="utf-8-sig") as csvfile:
    clientreader = csv.DictReader(csvfile)
    counter = 0
    for row in clientreader:
        clientid = row['EntityID']
        try:
            cwclient = session.GetClient(clientid)
        except:
            print('Client not found')
            writer.writerow([clientid, row['ProgramID'], 'Client Not Found Error'])
            continue
        cwfamily = cwclient['FamilyMember']['FamilyID']
        record = CWObjects.CWEnrollment()
        enrollmentmember = CWObjects.CWEnrollmentMember()
        record['currentProviderID'] = ProviderID
        record['currentOrganizationID'] = OrganizationID
        record['BeginDate'] = row['BeginDate']
        record['EndDate'] = row['EndDate']
        record['ProgramID'] = row['ProgramID']
        record['Status'] = row['EnrollmentStatus']
        record['FamilyID'] = cwfamily
        record['FamilyOrIndividual'] = 1
        #record['LegacyID'] = row['LegacyID']
        record['CustomFields'] = None
        enrollmentmember['ClientID'] = clientid
        enrollmentmember['BeginDate'] = row['BeginDate']
        enrollmentmember['EndDate'] = row['EndDate']
        enrollmentmember['ProviderID'] = ProviderID
        enrollmentmember['RelationToHoH'] = 1
        enrollmentmember['Restriction'] = 1
        record['EnrollmentMembers']=[enrollmentmember]
        try:
            newenrollment = session.CreateEnrollment(record)
            print('Enrollment created')
            writer.writerow([clientid, row['ProgramID'], newenrollment['ID']])
        except:
            print('Enrollment not created')
            writer.writerow([clientid, row['ProgramID'], 'Error'])
        counter += 1
        #if counter >= 1:
        #    break
        record = None
outputs.close()