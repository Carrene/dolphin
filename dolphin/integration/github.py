from nanohttp import settings, HTTPStatus
from requests import request
from restfulpy.orm import DBSession


class VCS:
    pass


class Github(VCS):

    def __init__(self):
        self.token = settings.github.application_token
        self.base_url = settings.github.base_url

    def get_member_token(self):
        members_token = DBSession.query(Github)

    @property
    def header(self):
        return {
            'Authorization': f'token {self.token}',
            'X-OAuth-Scopes': 'admin:repository_hook',
            'Accept': 'application/vnd.github.symmetra-preview+json'
        }

    def create_issue(self, repository, title, body):
        url = f'{settings.github.base_url}/repos/{repository}/issues'
        json = {
            'title':title,
            'body':body,
        }
        response = request(
            'POST',
            url,
            headers=self.header,
            json=json
        )
        if response.status_code not in [200, 201, 204]:
            print(f'ERROR: Got {response.status_code} when requesting {url}')
            raise HTTPStatus(response.status_code)

        return response

    def assign_issue(self, repository, issue_number, assignees):
        url = f'{self.url}/{repository}/issues/{issue_number}/assignees'
        json = {
            'assignees': assignees
        }
        response = request(
            'POST',
            url,
            headers=self.header,
            json=json
        )
        return response

    def list_repository(self, type_='all', sort='created', direction='asc'):
        url = f'{self.base_url}/orgs/{self.organization}/repos'
        json = {'type': type_, 'sort': sort, 'direction': direction}
        response = request(
            'GET',
            url,
            headers=self.header,
            json=json
        )
        return response

    def list_organizationmember(self, filter_='all', role='all'):
        url = f'{self.base_url}/orgs/{self.organization}/members'
        json = {'filter': filter_, 'role': role}
        response = request(
            'GET',
            url,
            headers=self.header,
            json=json
        )
        return response

