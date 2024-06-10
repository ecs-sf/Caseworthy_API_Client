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
inputfile = 'NewGetCareClients.csv'
outputs = open(inputfile+'_results.csv', 'w')
writer = csv.writer(outputs)
with open(inputfile, encoding="utf-8-sig") as csvfile:
    clientreader = csv.DictReader(csvfile)
    counter = 0
    for row in clientreader:
        record = CWObjects.CWClient()
        record['FirstName'] = row['FirstName']
        record['LastName'] = row['LastName']
        record['NameDataQuality'] = row['NameDataQuality']
        record['BirthDate'] = row['BirthDate']
        record['DOBDataQuality'] = row['DOBDataQuality']
        #record['Ethnicity'] = row['Ethnicity']
        record['ssn'] = row['SSN']
        record['SSNDataQuality'] = row['SSNDataQuality']
        record['PrimaryLanguage'] = row['PrimaryLanguage']
        record.pop('Race') #= row['race']
        record.pop('Gender')
        record['Multi_Races'] = json.loads(row['Multi_Races'])
        record['Multi_Genders'] = json.loads(row['Multi_Genders'])
        record['VeteranStatus'] = row['VeteranStatus']
        for field in record['CustomFields']:
            #if field['Name'] == 'X_Pronouns':
            #    field['Value'] = row['pronouns']
            #if field['Name'] == 'X_RTZShelter':
            #    field['Value'] = row['patient_id']
            #if field['Name'] == 'X_ONEID':
            #    field['Value'] = row['one_id']
            if field['Name'] == 'X_SexualOrientation':
                field['Value'] = row['X_SexualOrientation']           
            if field['Name'] == 'X_RTZAge':
                field['Value'] = row['X_RTZAge']
            if field['Name'] == 'X_MaritalStatus':
                field['Value'] = row['X_MaritalStatus']
        try:
            newclient = session.CreateClient(record)
            #print('Client Created')
            writer.writerow([row['X_RTZAge'], newclient['ID']])
        except:
            print('Client not created')
            writer.writerow([row['X_RTZAge'], 'Error'])
        counter += 1
        #if counter >= 5:
        #    break
        record = None
outputs.close()