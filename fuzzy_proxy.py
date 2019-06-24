import os
import ssl
import json
import base64
import urllib.request, urllib.parse
from dotenv import load_dotenv
from difflib import SequenceMatcher as SM
from flask import Flask, redirect, request

app = Flask(__name__)

load_dotenv(override=True)
context = ssl._create_unverified_context()

# RANCHER SPECIFIC
BASE_RANCHER_URL = os.environ['RANCHER_URL']
RANCHER_AUTHORIZATION = 'Basic ' + base64.b64encode(
  (os.environ['RANCHER_TOKEN'] + ':' + os.environ['RANCHER_SECRET']).encode()
).decode('ascii')
RANCHER_CLUSTER_ID = os.environ['RANCHER_CLUSTER_ID']
RANCHER_PROJECT_ID = os.environ['RANCHER_PROJECT_ID']

def get_rules():
  req = urllib.request.urlopen(
    urllib.request.Request(
      BASE_RANCHER_URL + '/v3/project/{clusterId}:{projectId}/ingresses'.format(clusterId=RANCHER_CLUSTER_ID, projectId=RANCHER_PROJECT_ID),
      method='GET',
      headers={
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': RANCHER_AUTHORIZATION,
      },
    ),
    context=context,
  )
  data = json.loads(req.read().decode('utf-8'))
  return {
    d['id']: r['host'] + p['path']
    for d in data['data']
    for r in d['rules']
    for p in r['paths']
    if p.get('path')
  }

# GENERIC

def similarity_query(query, rules):
  return [
    (SM(a=query.lower(), b=value.lower()).ratio(), key)
    for key, value in rules.items()
  ]

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  try:
    rules = get_rules()
    parsed_url = urllib.parse.urlparse(request.url)
    parsed_url_base_path = '/' + parsed_url.path[1:].split('/')[0]
    parsed_url_remaining_path = '/' + '/'.join(parsed_url.path[1:].split('/')[1:])
    similar = similarity_query(parsed_url.hostname + parsed_url_base_path, rules)
    top = max(similar)[1]
    top_url = rules[top].split('/')
    new_url = urllib.parse.urlunparse(
      parsed_url._replace(
        netloc=top_url[0],
        path=top_url[1] + parsed_url_remaining_path,
      )
    )
    print(request.url, ' => ', new_url)
    return redirect(new_url, code=301)
  except Exception as e:
    print(e)
    return not_found()

def not_found():
  return 'Page not found'

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
