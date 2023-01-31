import requests
import json
from random import random
import urllib.parse

def GetAccessToken():
    with open("./accesstoken.json", "r") as accesstokenfile:
        accessTokenJson = json.load(accesstokenfile)
        
        accessToken = accessTokenJson['access_token']
        return  accessToken

def GetFileDetails(fileid, driveId="root"):
    access_token = GetAccessToken()
    url = f"https://www.googleapis.com/drive/v3/files/{fileid}?fields=*"
    if driveId != "root":
        url = f"{url}&supportsAllDrives=true&driveId={driveId}"

    response = requests.get(url, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)})
    if response.status_code != 200:
        print(f"Failed to retrieve file details!!!: {response.status_code}")
        print(response.content)
        return
    
    return json.loads(response.content)

def GetFileRevision(fileId, driveId="root"):
    access_token = GetAccessToken()
    url = f"https://www.googleapis.com/drive/v3/files/{fileId}/revisions?fields=*"

    if driveId != "root":
        url = f"{url}&supportsAllDrives=true&driveId={driveId}"

    response = requests.get(url, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)})
    if response.status_code != 200:
        print(f"Failed to retrieve file details!!!: {response.status_code}")
        print(response.content)
        return

    return json.loads(response.content)

def GetFilesFromDrive(driveId = "root", qfilter=""):
    access_token = GetAccessToken()

    files = []
    nextpage = None
    qencoded = urllib.parse.quote_plus(qfilter)
    fields = urllib.parse.quote_plus("files/name,files/id,files/mimeType,nextPageToken")
    while True:
      
        url = f"https://www.googleapis.com/drive/v3/files?pageSize=100&q={qencoded}&fields={fields}"
        if driveId != "root":
            url = f"{url}&corpora=drive&driveId={driveId}&supportsAllDrives=true&includeItemsFromAllDrives=true"
        if nextpage != None:
            url = f"{url}&pageToken={nextpage}"

        print(f"Will be calling: {url}")
        response = requests.get(url, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(access_token)})
        if response.status_code != 200:
            print(f"Failed to retrieve files!!!: {response.status_code}")
            print(response.content)
            return


        jsonResponse = json.loads(response.content)

        for file in jsonResponse['files']:
            files.append(file)
        if "nextPageToken" in jsonResponse:
            nextpage = jsonResponse['nextPageToken']
            print(f"Got Drives: {nextpage} - {len(jsonResponse['files'])}")
        else:
            break
        
    return files


def main():
#    files = GetFilesFromDrive("0AJP9GbOnBIrVUk9PVA", "mimeType = 'application/vnd.google-apps.folder'")

    files = GetFilesFromDrive()
    for file in files:
        drivename = file['name']
        driveid = file['id']
        print(f"===== {drivename} - {driveid} - {file['mimeType']}")
        rev = GetFileRevision(file['id'])
        print(json.dumps(rev))
    #print(json.dumps(GetFileDetails("1ZVSgoC2n1p4ftx1oGaU0jnb8Ck7HKjn7","0AJPIOamKTtvGUk9PVA")))
       


if __name__ == '__main__':
    main()
