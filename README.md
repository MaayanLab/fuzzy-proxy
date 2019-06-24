# fuzzy-proxy
A fuzzy-matching proxy forwarder. Redirects users to the closest (difflib similarity) ingress rule.

Currently designed to work with rancher but could easily be repurposed to work with any url rule provider.

## Environment settings
Uses a .env file during development (or just load the environment).

```env
RANCHER_URL=
RANCHER_TOKEN=
RANCHER_SECRET=
RANCHER_CLUSTER_ID=
RANCHER_PROJECT_ID=
```
