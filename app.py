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
    print('1')
    credentials = STORAGE.get()
    print('2')
    # If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        print('3')
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        print('4')
        http = httplib2.Http()
        print('5')
        credentials = run_flow(flow, STORAGE, http=http)
        print('6')
    print('7')
    return credentials

def get_google_contacts():
    credentials = authorize_credentials()
    print("credentials", credentials)
    http = credentials.authorize(httplib2.Http())
    print('htto', http)
    discoveryUrl = ('https://people.googleapis.com/$discovery/rest?version=v1')
    service = discovery.build('people', 'v1', http=http, discoveryServiceUrl=discoveryUrl)
    # print("service", service)
    # service = discovery.build('people', 'v1', http=http)

    results = service.otherContacts().list(readMask='emailAddresses', pageSize=1000).execute()
    print('results', results)
    print(results['otherContacts'])
    print(results['otherContacts'][0])
    # values = results['otherContacts']
    values = results['otherContacts']
    # [50]['emailAddresses'][0]['value']
    print(len(values))
    list_emails = []
    for email in values:
        list_emails.append(email['emailAddresses'][0]['value'])

    print(type(values))

    return sorted(list_emails)

# credentials = authorize_credentials()

def logout_goole():
    credentials = STORAGE.delete()
    return credentials

# authorize_credentials()

# Default route
@app.route('/')
def index():
    return render_template('index.html')


# Google login route
@app.route('/login')
def google_login():
    # redirect_uri = url_for('google_authorize', _external=True)
    credentials = None

    if not credentials:
        print("Certinho")
        credentials = authorize_credentials()
        print(credentials)
    return render_template('logado.html', enable=True)


# Google authorize route
@app.route('/contatos')
def google_authorize(*args):
    emailAddresses = get_google_contacts()
    return f"{emailAddresses}"



@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
