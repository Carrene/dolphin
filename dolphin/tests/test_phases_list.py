from bddrest.authoring import status, response, when

from dolphin.models import Phase, Workflow, Member, Skill
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestListPhase(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member)

        skill = Skill(title='First Skill')
        cls.triage = Phase(title='triage', order=0, skill=skill)
        backlog = Phase(title='backlog', order=-1, skill=skill)

        default_workflow = Workflow(
            title='Default',
            phases=[cls.triage, backlog]
        )
        session.add(default_workflow)
        session.commit()

    def test_list_phases(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List phases of a workflow',
            '/apiv1/workflows/id:1/phases',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when(
                'Try to send a form in the request',
                form=dict(parameter='form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 2
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['order'] == -1

            when(
                'Sorting befor pagination',
                query=dict(sort='-id', take=1, skip=1)
            )
            assert len(response.json) == 1
            assert response.json[0]['order'] == 0

            when('Filtering the response', query=dict(id=self.triage.id))
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'triage'

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

    def test_list_phases_without_workflow(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'List all phases',
            '/apiv1/phases',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when(
                'Try to send a form in the request',
                form=dict(parameter='form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 2
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 2

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['order'] == -1

            when('Filtering the response', query=dict(id=self.triage.id))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.triage.title

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

