from bddrest import when, response, status

from ..models import Item, Member, Issue, Workflow, Project, Phase
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestResource(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=222222222,
            reference_id=2
        )
        session.add(cls.member1)

        member2 = Member(
            title='Second Member',
            email='member2@example.com',
            access_token='access token 2',
            phone=333333333,
            reference_id=3
        )
        session.add(member2)

        workflow = Workflow(title='default')

        cls.phase1 = Phase(
            title='backlog',
            order=-1,
            workflow=workflow
        )
        session.add(cls.phase1)

        project = Project(
            workflow=workflow,
            member=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)
        session.flush()

        item1=Item(
            issue_id=issue1.id,
            phase_id=cls.phase1.id,
            member_id=cls.member1.id,
        )
        session.add(item1)

        item2=Item(
            issue_id=issue1.id,
            phase_id=cls.phase1.id,
            member_id=member2.id,
        )
        session.add(item2)
        session.commit()

    def test_list(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
           f'Getting list of resources',
           f'/apiv1/phases/id: {self.phase1.id}/resources',
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
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert response.json[0]['id'] == 1
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

