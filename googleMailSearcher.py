
from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import pprint

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
LST_SCOPES = ['https://mail.google.com/','https://www.googleapis.com/auth/gmail.modify','https://www.googleapis.com/auth/gmail.readonly']
SEARCH_STRING = 'subject:"SUBJECT" "Message Content"'

# Be sure to replace the below with files that match your script, see screenshots
CLIENT_KEY_FILE = 'client_secret.json'
APPLICATION_NAME = 'googleMailSearcher'
SERVICE_ACCOUNT_EMAIL = 'googlemailsearcher@appspot.gserviceaccount.com'
SERVICE_ACCOUNT_PKCS12_FILE_PATH = 'googleMailSearcher.p12'

def get_delegated_credentialed_service(scopes, emailAddress):
    f = file(SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
    key = f.read()
    f.close()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_KEY_FILE, scopes=scopes)
    delegated_credentials = credentials.create_delegated(emailAddress)
    http = httplib2.Http()
    http = delegated_credentials.authorize(httplib2.Http())
    return discovery.build('gmail', 'v1', http=http)

def ListMessagesMatchingQuery(service, user_id, query):
  try:
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except TypeError, error:
    print("Odd error: %s" % error)

def main():
    inputFile = open("domain_users.csv")
    emailAddresses = map(lambda line: line.strip(), inputFile.readlines())
    inputFile.close()

    results = {}
    for emailAddress in emailAddresses:
        try:
            results[emailAddress] = iterateEmailAccount(emailAddress)
            print("%s:%s" %(emailAddress, results[emailAddress]))
        except:
            pass

    resultFile = open("results.csv", "w")
    for k,v in results.items():
        resultFile.write("%s,%s\n" %(k,v))
    resultFile.close()

def iterateEmailAccount(emailAddress):
    service = get_delegated_credentialed_service(LST_SCOPES, emailAddress)
    matchingMessages = ListMessagesMatchingQuery(service, emailAddress, SEARCH_STRING)
    return len(matchingMessages) #returns a count of messages matching search parameters, bu you can do anything you want with this.

if __name__ == '__main__':
    main()
