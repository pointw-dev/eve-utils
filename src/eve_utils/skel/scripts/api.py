import json
from requestshelper import requests, RequestsWithDefaults
import socket
import re
import sys

class Api:
    def __init__(self, base_api_url, auth='Basic cm9vdDpwYXNzd29yZA=='):  # root:password
        self.base_api_url = base_api_url
        self._api = RequestsWithDefaults(url_base=self.base_api_url, headers={
            'Content-type': 'application/json',
            'Cache-Control': 'no-cache',
            'Authorization': auth
        })

    def post(self, url, data):
        if type(data) is not str:
            data = json.dumps(data)
        response = self._api.post(url, data=data)
        try:
            response.raise_for_status()
            return response.json()
        except:
            if response.status_code == 422:
                issue = response.json().get('_issues', {}).get('name', '')
                if 'is not unique' in issue:
                    new_data = json.loads(data)
                    new_data['name'] += ' ~'
                    return self.post(url, new_data)
            message = f'{response.status_code} {response.reason}'            
            details = response.text
            raise RuntimeError(f'POST {url} - {message}\n{details}\n\n{data}')

    def post_rel(self, resource, rel, data):
        url = resource['_links'][rel]['href']        
        return self.post(url, data)

    def patch(self, resource, data):
        if type(data) is not str:
            data = json.dumps(data)
        url = resource['_links']['self']['href']
        headers = {
            'If-Match': resource['_etag']
        }
        response = self._api.patch(url, data=data, headers=headers)

        try:
            response.raise_for_status()
            return response.json()
        except:
            message = f'{response.status_code} {response.reason}'
            details = response.text
            raise RuntimeError(f'PATCH {url}\n{headers}\n{message}\n{details}\n\n{data}')


    def put(self, resource, data, rel='self'):
        if type(data) is not str:
            data = json.dumps(data)
        url = resource['_links'][rel]['href']
        headers = {
            'If-Match': resource['_etag']
        }
        response = self._api.put(url, data=data, headers=headers)

        try:
            response.raise_for_status()
            return response.json()
        except:
            message = f'{response.status_code} {response.reason}'
            details = response.text
            raise RuntimeError(f'PUT {url}\n{headers}\n{message}\n{details}\n\n{data}')


    def get(self, url):
        response = self._api.get(url)
        if response.status_code == 404:
            return None
        try:
            response.raise_for_status()
            return response.json()
        except:
            message = f'GET {url} - {response.status_code} {response.reason}'
            details = response.text
            raise RuntimeError(f'{message}\n{details}')


    def get_rel(self, resource, rel='self'):
        url = resource['_links'][rel]['href']
        return self.get(url)


    def delete_collection(self, url):
        response = self._api.delete(url)

        try:
            response.raise_for_status()
        except:
            message = f'{response.status_code} {response.reason}'
            details = response.text
            raise RuntimeError(f'DELETE {url}\n{headers}\n{message}\n{details}')


    def delete_resource(self, resource):
        url = resource['_links']['self']['href']
        headers = {
            'If-Match': resource['_etag']
        }
        response = self._api.delete(url, headers=headers)

        try:
            response.raise_for_status()
        except:
            message = f'{response.status_code} {response.reason}'
            details = response.text
            raise RuntimeError(f'DELETE {url}\n{headers}\n{message}\n{details}')
