from bddrest import status, response, when, given
from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestEventType(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'Type1'
        description = 'A description for a type1'

        with oauth_mockup_server(), self.given(
            'Creating an event type',
            '/apiv1/eventtypes',
            'CREATE',
            json=dict(
                title=title,
                description=description,
            ),
        ):
            assert status == 200
            assert response.json['title'] == title
            assert response.json['description'] == description
            assert response.json['id'] is not None

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Trying to pass without title',
                json=dict(a='a'),
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Trying to pass with none title',
                json=dict(title=None)
            )
            assert status == '727 Title Is None'

            when(
                'Description length is less than limit',
                json=given | dict(description=(512 + 1) * 'a'),
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

