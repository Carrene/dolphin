from auditor import MiddleWare
from auditor.context import Context as AuditLogContext
from auditor.logentry import RequestLogEntry, InstantiationLogEntry
from bddrest import status, response, when, Remove, given, Update

from dolphin import Dolphin
from dolphin.models import Member, Release, Group
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


def callback(audit_logs):
    global logs
    logs = audit_logs


class TestRelease(LocalApplicationTestCase):
    __application__ = MiddleWare(Dolphin(), callback)

    @classmethod
    @AuditLogContext(dict())
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

        cls.group = Group(title='default')

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=cls.group,
        )
        session.add(release1)
        session.commit()

    def test_create(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            json=dict(
                title='My awesome release',
                description='Decription for my release',
                cutoff='2030-2-20',
                launchDate='2030-2-20',
                managerId=self.member.id,
                groupId=self.group.id,
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome release'
            assert response.json['description'] == 'Decription for my release'
            assert response.json['cutoff'] == '2030-02-20T00:00:00'
            assert response.json['launchDate'] == '2030-02-20T00:00:00'
            assert response.json['status'] is None
            assert response.json['managerId'] == self.member.id
            assert response.json['roomId'] is not None
            assert len(response.json['projects']) == 0

            assert len(logs) == 2
            assert isinstance(logs[0], InstantiationLogEntry)
            assert isinstance(logs[1], RequestLogEntry)
            assert response.json['groupId'] == self.group.id

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
            assert status == '600 Repetitive Title'

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
                'Launch date format is wrong',
                json=Update(
                    launchDate='30-20-20',
                    title='Another title'
                )
            )
            assert status == '784 Invalid Launch Date Format'

            when(
                'Launch Date is not in form',
                json=given - 'launchDate' | dict(title='Another title')
            )
            assert status == '783 Launch Date Not In Form'

            when(
                'The cutoff date greater than launch date',
                json=Update(
                    title='Another title',
                    cutoff='2030-2-25',
                )
            )
            assert status == '651 The Launch Date Must Greater Than Cutoff Date'

            when(
                'The launch date less than cutoff date',
                json=Update(
                    title='Another title',
                    launchDate='2030-2-15',
                )
            )
            assert status == '651 The Launch Date Must Greater Than Cutoff Date'

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
                'Manager id is null',
                json=Update(title='New Release', managerId=None)
            )
            assert status == '778 Manager Id Is Null'

            when(
                'Manager is not found',
                json=Update(title='New Release', managerId=0)
            )
            assert status == '608 Manager Not Found'

            when(
                'Maneger id is not in form',
                json=given - 'managerId' | dict(title='New Release')
            )
            assert status == '777 Manager Id Not In Form'

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

            when(
                'Group id is not in form',
                json=given - 'groupId' | dict(title='New Release')
            )
            assert status == '795 Group Id Not In Form'

            when('Trying to pass without form', json={})
            assert status == '708 No Parameter Exists In The Form'

            when(
                'Trying to pass with invalid field in form',
                json=Update(a=1),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, status, cutoff, ' \
                'managerId, launchDate, groupId'

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    json=given | dict(title='Another title')
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    json=given | dict(title='Another title')
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    json=given | dict(title='Another title')
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('615 Room Already Exists'):
                when(
                    'Intended room is already exists',
                    json=given | dict(title='Another title')
                )
                assert status == 200

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Intended member is already added to room',
                    json=given | dict(title='Awesome release')
                )
                assert status == 200

            when('Request is not authorized', authorization=None)
            assert status == 401

