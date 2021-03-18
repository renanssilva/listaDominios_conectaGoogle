
# from flask import Flask, render_template, url_for, redirect, session
from flask import Flask, render_template
import httplib2
from googleapiclient import discovery

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


app = Flask(__name__)

CLIENT_SECRET = 'credentials.json'
SCOPE = 'https://www.googleapis.com/auth/contacts.other.readonly'
STORAGE = Storage('credentials.storage')

print(STORAGE)


def authorize_credentials():
    # Fetch credentials from storage
    credentials = STORAGE.get()
    # If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials


def get_google_contacts():
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://people.googleapis.com/$discovery/rest?version=v1')
    service = discovery.build('people', 'v1', http=http, discoveryServiceUrl=discoveryUrl)
    results = service.otherContacts().list(readMask='emailAddresses', pageSize=1000).execute()
    values = results['otherContacts']
    print(len(values))

    values_list = []

    for email in values:
        values_list.append(email['emailAddresses'][0]['value'])

    print(values_list)

    return values_list


def format_googleContacts(contactList: list):
    dictContact = {}

    for addressesEmail in contactList:
        domain = addressesEmail.split('@')[1]

        if not dictContact:
            dictContact[domain] = [addressesEmail]
        elif domain in dictContact.keys():
            dictContact[domain] += [addressesEmail]
        else:
            dictContact[domain] = [addressesEmail]

    orderDictContact = sorted(dictContact.items())

    return dict(orderDictContact)


# authorize_credentials()

# Default route
@app.route('/')
def index():
    return render_template('index.html')


# Google login route
@app.route('/login')
def google_login():

    authorize_credentials()

    contacts = get_google_contacts()

    formatContacts = format_googleContacts(contacts)

    return render_template('logado.html', enable=True, contacts=formatContacts)


@app.route('/logout')
def logout_goole():
    STORAGE.delete()
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
