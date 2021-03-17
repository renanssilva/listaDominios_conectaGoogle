from flask import Flask, render_template, url_for, redirect, session

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
    list_emails = []
    for email in values:
        list_emails.append(email['emailAddresses'][0]['value'])
    return sorted(list_emails)

def logout_goole():
    credentials = STORAGE.delete()
    return credentials

# Default route
@app.route('/')
def index():
    return render_template('index.html')


# Google login route
@app.route('/login')
def google_login():
    credentials = None

    if not credentials:
        authorize_credentials()
    return render_template('logado.html', enable=True)


# Google authorize route
# @app.route('/contatos')
# def google_authorize(*args):
#     emailAddresses = get_google_contacts()
#     return f"{emailAddresses}"

@app.route('/logout')
def logout():
    pass
    return 'logout'


if __name__ == '__main__':
    app.run(debug=True)
