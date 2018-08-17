def test_check_sanity(client):
    resp = client.get('/sanity')
    assert resp.status_code == 200
    assert 'Sanity check passed.' == resp.data.decode()

def test_api_root(client):
    resp = client.get('/', content_type='application/json')
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert 'keys_url' in resp_data
    assert len(resp_data) == 1
    assert resp_data['keys_url'][-5:] == '/keys'
