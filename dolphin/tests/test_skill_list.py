from bddrest import when, response, status

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Skill, Member, SkillMember


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

        skill1 = Skill(
            title='first skill',
            members=[cls.member],
        )
        session.add(skill1)

        skill2 = Skill(
            title='second skill',
            members=[cls.member],
        )
        session.add(skill2)

        skill3 = Skill(
            title='thired skill',
        )
        session.add(skill3)
        session.commit()

    def test_list(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'List of skills',
            '/apiv1/skills',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id'] == 2

            when('Trying pagination response', query=dict(take=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert response.json[0]['id'] == 2
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

    def test_list_skills_of_member(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'List of member\'s skills',
            f'/apiv1/members/id: {self.member.id}/skills',
            f'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id']

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id']

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

