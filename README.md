# daac-broker

This is the main frontend for DCaaS. It uses auth0 for authenication. It will automatically create, and terminate Desktop Containers upon OpenShift.

## DCaaS Run Demo

!['DCaaS Run Demo'](./demo/daac-run.gif)

# Required Env Variables

```bash
PROJECT_NAME=DCaaS API Broker

# Postgres
POSTGRES_SERVICE_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=guac
POSTGRES_PASSWORD=guac_pass
POSTGRES_DB=guacamole_db

SECRET_KEY=SOME SECRET VALUE

LOG_LEVEL=debug
```

### Service Account

* need to reduce the access level for this service account.

```bash
oc create serviceaccount guacrobot

oc policy add-role-to-user admin -z guacrobot

# Check Bindings
oc get rolebindings
NAME                    ROLE                    USERS                                   GROUPS                        SERVICE ACCOUNTS   SUBJECTS
admin                   /admin                  snowjet
admin-0                 /admin                                                                                        guacrobot
system:deployers        /system:deployer                                                                              deployer
system:image-builders   /system:image-builder                                                                         builder
system:image-pullers    /system:image-puller                                            system:serviceaccounts:guac
```

### OpenShift
```
oc new-app --name guac-api \
    -e POSTGRES_SERVICE_HOST='127.0.0.1' \
    -e POSTGRES_USER='guac' \
    -e POSTGRES_PASSWORD='guac_pass' \
    -e POSTGRES_DATABASE='guacamole_db' \
    -e APP_HOME=flask https://github.com/snowjet/daac-broker.git
```

## Local Run

create a .env file with the required env variables
```bash
PROJECT_NAME=DCaaS API Broker

# Postgres
POSTGRES_SERVICE_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=guac
POSTGRES_PASSWORD=guac_pass
POSTGRES_DB=guacamole_db

# Auth0
client_id=''
client_secret=''
auth0_domain=''
daac_redirect_domain=''

# Guac Admin Password
GUACADMIN_PASSWORD=''

# Project / Namespace name in OpenShift
NAMESPACE=''

# Guacamole Route 
GUAC_URL= ''

SECRET_KEY=SOME SECRET VALUE
LOG_LEVEL=debug
```

Port forward the posgtres database running on openshfit to the laptop
```
oc port-forward pod/postgres-1-<random> 5432:5432
```

The run python locally
```bash
python3 wsgi.py
```

Browse to http://127.0.0.1:5000