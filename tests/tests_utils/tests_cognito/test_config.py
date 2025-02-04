from aws_portal.utils.cognito.config import CognitoPoolConfig


def test_cognito_config_initialization():
    config = CognitoPoolConfig(
        client_id="test_client",
        client_secret="test_secret",
        domain="test.auth.us-east-1.amazoncognito.com",
        region="us-east-1",
        user_pool_id="us-east-1_test",
        redirect_uri="http://localhost/callback",
        logout_uri="http://localhost/logout"
    )

    assert config.issuer == "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_test"
    assert config.client_id == "test_client"
    assert config.domain == "test.auth.us-east-1.amazoncognito.com"
