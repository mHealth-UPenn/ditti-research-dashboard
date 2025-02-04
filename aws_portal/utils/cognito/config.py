class CognitoPoolConfig:
    def __init__(self, client_id: str, client_secret: str, domain: str, region: str,
                 user_pool_id: str, redirect_uri: str, logout_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.domain = domain
        self.region = region
        self.user_pool_id = user_pool_id
        self.redirect_uri = redirect_uri
        self.logout_uri = logout_uri
        self.issuer = f"https://cognito-idp.{
            self.region}.amazonaws.com/{self.user_pool_id}"
