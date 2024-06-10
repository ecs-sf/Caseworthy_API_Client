#Class that implements basic read/write against the Caseworthy API.
from datetime import datetime
import time
import hashlib
import hmac
import random
import string
import requests
import base64
from urllib import parse
import math
import json

class CWSession:
    def CreateRandomString (self,length = 10):
        rstring = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=length))
        return rstring

    def AssembleHMACKey (self, RequestMethod, RequestPath, RequestBody):
        RequestTimestamp = math.trunc(datetime.timestamp(datetime.now()))
        Nonce = self.CreateRandomString()
        if RequestBody != '':
            BodyHash = hashlib.md5(RequestBody.encode()).digest()
            BodyHashBase64 = base64.b64encode(BodyHash).decode('utf-8')
        else:
            BodyHashBase64 = ''
        RequestURL = parse.quote(self.BaseURL + RequestPath,'')
        message = (self.AccessKey + RequestMethod + RequestURL + str(RequestTimestamp) + str(Nonce) + BodyHashBase64).encode('utf-8')
        signature = hmac.new(
            key=base64.b64decode(self.Secret.encode("ascii")),
            msg=message,
            digestmod=hashlib.sha256
        )
        SignatureBase64 = base64.b64encode(signature.digest()).decode()
        hmackey = 'amx ' + self.AccessKey + ':' + SignatureBase64 + ':' + str(Nonce) + ':' + str(RequestTimestamp)
        return hmackey

    def TestAuth(self):
        RequestType = 'Post'.upper()
        RequestPath = 'TestSchema/TestItemPost'.lower()
        RequestBody = 'Test Post'

        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,RequestBody)
        }
        response  = requests.post(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = RequestBody
        )
        if response.status_code == 200:
            return
        else: 
            return(response.text)

    def __init__(self, AccessKey, Secret, Mode, DefaultOrg, DefaultProvider, TestClient=24575):
        #Set/Read Global Variables
        
        if Mode == 'Train':
            self.BaseURL = 'https://train.caseworthy.com/CaseWorthy.ClientAPI.Web/rest/'.lower()
        elif Mode == 'UAT':
            self.BaseURL = 'https://uat.caseworthy.com/CaseWorthy.ClientAPI.Web/rest/'.lower()
        elif Mode == 'Prod': 
            self.BaseURL = 'https://prod.caseworthy.com/CaseWorthy.ClientAPI.Web/rest/'.lower()
        else:
            raise RuntimeError('Invalid API Mode')
        self.AccessKey = AccessKey
        self.Secret = Secret
        self.DefaultOrg = DefaultOrg
        self.DefaultProvider = DefaultProvider

        if len(self.AccessKey) != 36:
            raise RuntimeError('Access Key Must be 36 characters')
        if len(self.Secret) != 88:
            raise RuntimeError('Secret must be 88 characters')
        SelfTest = self.TestAuth()
        if SelfTest == None:
            #print('Auth test successful')
            pass
        else: 
            print('Auth error')
            raise RuntimeError(SelfTest)
        BasicTest = self.ClientTests(TestClient)
        print('CW Session Established')
  
    def UpdateClient(self,id,clientfields,organization=None, provider=None):
        RequestType = 'Patch'.upper()
        RequestPath = 'CaseWorthy/Client_Patch'.lower()
        BodyDict = {'id':id, 'fields':clientfields}
        if organization == None:
            BodyDict['currentOrganizationID'] = self.DefaultOrg
        else:
            BodyDict['currentOrganizationID'] = organization
        if provider == None:
            BodyDict['currentProviderID'] = self.DefaultProvider
        else:
            BodyDict['currentProviderID'] = provider
        RequestBody =  json.dumps(BodyDict)
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.patch(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else: 
            print(response.text)
            print(response.request.body)
            raise RuntimeError(response.text)

    def GetClient(self,id,organization=None, provider=None):
        RequestType = 'Get'.upper()
        RequestPath = 'CaseWorthy/Client_Get'.lower()
        RequestBody = {'ID':id}
        if organization == None:
            RequestBody['currentOrganizationID'] = self.DefaultOrg
        else:
            RequestBody['currentOrganizationID'] = organization
        if provider == None:
            RequestBody['currentProviderID'] = self.DefaultProvider
        else:
            RequestBody['currentProviderID'] = provider
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.get(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else:  
            raise KeyError(response.text)
 
    def CreateClient(self,client):
        RequestType = 'Post'.upper()
        RequestPath = 'CaseWorthy/Client_Create'.lower()
        RequestBody =  json.dumps(client)
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.post(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else: 
            print(response.text)
            print(response.request.body)
            raise RuntimeError(response.text)

    def GetEnrollment(self,id,organization=None,provider=None):
        RequestType = 'Get'.upper()
        RequestPath = 'CaseWorthy/Enrollment_Get'.lower()
        RequestBody = {'ID':id
                       }
        if organization == None:
            RequestBody['currentOrganizationID'] = self.DefaultOrg
        else:
            RequestBody['currentOrganizationID'] = organization
        if provider == None:
            RequestBody['currentProviderID'] = self.DefaultProvider
        else:
            RequestBody['currentProviderID'] = provider
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.get(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        #print(response.text)
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else:  
            raise RuntimeError(response.text)
        
    def CreateEnrollment(self,enrollment):
        RequestType = 'Post'.upper()
        RequestPath = 'CaseWorthy/Enrollment_Create'.lower()
        #If patching an existing enrollment, act as the org and provider that own it.
        try:
            enrollment['currentOrganizationID']
        except:
            enrollment['currentOrganizationID'] = enrollment['OwnedByOrgID']
        try: 
            enrollment['currentProviderID']
        except:
            enrollment['currentProviderID']=enrollment['EnrollmentMembers'][0]['ProviderID']
        RequestBody =  json.dumps(enrollment)
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.post(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else: 
            print(response.text)
            #print(response.request.body)
            raise RuntimeError(response.text)
        
    def CreateServicePlan(self,client):
        return 'Not yet implemented'
        RequestType = 'Post'.upper()
        RequestPath = 'CaseWorthy/Client_Create'.lower()
        RequestBody =  json.dumps(client)
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.post(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else: 
            print(response.text)
            print(response.request.body)
            raise RuntimeError(response.text)
        

    def CreateGoal(self,client):
        return 'Not yet implemented'
        RequestType = 'Post'.upper()
        RequestPath = 'CaseWorthy/Client_Create'.lower()
        RequestBody =  json.dumps(client)
        Headers = {
            'Authorization':self.AssembleHMACKey(RequestType,RequestPath,str(RequestBody))
        }
        response  = requests.post(
            self.BaseURL+RequestPath,
            headers = Headers,
            data = str(RequestBody)
        )
        if response.status_code == 200:
            payload = json.loads(response.text)
            return payload
        else: 
            print(response.text)
            print(response.request.body)
            raise RuntimeError(response.text)

        
    def ClientTests(self, testclient):       
        try:
            ClientSample = self.GetClient(testclient)
        except:
            raise RuntimeError('Error getting sample client')
        try:
            response = self.UpdateClient(testclient,{'MiddleName': self.CreateRandomString()})
        except:
            raise RuntimeError('Error updating sample client')
        return

class CWObjects:
    def CWClient():
        client = {
            'FirstName': None, 
            'LastName': None, 
            'MiddleName': None, 
            'Suffix': None, 
            'NameDataQuality': 99, 
            'Multi_Genders': [99], 
            'Gender': 99, 
            'SSN': '', 
            'SSNDataQuality': 99, 
            'BirthDate': None, 
            'DOBDataQuality': 99, 
            'Multi_Races': [99], 
            'Race': 99, 
            'Ethnicity': 99, 
            'CitizenshipStatusID': None, 
            'PrimaryLanguage': 99, 
            'Bilingual': None, 
            'LimitedEnglishProficient': None, 
            'EnglishProficiency': None, 
            'VeteranStatus': 99, 
            'Restriction': 1, 
            'ScanCardID': None,
            'CustomFields':[
                {'Name': 'X_CDCRID', 'Value': None}, 
                {'Name': 'X_ChangesID', 'Value': None}, 
                {'Name': 'X_GMSID', 'Value': None}, 
                {'Name': 'X_HasAddress', 'Value': 102}, 
                {'Name': 'X_LanguageLearner', 'Value': 99}, 
                {'Name': 'X_LaunchpadID', 'Value': None}, 
                {'Name': 'X_MaritalStatus', 'Value': '9'}, 
                {'Name': 'X_ONEID', 'Value': None}, 
                {'Name': 'X_Pronouns', 'Value': '6'}, 
                {'Name': 'X_PronounsOther', 'Value': ''}, 
                {'Name': 'X_RTZAge', 'Value': None}, 
                {'Name': 'X_RTZShelter', 'Value': None}, 
                {'Name': 'X_SexualOrientation', 'Value': '99'}, 
                {'Name': 'X_SFJailID', 'Value': None}, 
                {'Name': 'X_VAEligible', 'Value': None}, 
                {'Name': 'X_YardiID', 'Value': None}
            ]
        }
        return client
    
    def CWEnrollment():
        enrollment = {
            'currentProviderID': None,
            'currentOrganizationID': None,
            'AccountID': None, 
            'BeginDate': None, 
            'EndDate': None, 
            'ProgramID': None, 
            'Status': None, 
            'SubStatus': None, 
            'FamilyID': None, 
            'Alt_FamilyID': None, 
            'FamilyOrIndividual': None, 
            'EnrollmentHMIS': None, 
            'EnrollmentMembers': None,
            'CustomFields': 
                [
                    {'Name': 'X_Cohort', 'Value': ''}, 
                    {'Name': 'X_ExpectedExitDate', 'Value': ''}, 
                    {'Name': 'X_ProbationEndDate', 'Value': ''}, 
                    {'Name': 'X_ProbationStartDate', 'Value': ''}, 
                    {'Name': 'X_Subtype', 'Value': ''}
                ]
        }
        return enrollment
    
    def CWEnrollmentMember():
        enrollmentmember = {
                'ClientID': None, 
                'Alt_ClientID': None, 
                'BeginDate': None, 
                'EndDate': None, 
                'ProviderID': None, 
                'RelationToHoH': None, 
                'EnrollmentMemberHMIS': None
        }
        return enrollmentmember
    
    def CWServicePlan():
        serviceplan = {
                "currentOrganizationID": None,
                "currentProviderID": None,
                "alt_ID": None,
                "customFields": [
                    {
                    "name": "string",
                    "value": "string"
                    }
                ],
                "enrollmentID": None,
                "alt_EnrollmentID": None,
                "clientID": None,
                "alt_ClientID": None,
                "planTypeID": None,
                "planBeginDate": None,
                "planEndDate": None,
                "actualCompletedDate": None,
                "description": None,
                "percentComplete": 0,
                "caseManagerID": None,
                "familyOrIndividual": 1,
                "contextID": None,
                "contextTypeID": None
                }
        return serviceplan
        
    def CWGoal():
        goal = {
                "currentOrganizationID": None,
                "currentProviderID": None,
                "alt_ID": None,
                "customFields": [
                    {
                    "name": "string",
                    "value": "string"
                    }
                ],
                "tableInfo": {
                    "foreignKey": {},
                    "primaryKey": {}
                },
                "clientID": None,
                "alt_ClientID": None,
                "goalTypeID": None,
                "planAttainDate": None,
                "actualAttainDate": None,
                "setDate": None,
                "caseNoteID": None,
                "percentComplete": 0,
                "userID": None,
                "alt_UserID": None,
                "responsibleParty": 0,
                "weight": 100,
                "typeID": None,
                "tierLevelSupport": None,
                "contextTypeID": None,
                "contextID": None,
                "providedByEntityID": None,
                "isClientInvolved": 1,
                "servicePlanGoals": {
                    "id": 0,
                    "currentOrganizationID": 0,
                    "currentProviderID": 0,
                    "alt_ID": "string",
                    "customFields": [
                    {
                        "name": "string",
                        "value": "string"
                    }
                    ],
                    "tableInfo": {
                    "foreignKey": {},
                    "primaryKey": {}
                    },
                    "goalID": 0,
                    "priority": 0,
                    "weight": 0,
                    "enrollmentServicePlanID": 0,
                    "alt_EnrollmentServicePlanID": "string"
                },
                "clientGoalSteps": [
                    {
                    "id": 0,
                    "currentOrganizationID": 0,
                    "currentProviderID": 0,
                    "alt_ID": "string",
                    "customFields": [
                        {
                        "name": "string",
                        "value": "string"
                        }
                    ],
                    "tableInfo": {
                        "foreignKey": {},
                        "primaryKey": {}
                    },
                    "stepSetDate": "2024-06-10T15:46:15.697Z",
                    "goalID": 0,
                    "goalStepTypeID": 0,
                    "status": 0,
                    "stepTargetDate": "2024-06-10T15:46:15.697Z",
                    "stepCompletionDate": "2024-06-10T15:46:15.697Z",
                    "responsibleParty": 0,
                    "percentComplete": 0,
                    "weight": 0,
                    "typeID": 0,
                    "target": "string",
                    "createdFormID": 0,
                    "lastModifiedFormID": 0,
                    "clientGoalStepExt": {
                        "id": 0,
                        "currentOrganizationID": 0,
                        "currentProviderID": 0,
                        "alt_ID": "string",
                        "customFields": [
                        {
                            "name": "string",
                            "value": "string"
                        }
                        ],
                        "tableInfo": {
                        "foreignKey": {},
                        "primaryKey": {}
                        },
                        "description": "string",
                        "serviceTypeID": 0,
                        "hourBudget": 0,
                        "frequency": 0,
                        "accountID": 0
                    }
                    }
                ]
                }
        return goal