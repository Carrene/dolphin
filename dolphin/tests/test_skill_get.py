from bddrest import status, response, when

from dolphin.models import Member, Skill
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestSkill(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member)

        cls.skill = Skill(
            title='skill 1',
            description='A description',
        )
        session.add(cls.skill)
        session.commit()

    def test_get(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Getting a skill',
            f'/apiv1/skills/id: {self.skill.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.skill.id

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

