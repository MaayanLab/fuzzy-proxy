# fuzzy-proxy
A fuzzy-matching proxy forwarder. Redirects users to the closest (difflib similarity) ingress rule.

Currently designed to work with rancher but could easily be repurposed to work with any url rule provider.

`docker pull maayanlab/fuzzy-proxy:1.1.3`

## Environment settings
Uses a .env file during development (or just load the environment).

```env
KUBE_NAMESPACE=
REDIRECT_CODE=
```
