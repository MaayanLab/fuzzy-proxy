import os
import urllib.request, urllib.parse
import traceback
from kubernetes import client, config
from dotenv import load_dotenv
from difflib import SequenceMatcher as SM
from flask import Flask, abort, redirect, request

app = Flask(__name__)

load_dotenv(override=True)

NAMESPACE = os.environ.get('KUBE_NAMESPACE', 'default')
REDIRECT_CODE = int(os.environ.get('REDIRECT_CODE') or 302)

def get_urls():
  try:
    config.load_incluster_config()
  except:
    config.load_kube_config()
  networking_v1 = client.NetworkingV1Api()
  if NAMESPACE == '*':
    ingresses = networking_v1.list_ingress_for_all_namespaces()
  else:
    ingresses = networking_v1.list_namespaced_ingress(NAMESPACE)
  return {
    ingress.metadata.annotations['maayanlab.cloud/ingress']
    for ingress in ingresses.items
    if ingress.metadata.annotations.get('maayanlab.cloud/ingress')
  }

# GENERIC

def best_match(query, urls):
  query_parsed = urllib.parse.urlparse(query)
  query_parts = list(filter(None, query_parsed.path.strip('/').split('/')))
  candidates = []
  for url in urls:
    url_parsed = urllib.parse.urlparse(url)
    if url_parsed.hostname.lower() != query_parsed.hostname.lower(): continue
    if not url_parsed.path.strip('/'): continue
    url_parts = url_parsed.path.strip('/').split('/')
    if len(url_parts) > len(query_parts): continue
    candidates.append((
      sum(
        SM(a=query_part.lower(), b=url_part.lower()).ratio()
        for query_part, url_part in zip(query_parts, url_parts)
      )/len(url_parts),
      url_parsed.scheme,
      '/'.join(['', *url_parts, *query_parts[len(url_parts):], *(
        # add trailing slash if it's in the query or in the ingress
        [''] if query_parsed.path.endswith('/') or url_parsed.path.endswith('/') else []
      )]),
    ))
  if not candidates: return
  _top_score, new_scheme, new_path = max(candidates)
  new_url = urllib.parse.urlunparse(
    query_parsed._replace(
      scheme=new_scheme,
      path=new_path,
    )
  )
  return new_url

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  try:
    urls = get_urls()
    new_url = best_match(request.url, urls)
    assert new_url is not None
    print(request.url, ' => ', new_url)
    return redirect(new_url, code=REDIRECT_CODE)
  except Exception:
    print(request.url)
    traceback.print_exc()
    abort(404)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
