from datetime import datetime

from bddrest import when, response, status
from auditor.context import Context as AuditLogContext

from ..models import Workflow, Phase, Resource, Skill, Group, Release,  \
    Project, Issue, Item
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestResource(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        workflow = Workflow(title='Default')
        skill1 = Skill(title='First Skill')

        skill2 = Skill(title='Second Skill')

        cls.phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow,
            skill=skill1
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='Design',
            order=1,
            workflow=workflow,
            skill=skill2
        )
        session.add(cls.phase2)

        cls.phase3 = Phase(
            title='Development',
            order=2,
            workflow=workflow,
            skill=skill1,
        )
        session.add(cls.phase3)

        cls.phase4 = Phase(
            title='Test',
            order=3,
            workflow=workflow,
            skill=skill2,
        )
        session.add(cls.phase4)

        cls.resource1 = Resource(
            title='First Resource',
            email='resource1@example.com',
            access_token='access token 1',
            phone=222222222,
            reference_id=2,
            skills=[skill1],
        )
        session.add(cls.resource1)

        cls.resource2 = Resource(
            title='Second Resource',
            email='resource2@example.com',
            access_token='access token 2',
            phone=333333333,
            reference_id=3,
            skills=[skill1],
        )
        session.add(cls.resource2)

        cls.resource3 = Resource(
            title='Third Resource',
            email='resource3@example.com',
            access_token='access token 3',
            phone=444444444,
            reference_id=4,
            skill=skill2
        )
        session.add(cls.resource3)

        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.resource1,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.resource2,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        cls.issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(cls.issue1)

        cls.issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            kind='feature',
            days=1,
            room_id=3
        )
        session.add(cls.issue2)

        cls.issue3 = Issue(
            project=project,
            title='Third issue',
            description='This is description of third issue',
            kind='feature',
            days=1,
            room_id=4
        )
        session.add(cls.issue3)

        cls.issue4 = Issue(
            project=project,
            title='Fourth issue',
            description='This is description of fourth issue',
            kind='feature',
            days=1,
            room_id=5
        )
        session.add(cls.issue3)
        session.flush()

        cls.item1 = Item(
            issue_id=cls.issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.resource1.id,
        )
        session.add(cls.item1)

#        cls.item2 = Item(
#            issue_id=cls.issue2.id,
#            phase_id=cls.phase2.id,
#            member_id=cls.resource2.id,
#            start_date=datetime.strptime('2020-2-2', '%Y-%m-%d'),
#            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
#            estimated_hours=3,
#        )
#        session.add(cls.item2)

#        cls.item3 = Item(
#            issue_id=cls.issue3.id,
#            phase_id=cls.phase2.id,
#            member_id=cls.resource1.id,
#            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
#            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
#            estimated_hours=3,
#        )
#        session.add(cls.item3)
#
#        cls.item4 = Item(
#            issue_id=cls.issue4.id,
#            phase_id=cls.phase4.id,
#            member_id=cls.resource2.id,
#            start_date=datetime.strptime('2018-2-2', '%Y-%m-%d'),
#            end_date=datetime.strptime('2020-2-3', '%Y-%m-%d'),
#            estimated_hours=3,
#        )
#        session.add(cls.item4)
#
#        cls.item5 = Item(
#            issue_id=cls.issue4.id,
#            phase_id=cls.phase2.id,
#            member_id=cls.resource1.id,
#            status='done',
#        )
#        session.add(cls.item5)
        session.commit()

    def test_list(self):
        self.login(self.resource1.email)

        with oauth_mockup_server(), self.given(
           f'Getting list of resources',
           f'/apiv1/issues/issue_id: {self.issue1.id}/' \
           f'phases/id:{self.phase1.id}/resources',
           f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Trying to pass with wrong id', url_parameters=dict(id=0))
            assert status == 404

            when('Type of id is invalid', url_parameters=dict(id='not-integer'))
            assert status == 404

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] == 1
            assert response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2
            assert response.json[1]['id'] == 1

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            self.logout()
            when(
                'Trying with an unauthorized member',
                authorization=self._authentication_token
            )
            assert status == 401

