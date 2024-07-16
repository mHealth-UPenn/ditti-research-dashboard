import json


def test_touch(client):
    res = client.get('/touch')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'OK'
