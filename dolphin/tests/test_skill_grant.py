from bddrest import status, response, when, given

from dolphin.models import Member, Skill, SkillMember
from dolphin.tests.helpers import LocalApplicationTestCase


class TestSkill(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        cls.skill = Skill(
            title='First skill',
            description='Sample description',
        )
        session.add(cls.skill)
        session.commit()

    def test_grant(self):
        self.login(self.member.email)
        session = self.create_session()

        with self.given(
            f'Granting a skill',
            f'/apiv1/members/member_id: {self.member.id}/' \
            f'skills/skill_id: {self.skill.id}',
            f'GRANT',
        ):
            assert status == 200
            assert response.json['title'] == self.skill.title
            assert response.json['description'] == self.skill.description
            assert session.query(SkillMember) \
                .filter(
                    SkillMember.skill_id == self.skill.id,
                    SkillMember.member_id == self.member.id
                ) \
                .one()

            when('Skill is already granted to member')
            assert status == '655 Skill Already Granted'

            when(
                'Intended skill with string type not found',
                url_parameters=given | dict(skill_id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended skill with integer type not found',
                url_parameters=given | dict(skill_id=0)
            )
            assert status == 404

            when(
                'Intended member with string type not found',
                url_parameters=given | dict(member_id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended member with integer type not found',
                url_parameters=given | dict(member_id=0)
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

