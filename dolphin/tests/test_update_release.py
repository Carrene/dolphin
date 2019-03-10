from bddrest import status, response, when, given, Update

from dolphin.models import Release, Member
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            manager=member1,
        )
        session.add(release1)

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
            manager=member1,
        )
        session.add(release2)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Updating a release',
            '/apiv1/releases/id:1',
            'UPDATE',
            json=dict(
                title='My interesting release',
                description='This is my new awesome release',
                cutoff='2300-2-2',
                status='in-progress',
                managerReferenceId=self.member2.reference_id,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting release'
            assert response.json['description'] == 'This is my new awesome release'
            assert response.json['cutoff'] == '2300-02-02T00:00:00'
            assert response.json['status'] == 'in-progress'
            assert response.json['managerId'] == self.member2.id

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                json=given | dict(title='Another title'),
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title length is more than limit',
                json=given | dict(title=((128 + 1) * 'a'))
            )
            assert status == '704 At Most 128 Characters Are Valid For Title'

            when(
                'Title is repetitive',
                json=given | dict(title='My second release')
            )
            assert status == '600 Another release with title: "My second '\
                'release" is already exists.'

            when(
                'Title format is wrong',
                json=given | dict(title=' Invalid Format ')
            )
            assert status == '747 Invalid Title Format'

            when(
                'Description length is less than limit',
                json=given | dict(
                    description=((8192 + 1) * 'a'),
                )
            )
            assert status == '703 At Most 8192 Characters Are Valid For '\
                'Description'

            when(
                'Cutoff format is wrong',
                json=given | dict(
                    cutoff='30-20-20',
                )
            )
            assert status == '702 Invalid Cutoff Format'

            when(
                'Invalid status in form',
                json=given | dict(
                    status='progressing',
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

            when('Trying to pass without form', json={})
            assert status == '708 No Parameter Exists In The Form'

            when('Request is not authorized', authorization=None)
            assert status == 401

        with oauth_mockup_server(), self.given(
            'Send HTTP request with empty form parameter',
            '/apiv1/releases/id:1',
            'UPDATE',
            json=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

