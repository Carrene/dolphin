from requests import request


class Github:
    github_base_url = 'https://api.github.com'
    def __init__(self, token):
        self.token = token

    def header(self):
        return {
            'Authorization': f'token {self.token}',
            'X-OAuth-Scopes': 'admin:repository_hook',
            'Accept': 'application/vnd.github.symmetra-preview+json'
        }

    def create_issue(self, owner, repository, title, body):
        url = f'{self.github_base_url}/repos/{owner}/{repository}/issues'
        json = {
            'title':title, 
            'body':body, 
        }
        response = request(
            'POST', 
            url, 
            headers=self.header(), 
            json=json
        )
        if response.status_code not in [200, 201, 204]:
            print(f'ERROR: Got {response.status_code} when requesting {url}')
            raise HttpError(response.status_code)

        return response

    def assign_issue(self, owner, repository, issue_number, assignees):
        url = f'{self.github_base_url}/repos/{owner}/{repository}/issues/ \
            {issue_number}/assignees'
        json = {
            'assignees': assignees
        }
        response = request(
            'POST',
            url,
            headers=self.header(),
            json=json
        )
        return response

    def list_repository(self, organization, type_='all', sort='created',
                        direction='asc'):
        url = f'{self.github_base_url}/orgs/{organization}/repos'
        json = {'type': type_, 'sort': sort, 'direction': direction}
        response = request(
            'GET',
            url,
            headers=self.header(),
            json=json
        )
        return response

    def list_organizationmember(self, organization, filter_='all', role='all'):
        url = f'{self.github_base_url}/orgs/{organization}/members'
        json = {'filter': filter_, 'role': role}
        response = request(
            'GET',
            url,
            headers=self.header(),
            json=json
        )
        return response

