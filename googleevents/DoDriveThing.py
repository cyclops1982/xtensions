import requests
import json
from random import random
import urllib.parse

def GetAccessToken():
    with open("./accesstoken.json", "r") as accesstokenfile:
        accessTokenJson = json.load(accesstokenfile)
        
        accessToken = accessTokenJson['access_token']
        return  accessToken



def GetDrives(qfilter=""):
    access_token = GetAccessToken()

    drives = []
    qencoded = urllib.parse.quote_plus(qfilter)
    fields = urllib.parse.quote_plus("drives/name,drives/id,drives/hidden,nextPageToken")
    nextpage = None
    while True:
        url = f"https://www.googleapis.com/drive/v3/drives?pageSize=100&fields={fields}&useDomainAdminAccess=true&q={qencoded}"
        if nextpage != None:
            url = f"{url}&pageToken={nextpage}"

        response = requests.get(url, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)})
        if response.status_code != 200:
            print(f"Failed to retrieve drives!!!: {response.status_code}")
            print(response.content)
            return

        

        jsonResponse = json.loads(response.content)
        #print (json.dumps(jsonResponse, indent=4))

        for drive in jsonResponse['drives']:
            drives.append(drive)
        if "nextPageToken" in jsonResponse:
            nextpage = jsonResponse['nextPageToken']
            # print(f"Got Drives: {nextpage} - {len(jsonResponse['drives'])}")
        else:
            break
        
    return drives

def CreateDrive(driveName):
    access_token = GetAccessToken()
    
    response = requests.post(f"https://www.googleapis.com/drive/v3/drives?requestId={random()}" , 
        headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)},
        json={"name": driveName})


    if response.status_code != 200:
        print(f"Failed to create drive: {response.status_code}")
        print(response.content)
        return

    print("Created drive!")
    print(json.loads(response.content))


def DeleteDrive(driveId):
    access_token = GetAccessToken()


    response = requests.delete(f"https://www.googleapis.com/drive/v3/drives/{driveId}?allowItemDeletion=true&useDomainAdminAccess=true" , 
        headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)})
    

    if response.status_code != 204:
        print(f"Failed to delete drive {driveId}: {response.status_code}")
        print(response.content)
        return

    print("Drive Deleted!")


def main():
    #for i in range(1, 2500):
    #    name = f"ZZZ_RDA_Drive_{i}"
    #    CreateDrive(name)
    drives = GetDrives()
    count = 0
    for drive in drives:
        drivename = drive['name']
        driveid = drive['id']
        hidden = drive['hidden']
        print(f"{drivename} - {driveid} - {hidden}")
        count = count + 1
        if count > 2499 and (drivename[0:3] == "ZZ_" or drivename[0:4] == "ZZZ_"):
            DeleteDrive(driveid)

    print (f"There are {count} drives")

if __name__ == '__main__':
    main()
