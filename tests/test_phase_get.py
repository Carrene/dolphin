from bddrest import status, response, when, given

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Specialty, Phase, Workflow, Skill


class TestPhase(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member)

        skill = Skill(title='First Skill')
        specialty1 = Specialty(
            title='First Specialty',
            skill=skill,
        )

        cls.workflow = Workflow(
            title='workflow',
        )

        cls.phase = Phase(
             title='phase 1',
             order=1,
             specialty=specialty1,
             workflow=cls.workflow,
        )
        session.add(cls.phase)
        session.commit()

    def test_get(self):
        self.login(self.member.email)
        with oauth_mockup_server(), self.given(
            f'Getting a phase',
            f'/apiv1/phases/phase_id: {self.phase.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.phase.id

            when(
                'Phase Not Found',
                url_parameters=given | dict(phase_id=0)
            )
            assert status == 404

            when(
                'Phase Not Found',
                url_parameters=given | dict(phase_id='not-integer')
            )
            assert status == 404

            when(
                'Form Parameter',
                form=dict(a='a')
            )
            assert status == '709 Form Not Allowed'

            when(
                'Request is not authorized',
                authorization=None,
            )
            assert status == 401

