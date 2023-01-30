# fuzzy-proxy
A fuzzy-matching proxy forwarder. Redirects users to the closest (difflib similarity) ingress rule.

Currently designed to work with ingress-nginx + maayanlab.cloud/ingress annotations but could easily be repurposed to work with any url rule provider.
It works better with case sensitive ingress matchers (allowing case to be corrected by this service).

`docker pull maayanlab/fuzzy-proxy:1.2.5`

## Environment settings
Uses a .env file during development (or just load the environment).

```env
KUBE_NAMESPACE=
REDIRECT_CODE=
```
