# daac-broker



# Required Variables

```bash
export POSTGRES_USER='guac'
export POSTGRES_PASSWORD='guac_pass'
export POSTGRES_DATABASE='guacamole_db'
```

### Service Account

* need to reduce the access level for this service account.

```bash
oc create serviceaccount guacrobot

oc policy add-role-to-user admin -z guacrobot

oc describe serviceaccount guacrobot
Name:                guacrobot
Namespace:           guac
Labels:              <none>
Annotations:         <none>
Image pull secrets:  guacrobot-dockercfg-btz4l
Mountable secrets:   guacrobot-token-c7hhc
                     guacrobot-dockercfg-btz4l
Tokens:              guacrobot-token-c7hhc
                     guacrobot-token-k44m7
Events:              <none>

oc describe secret guacrobot-token-c7hhc
Name:         guacrobot-token-c7hhc
Namespace:    guac
Labels:       <none>
Annotations:  kubernetes.io/service-account.name=guacrobot
              kubernetes.io/service-account.uid=df6e6192-a46b-11e9-addf-025f6b8bf8ee

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:          2719 bytes
namespace:       4 bytes
service-ca.crt:  3835 bytes
token:           <------token------->


oc get rolebindings
NAME                    ROLE                    USERS                                   GROUPS                        SERVICE ACCOUNTS   SUBJECTS
admin                   /admin                  snowjet
admin-0                 /admin                                                                                        guacrobot
system:deployers        /system:deployer                                                                              deployer
system:image-builders   /system:image-builder                                                                         builder
system:image-pullers    /system:image-puller                                            system:serviceaccounts:guac

```