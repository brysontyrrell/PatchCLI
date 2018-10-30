from patchlib.api.shared import PatchApiCore


class PatchServer(PatchApiCore):
    def list_titles(self):
        return self._request('jamf/v1/software')

    def get_title(self, title_id):
        return self._request('jamf/v1/patch/{}'.format(title_id))

    def create_title(self, definition):
        return self._request('api/v1/title', data=definition)

    def update_version(self, title_id, version):
        return self._request(
            'api/v1/title/{}/version'.format(title_id), data=version)

    def delete_title(self, title_id):
        return self._request('api/v1/title/{}'.format(title_id), delete=True)
