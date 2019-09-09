from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0 as auth0v3
from auth0.v3.exceptions import Auth0Error

from core.config import auth0_config
from core.log import logger


class Auth0Management:

    def __init__(self):

        self._request_token()

    def _request_token(self):

        domain = auth0_config["auth0_domain"]
        non_interactive_client_id = auth0_config["client_id"]
        non_interactive_client_secret = auth0_config["client_secret"]

        get_token = GetToken(domain)
        token = get_token.client_credentials(
            non_interactive_client_id,
            non_interactive_client_secret,
            "https://{}/api/v2/".format(domain),
        )

        mgmt_api_token = token["access_token"]

        self.auth0 = auth0v3(domain, mgmt_api_token)
        self.admin_role = self.auth0.roles.list(name_filter=auth0_config["admin_role"])['roles'][0]['id']

    def is_admin(self, name):

        try:

            users = self.auth0.roles.list_users(id=self.admin_role)

            for user in users['users']:
                if str(user['name']).lower() == str(name).lower():
                    return True

            return False

        except Auth0Error as error_msg:
            logger.error("Auth0 Error", error=error_msg)
