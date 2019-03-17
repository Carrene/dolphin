from bddrest import status, response, when

from dolphin.models import Member, Phase, Skill
from dolphin.tests.helpers import create_workflow, LocalApplicationTestCase, \
    oauth_mockup_server


class TestPhase(LocalApplicationTestCase):

    @classmethod
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

        cls.skill = Skill(title='skill 1')
        session.add(cls.skill)

        cls.workflow = create_workflow()
        session.add(cls.workflow)

        cls.phase = Phase(
            title='phase 1',
            order=1,
            skill=cls.skill,
            workflow=cls.workflow,
        )
        session.add(cls.phase)
        session.commit()

    def test_create(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'Creating a phase',
            f'/apiv1/workflows/id: {self.workflow.id}/phases',
            'CREATE',
            json=dict(
                title='new phase',
                skill_id=self.skill.id,
                order=self.phase.order + 1
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['order'] == self.phase.order
            assert response.json['skillId'] == self.skill.id

            when(
                'Title is repetitive',
                json=given | dict(title=cls.phase.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Order is repetitive',
                json=given | dict(title=cls.phase.order)
            )
            assert status == '615 Repetitive Order'

            when(
                'Order is repetitive',
                json=given | dict(title=cls.phase.order)
            )
            assert status == '615 Repetitive Order'

            when(
                'Title length is more than limit',
                json=given | dict(title=('a' * 50) + 1)
            )
            assert status == '615 Repetitive Order'

            when('Title is not in form', json=given - 'title')
            assert status == '610 Title Not In Form'

            when('Order type is wrong', json=given | dict(order='order'))
            assert status == '741 Invalid Order Type'

            when('Order is not in form', json=given | dict(order='order'))
            assert status == '742 Order Not In Form'

            when(
                'Workflow is not found',
                url=f'/apiv1/workflows/id: {cls.workflow.id}/phases'
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

