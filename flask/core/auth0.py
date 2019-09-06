from auth0.v3.authentication import GetToken
from config import auth0_config

DOMAIN = auth0_config['auth0_domain']
AUDIENCE = f"https://{DOMAIN}/api/v2/"
CLIENT_ID = auth0_config["client_id"]
CLIENT_SECRET = auth0_config["client_secret"]

domain = 'myaccount.auth0.com'
non_interactive_client_id = 'exampleid'
non_interactive_client_secret = 'examplesecret'

get_token = GetToken(domain)
token = get_token.client_credentials(non_interactive_client_id,
    non_interactive_client_secret, 'https://{}/api/v2/'.format(domain))
mgmt_api_token = token['access_token']

from auth0.v3.management import Auth0

domain = 'myaccount.auth0.com'
mgmt_api_token = 'MGMT_API_TOKEN'

auth0 = Auth0(domain, mgmt_api_token)


class Auth0Management:

    def __init__(self):

        print("new")


mgmt = Auth0Management()
