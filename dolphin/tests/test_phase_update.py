from bddrest import status, response, when, given, Update

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

        cls.skill1 = Skill(title='skill 1')
        session.add(cls.skill1)

        cls.skill2 = Skill(title='skill 1')
        session.add(cls.skill2)

        cls.workflow = create_workflow()
        session.add(cls.workflow)

        cls.phase1 = Phase(
            title='phase 1',
            order=1,
            skill=cls.skill1,
            workflow=cls.workflow,
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='phase 2',
            order=2,
            skill=cls.skill1,
            workflow=cls.workflow,
        )
        session.add(cls.phase2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)
        new_title = 'new title'
        new_order = self.phase1.order + 2

        with oauth_mockup_server(), self.given(
            f'Updating a phase',
            f'/apiv1/workflows/workflow_id: {self.workflow.id}/' \
                f'phases/id: {self.phase1.id}',
            f'UPDATE',
            json=dict(
                title=new_title,
                skillId=self.skill2.id,
                order=new_order,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == new_title
            assert response.json['order'] == new_order
            assert response.json['skillId'] == self.skill2.id

            when(
                'Title is repetitive',
                json=given | dict(title=self.phase2.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Order is repetitive',
                json=given | dict(order=self.phase2.order)
            )
            assert status == '615 Repetitive Order'

            when(
                'Title length is more than limit',
                json=given | dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Valid For Title'

            when(
                'Order type is wrong',
                json=given | dict(order='order')
            )
            assert status == '741 Invalid Order Type'

            when(
                'Workflow is not found',
                url_parameters=Update(workflow_id=0),
            )
            assert status == 404

            when(
                'Skill is not found',
                json=given | dict(skillId=0),
            )
            assert status == '645 Skill Not Found'

            when(
                'Skill id type is wrong',
                json=given | dict(skillId='not-integer'),
            )
            assert status == '788 Invalid Skill Id Type'

            when('Request is not authorized', authorization=None)
            assert status == 401

