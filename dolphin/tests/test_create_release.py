from bddrest import status, response, when, Remove, given

from dolphin.models import Release, Member, Project
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member)
        session.commit()

    def test_create(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            form=dict(
                title='My awesome release',
                description='Decription for my release',
                cutoff='2030-2-20'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome release'
            assert response.json['description'] == 'Decription for my release'
            assert response.json['cutoff'] == '2030-02-20T00:00:00'
            assert response.json['status'] is None

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                form=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Description length is less than limit',
                form=given | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 512 Characters Are Valid For '\
                'Description'

            when(
                'Cutoff format is wrong',
                form=given | dict(
                    cutoff='30-20-20',
                    title='Another title'
                )
            )
            assert status == '702 Invalid Cutoff Format'

            when(
                'Due date is not in form',
                form=given - 'cutoff' | dict(title='Another title')
            )
            assert status == '712 Cutoff Not In Form'

            when(
                'Invalid status in form',
                form=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

            when('Request is not authorized', authorization=None)
            assert status == 401

