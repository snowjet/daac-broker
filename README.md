# daac-broker



# Required Variables

```bash
export POSTGRES_HOST='127.0.0.1'
export POSTGRES_USER='guac'
export POSTGRES_PASSWORD='guac_pass'
export POSTGRES_DATABASE='guacamole_db'
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

oc new-app --name guac-api -e POSTGRES_HOST='127.0.0.1' -e POSTGRES_USER='guac' -e POSTGRES_PASSWORD='guac_pass' -e POSTGRES_DATABASE='guacamole_db' https://github.com/snowjet/daac-broker.git