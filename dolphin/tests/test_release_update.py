from auditor import MiddleWare
from auditor.logentry import ChangeAttributeLogEntry
from auditor.context import Context as AuditLogContext
from auditor.logentry import RequestLogEntry, InstantiationLogEntry
from bddrest import status, response, when, given, Update
from nanohttp.contexts import Context
from nanohttp import context

from dolphin import Dolphin
from dolphin.models import Release, Member, Group
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


def callback(audit_logs):
    global logs
    logs = audit_logs


class TestRelease(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member1)

        group1 = Group(title='group1')
        cls.group2 = Group(title='group2')
        session.add(cls.group2)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=123456788,
            reference_id=2
        )
        session.add(cls.member2)

        cls.release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group1,
        )
        session.add(cls.release1)

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
            group=group1,
        )
        session.add(release2)
        session.commit()

    def test_update(self):
        self.login('member1@example.com')

        class Identity:
            def __init__(self, member):
                self.id = member.id
                self.reference_id = member.reference_id

        with Context({}):
            context.identity = Identity(self.member1)
            old_values = self.release1.to_dict()

        form = dict(
            title='My interesting release',
            description='This is my new awesome release',
            cutoff='2030-2-21',
            launchDate='2030-2-21',
            status='in-progress',
            managerReferenceId=self.member2.reference_id,
        )

        with oauth_mockup_server(), self.given(
            'Updating a release',
            f'/apiv1/releases/id: {self.release1.id}',
            'UPDATE',
            json=form,
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting release'
            assert response.json['description'] == 'This is my new awesome release'
            assert response.json['cutoff'] == '2030-02-21T00:00:00'
            assert response.json['launchDate'] == '2030-02-21T00:00:00'
            assert response.json['status'] == 'in-progress'
            assert response.json['managerId'] == self.member2.id
            assert response.json['groupId'] == self.group2.id

            assert len(logs) == 8

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
                'Launch date format is wrong',
                json=Update(launchDate='30-20-20')
            )
            assert status == '784 Invalid Launch Date Format'

            when(
                'The cutoff date greater than launch date',
                json=Update(cutoff='2030-2-25')
            )
            assert status == '651 The Launch Date Must Greater Than Cutoff Date'

            when(
                'The launch date less than cutoff date',
                json=Update(launchDate='2030-2-15')
            )
            assert status == '651 The Launch Date Must Greater Than Cutoff Date'

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

            when(
                'Group id is null',
                json=given | dict(title='New Release', groupId=None)
            )
            assert status == '796 Group Id Is Null'

            when(
                'Group is not found',
                json=Update(title='New Release', groupId=0)
            )
            assert status == '659 Group Not Found'

            when('Request is not authorized', authorization=None)
            assert status == 401

        with oauth_mockup_server(), self.given(
            'Send HTTP request with empty form parameter',
            '/apiv1/releases/id:1',
            'UPDATE',
            json=dict()
        ):
            assert status == '708 No Parameter Exists In The Form'

