import json

import staccato.tests.integration.base as base


class TestApiNoSchedulerBasicFunctions(base.ApiTestBase):

    def _list_transfers(self, http_client):
        path = "/v1/transfers"
        response, content = http_client.request(path, 'GET')
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        return data

    def _cancel_transfer(self, http_client, id):
        data_json = {'xferaction': 'cancel'}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        path = "/v1/transfers/%s/action" % id
        return http_client.request(path, 'POST', headers=headers, body=data)

    def _delete_transfer(self, http_client, id):
        path = "/v1/transfers/%s" % id
        return http_client.request(path, 'DELETE')

    def _status_transfer(self, http_client, id):
        path = "/v1/transfers/%s" % id
        return http_client.request(path, 'GET')

    def _create_xfer(self, http_client, src='file:///etc/group',
                     dst='file:///dev/null'):
        path = "/v1/transfers"

        data_json = {'source_url': src,
                     'destination_url': dst}
        data = json.dumps(data_json)

        headers = {'content-type': 'application/json'}
        response, content = http_client.request(path, 'POST', body=data,
                                                headers=headers)
        return response, content

    def test_get_simple_empty_list(self):
        http_client = self.get_http_client()
        data = self._list_transfers(http_client)
        self.assertEqual([], data)

    def test_simple_create_transfer(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)

    def test_simple_create_transfer_list(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = self._list_transfers(http_client)
        self.assertEqual(len(data), 1)

    def test_simple_create_transfer_list_delete(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = self._list_transfers(http_client)
        self.assertEqual(len(data), 1)
        response, content = self._delete_transfer(http_client, data[0]['id'])
        self.assertEqual(response.status, 200)
        data = self._list_transfers(http_client)
        self.assertEqual(data, [])

    def test_simple_create_transfer_status(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        response, content = self._status_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        data_status = json.loads(content)
        self.assertEquals(data, data_status)

    def test_delete_unknown(self):
        http_client = self.get_http_client()
        response, content = self._delete_transfer(http_client, 'notreal')
        self.assertEqual(response.status, 404)

    def test_delete_twice(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        response, content = self._delete_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        response, content = self._delete_transfer(http_client, data['id'])
        self.assertEqual(response.status, 404)

    def test_status_unknown(self):
        http_client = self.get_http_client()
        response, content = self._delete_transfer(http_client, 'notreal')
        self.assertEqual(response.status, 404)

    def test_status_after_delete(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        response, content = self._delete_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        response, content = self._status_transfer(http_client, data['id'])
        self.assertEqual(response.status, 404)

    def test_create_state(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(data['state'], 'STATE_NEW')

    def test_create_cancel(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        response, content = self._cancel_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        response, content = self._status_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(data['state'], 'STATE_CANCELED')

    def test_create_cancel_delete(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        response, content = self._cancel_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        response, content = self._status_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)
        response, content = self._delete_transfer(http_client, data['id'])
        self.assertEqual(response.status, 200)

    def test_cancel_unknown(self):
        http_client = self.get_http_client()
        response, content = self._cancel_transfer(http_client, 'notreal')
        self.assertEqual(response.status, 404)

    def test_simple_create_bad_source(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client, src="bad_form")
        self.assertEqual(response.status, 400)

    def test_simple_create_bad_dest(self):
        http_client = self.get_http_client()
        response, content = self._create_xfer(http_client, dst="bad_form")
        self.assertEqual(response.status, 400)

    def test_bad_update(self):
        http_client = self.get_http_client()
        data_json = {'notaction': 'cancel'}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        path = "/v1/transfers/%s/action" % id
        response, content = http_client.request(path, 'POST', headers=headers,
                                                body=data)
        self.assertEqual(response.status, 400)

    def test_bad_action(self):
        http_client = self.get_http_client()
        data_json = {'xferaction': 'applesauce'}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        path = "/v1/transfers/%s/action" % id
        response, content =  http_client.request(path, 'POST', headers=headers, body=data)
        self.assertEqual(response.status, 400)

    def test_create_url_options(self):
        path = "/v1/transfers"
        http_client = self.get_http_client()

        data_json = {'source_url': 'file:///etc/group',
                     'destination_url': 'file:///dev/null',
                     'source_options': {'key': 10},
                     'destination_options': [1, 3, 5]}
        data = json.dumps(data_json)

        headers = {'content-type': 'application/json'}
        response, content = http_client.request(path, 'POST', body=data,
                                                headers=headers)
        self.assertEqual(response.status, 200)
        data_out = json.loads(content)
        self.assertEqual(data_json['source_options'],
                         data_out['source_options'])
        self.assertEqual(data_json['destination_options'],
                         data_out['destination_options'])

    def test_create_missing_url(self):
        path = "/v1/transfers"
        http_client = self.get_http_client()

        data_json = {'source_url': 'file:///etc/group'}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        response, content = http_client.request(path, 'POST', body=data,
                                                headers=headers)
        self.assertEqual(response.status, 400)

    def test_create_uknown_option(self):
        path = "/v1/transfers"
        http_client = self.get_http_client()

        data_json = {'source_url': 'file:///etc/group',
                     'destination_url': 'file:///dev/zero',
                     'random': 90}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        response, content = http_client.request(path, 'POST', body=data,
                                                headers=headers)
        self.assertEqual(response.status, 400)

    def test_list_limit(self):
        http_client = self.get_http_client()
        for i in range(10):
            response, content = self._create_xfer(http_client)
            self.assertEqual(response.status, 200)

        path = "/v1/transfers"
        data_json = {'limit': 5}
        data = json.dumps(data_json)
        headers = {'content-type': 'application/json'}
        response, content = http_client.request(path, 'GET', body=data,
                                                headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(len(data), 5)