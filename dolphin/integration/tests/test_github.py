from dolphin.integration.github import Github


accesstoken = '5391b0c60b7d2d1bfb0f73d18f82313c9fce9995'

def test_github():
    git = Github(accesstoken)
    response = git.create_issue(
        'smarthomeofus',
        'send-message',
        'First issue',
        'Body of issue'
    )
    assert response.status_code in [200, 201, 204]

def test_assign_issue():
    git = Github(accesstoken)
    response = git.assign_issue(
        'smarthomeofus',
        'send-message',
        '1',
        ['farzaneka']
    )
    assert response.status_code in [200, 201, 204]

def test_list_repository():
    git = Github(accesstoken)
    response = git.list_repository(
        'smarthomeofus'
    )
    assert response.status_code in [200, 201, 204]

def test_list_orgamization_member():
    git = Github(accesstoken)
    response = git.list_organizationmember(
        'smarthomeofus'
    )
    assert response.status_code in [200, 201, 204]

