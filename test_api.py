def test_check_sanity(client):
    resp = client.get('/sanity')
    assert resp.status_code == 200
    assert 'Sanity check passed.' == resp.data.decode()


# 'list collections' tests
def test_get_api_root(client):
    resp = client.get('/', content_type='application/json')
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert 'keys_url' in resp_data
    assert len(resp_data) == 1
    assert resp_data['keys_url'][-5:] == '/keys'


def test_delete_api_root_not_allowed(client):
    resp = client.delete('/', content_type='application/json')
    assert resp.status_code == 405


# 'list keys' tests
def test_get_empty_keys_list(client):
    resp = client.get('/keys', content_type='application/json')
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert len(resp_data) == 0


def test_get_nonempty_keys_list(client, keys, add_to_keys):
    add_to_keys({'key': 'babboon', 'value': 'Larry'})
    add_to_keys({'key': 'bees', 'value': ['Ann', 'Joe', 'Dee']})

    resp = client.get('/keys', content_type='application/json')
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert isinstance(resp_data, list)
    assert len(resp_data) == 2
    for doc_idx in (0, 1):
        for k in ('key', 'http_url'):
            assert k in resp_data[doc_idx]
        if resp_data[doc_idx]['key'] == 'babboon':
            assert resp_data[doc_idx]['http_url'][-13:] == '/keys/babboon'
        else:
            assert resp_data[doc_idx]['http_url'][-10:] == '/keys/bees'


def test_delete_on_keys_not_allowed(client):
    resp = client.delete('/keys', content_type='application/json')
    assert resp.status_code == 405


# 'get a key' tests
def test_get_existing_key(client, keys, add_to_keys):
    add_to_keys({'key': 'babboon', 'value': 'Larry'})
    add_to_keys({'key': 'bees', 'value': ['Ann', 'Joe', 'Dee']})

    resp = client.get('/keys/bees', content_type='application/json')
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert isinstance(resp_data, dict)
    for k in ('key', 'http_url', 'value'):
        assert k in resp_data
    assert resp_data['key'] == 'bees'
    assert resp_data['http_url'][-10:] == '/keys/bees'
    assert resp_data['value'] == ['Ann', 'Joe', 'Dee']


def test_get_nonexisting_key(client, keys):
    resp = client.get('/keys/bees', content_type='application/json')
    assert resp.status_code == 404


def test_post_on_a_key_not_allowed(client):
    resp = client.post('/keys/bees', content_type='application/json')
    assert resp.status_code == 405


# 'create a key' tests
def test_create_new_key(client, keys):
    new_doc = {'key': 'oscillator', 'value': 'Colpitts'}
    resp = client.post(
        '/keys',
        json=new_doc,
        content_type='application/json'
    )
    assert resp.status_code == 201
    resp_data = resp.get_json()
    assert isinstance(resp_data, dict)
    for k in ('key', 'http_url', 'value'):
        assert k in resp_data
    assert resp_data['key'] == new_doc['key']
    assert resp_data['value'] == new_doc['value']
    assert resp_data['http_url'][-16:] == '/keys/oscillator'


def test_create_duplicate_key(client, keys, add_to_keys):
    new_doc = {'key': 'oscillator', 'value': 'Colpitts'}
    add_to_keys(new_doc.copy())
    resp = client.post(
        '/keys',
        json=new_doc,
        content_type='application/json'
    )
    assert resp.status_code == 400
    resp_data = resp.get_json()
    assert 'error' in resp_data
    assert resp_data['error'] == "Can't create duplicate key (oscillator)."


def test_create_new_key_missing_key(client, keys):
    new_doc = {'value': 'Colpitts'}
    resp = client.post(
        '/keys',
        json=new_doc,
        content_type='application/json'
    )
    assert resp.status_code == 400
    resp_data = resp.get_json()
    assert 'error' in resp_data
    assert resp_data['error'] == 'Please provide the missing "key" parameter!'


def test_create_new_key_missing_value(client, keys):
    new_doc = {'key': 'oscillator'}
    resp = client.post(
        '/keys',
        json=new_doc,
        content_type='application/json'
    )
    assert resp.status_code == 400
    resp_data = resp.get_json()
    assert 'error' in resp_data
    assert resp_data['error'] == 'Please provide the missing "value" ' \
                                 'parameter!'


# 'update a key' tests
def test_update_a_key_existing(client, keys, add_to_keys):
    add_to_keys({'key': 'oscillator', 'value': 'Colpitts'})
    update_value = {'value': ['Pierce', 'Hartley']}
    resp = client.put(
        '/keys/oscillator',
        json=update_value,
        content_type='application/json'
    )
    assert resp.status_code == 204


def test_update_a_key_nonexisting(client, keys, add_to_keys):
    add_to_keys({'key': 'oscillator', 'value': 'Colpitts'})
    update_value = {'value': ['Pierce', 'Hartley']}
    resp = client.put(
        '/keys/gadget',
        json=update_value,
        content_type='application/json'
    )
    assert resp.status_code == 400
    resp_data = resp.get_json()
    assert 'error' in resp_data
    assert resp_data['error'] == 'Update failed.'


# 'delete a key' tests
def test_delete_a_key_existing(client, keys, add_to_keys):
    add_to_keys({'key': 'oscillator', 'value': 'Colpitts'})
    resp = client.delete(
        '/keys/oscillator',
        content_type='application/json'
    )
    assert resp.status_code == 204


def test_delete_a_key_nonexisting(client, keys):
    resp = client.delete(
        '/keys/oscillator',
        content_type='application/json'
    )
    assert resp.status_code == 404
