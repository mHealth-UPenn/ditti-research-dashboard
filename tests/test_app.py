# from tests.testing_utils import login_test_account


# def test_refresh_expiring_jwts(timeout_client):
#     res = login_test_account("foo", timeout_client)
#     old_token = res.json["jwt"]
#     headers = {"Authorization": "Bearer " + old_token}
#     res = timeout_client.get("/test/get", headers=headers)
#     new_token = res.json["jwt"]
#     assert old_token != new_token
