import jwt

from patchlib.api.shared import PatchApiCore


class CommunityPatch(PatchApiCore):
    def __init__(self, token, beta=False):
        url = 'https://www.communitypatch.com' \
            if not beta \
            else 'https://beta2.communitypatch.com'

        decoded_token = jwt.decode(token, verify=False)
        self.contributor_id = decoded_token.get('sub')

        super(CommunityPatch, self).__init__(url=url, token=token)

    def list_contributors(self):
        return self._request('api/v1/contributors')

    def list_titles(self, contributor_id=None):
        contributor_id = contributor_id or self.contributor_id
        return self._request('jamf/v1/{}/software'.format(contributor_id))

    def get_title(self, title_id, contributor_id=None):
        contributor_id = contributor_id or self.contributor_id
        return self._request(
            'jamf/v1/{}/patch/{}'.format(contributor_id, title_id))

    def create_title(self, definition):
        return self._request('api/v1/titles', data=definition)

    def update_version(self, title_id, version):
        return self._request(
            'api/v1/titles/{}/version'.format(title_id), data=version)

    def delete_title(self, title_id):
        return self._request('api/v1/titles/{}'.format(title_id), delete=True)