from bddrest.authoring import status, response, when

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Phase, Workflow, Member, Specialty, Skill


class TestListWorkflow(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member)

        workflow1 = Workflow(title='first workflow')
        session.add(workflow1)

        workflow2 = Workflow(title='second workflow')
        session.add(workflow2)

        workflow3 = Workflow(title='third workflow')
        session.add(workflow3)

        skill = Skill(title='First Skill')
        specialty = Specialty(
            title='First Specialty',
            skill=skill,
        )
        session.add(specialty)

        phase1 = Phase(
            title='phase 1',
            order=1,
            specialty=specialty,
            workflow=workflow1,
        )
        session.add(phase1)

        phase2 = Phase(
            title='phase 2',
            order=2,
            specialty=specialty,
            workflow=workflow2,
        )
        session.add(phase2)

        phase3 = Phase(
            title='phase 3',
            order=1,
            specialty=specialty,
            workflow=workflow3,
        )
        session.add(phase3)
        session.commit()

    def test_list_phases(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'List workflows',
            '/apiv1/workflows',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3
            assert response.json[0]['title'] == 'first workflow'

            for workflow in response.json:
                assert workflow['phases'] is not None

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'third workflow'

            with self.given(
                'Filter workflows',
                '/apiv1/workflows',
                'LIST',
                query=dict(sort='id', title='first workflow')
            ):
                assert response.json[0]['title'] == 'first workflow'

                when(
                    'List workflows except one of them',
                    query=dict(sort='id', title='!first workflow')
                )
                assert response.json[0]['title'] == 'second workflow'

            with self.given(
                'Workflow pagination',
                '/apiv1/workflows',
                'LIST',
                query=dict(sort='id', take=1, skip=2)
            ):
                assert response.json[0]['title'] == 'third workflow'

                when(
                    'Manipulate sorting and pagination',
                    query=dict(sort='-title', take=1, skip=2)
                )
                assert response.json[0]['title'] == 'first workflow'

                when('Request is not authorized', authorization=None)
                assert status == 401

