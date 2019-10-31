# daac-broker

# Required Env Variables

```bash
PROJECT_NAME=DCaaS API Broker

# Postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=guac
POSTGRES_PASSWORD=guac_pass
POSTGRES_DB=guacamole_db

SECRET_KEY=SOME SECRET VALUE

LOG_LEVEL=debug

# Auth0
client_id=''
client_secret=''
auth0_domain=''
ROOT_APP_DOMAIN=''
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
oc new-app --name guac-api -e POSTGRES_HOST='127.0.0.1' -e POSTGRES_USER='guac' -e POSTGRES_PASSWORD='guac_pass' -e POSTGRES_DATABASE='guacamole_db' -e APP_HOME=flask https://github.com/snowjet/daac-broker.git
```

## Local Run

```
export POSTGRES_HOST='127.0.0.1'
export POSTGRES_USER='guac'
export POSTGRES_PASSWORD='guac_pass'
export POSTGRES_DATABASE='guacamole_db'

docker run --name postgres \
    -e POSTGRESQL_USER=${POSTGRES_USER} \
    -e POSTGRESQL_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRESQL_DATABASE=${POSTGRES_DATABASE} \
    -d -p 5432:5432 registry.redhat.io/rhscl/postgresql-96-rhel7

oc login -u <user> http://openshiftcluser
```