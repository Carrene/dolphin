from bddrest.authoring import status, response, when, given

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member


class TestMember(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123987465,
            reference_id=3
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token',
            phone=1287465,
            reference_id=4
        )
        session.add(cls.member2)

        member3 = Member(
            title='Third Member',
            email='member3@example.com',
            access_token='access token',
            phone=1287456,
            reference_id=5
        )
        session.add(member3)
        session.commit()

    def test_search(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Search for a member by submitting form',
            '/apiv1/members',
            'SEARCH',
            form=dict(query='Sec'),
        ):
            assert status == 200
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.member2.title

            when('Search without query parameter', form=given - 'query')
            assert status == '912 Query Parameter Not In Form Or Query String'

            when(
                'Search string must be less than 20 charecters',
                form=given | dict(query=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Valid For Title'

            when(
                'Try to sort the response',
                query=dict(sort='id'),
                form=given | dict(query='member')
            )
            assert len(response.json) == 3
            assert response.json[0]['id'] < response.json[1]['id']

            when(
                'Trying ro sort the response in descend ordering',
                query=dict(sort='-id'),
                form=given | dict(query='member')
            )
            assert len(response.json) == 3
            assert response.json[0]['id'] > response.json[1]['id']

            when(
                'Filtering the response',
                query=dict(title=self.member2.title)
            )
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.member2.title

            when(
                'Trying to filter the response ignoring the title',
                query=dict(title=f'!{self.member2.title}'),
                form=given | dict(query='member')
            )
            assert len(response.json) == 2

            when(
                'Testing pagination',
                query=dict(take=1, skip=1),
                form=given | dict(query='member')
            )
            assert len(response.json) == 1

            when(
                'Sort before pagination',
                query=dict(sort='-id', take=2, skip=1),
                form=given | dict(query='member')
            )
            assert len(response.json) == 2
            assert response.json[0]['id'] > response.json[1]['id']

    def test_request_with_query_string(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Test request using query string',
            '/apiv1/members',
            'SEARCH',
            query=dict(query='Sec')
        ):
            assert status == 200
            assert len(response.json) == 1

            when('An unauthorized search', authorization=None)
            assert status == 401

