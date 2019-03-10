from bddrest import status, response, when, Remove, given, Update

from dolphin.models import Member, Release
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)
        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            manager=cls.member,
        )
        session.add(release1)
        session.commit()

    def test_create(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            json=dict(
                title='My awesome release',
                description='Decription for my release',
                cutoff='2030-2-20',
                managerReferenceId=self.member.reference_id,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome release'
            assert response.json['description'] == 'Decription for my release'
            assert response.json['cutoff'] == '2030-02-20T00:00:00'
            assert response.json['status'] is None
            assert response.json['managerId'] == self.member.reference_id

            when(
                'Title is not in form',
                json=Remove('title')
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Title is repetetive',
                json=given | dict(title='My first release')
            )
            assert status == '600 Another release with title: My first '\
                'release is already exists.'

            when(
                'Description length is less than limit',
                json=given | dict(
                    description=((8192 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For '\
                'Description'

            when(
                'Cutoff format is wrong',
                json=given | dict(
                    cutoff='30-20-20',
                    title='Another title'
                )
            )
            assert status == '702 Invalid Cutoff Format'

            when(
                'Due date is not in form',
                json=given - 'cutoff' | dict(title='Another title')
            )
            assert status == '712 Cutoff Not In Form'

            when(
                'Invalid status in form',
                json=given | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == '705 Invalid status value, only one of '\
                '"in-progress, on-hold, delayed, complete" will be accepted'

            when(
                'Manager reference id is null',
                json=Update(title='New Release', managerReferenceId=None)
            )
            assert status == '778 Manager Reference Id Is Null'

            when(
                'Manager is not found',
                json=Update(title='New Release', managerReferenceId=0)
            )
            assert status == '608 Manager Not Found'

            when(
                'Maneger reference id is not in form',
                json=given - 'managerReferenceId' | dict(title='New Release')
            )
            assert status == '777 Manager Reference Id Not In Form'

            when('Trying to pass without form', json={})
            assert status == '708 No Parameter Exists In The Form'

            when(
                'Trying to pass with invalid field in form',
                json=Update(a=1),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, status, cutoff, ' \
                'managerReferenceId'

            when('Request is not authorized', authorization=None)
            assert status == 401

