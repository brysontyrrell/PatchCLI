import os

import requests

from patchlib.exc import (
    PatchApiException,
    ApiBadRequest,
    ApiNotAuthorized,
    ApiForbidden,
    ApiNotFound
)


class PatchApiCore(object):
    def __init__(self, url, token=None):
        self.url = url
        self._token = token

        self._session = requests.Session()

    def _auth(self):
        return {'Authorization': 'Bearer {}'.format(self._token)} \
            if self._token \
            else {}

    def _request(self, uri, data=None, delete=False):
        if data and not delete:
            method = 'POST'
        elif delete and not data:
            method = 'DELETE'
        else:
            method = 'GET'

        headers = {}
        if data or delete:
            headers.update(self._auth())

        resp = self._session.request(
            method=method,
            url=os.path.join(self.url, uri),
            headers=headers,
            json=data
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            if resp.status_code == 401:
                raise ApiNotAuthorized
            elif resp.status_code == 403:
                raise ApiForbidden
            elif resp.status_code == 400:
                raise ApiBadRequest
            elif resp.status_code == 404:
                raise ApiNotFound
            else:
                raise PatchApiException

        return resp.json()
