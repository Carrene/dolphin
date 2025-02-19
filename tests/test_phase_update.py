from bddrest import status, response, when, given, Update

from .helpers import create_workflow, LocalApplicationTestCase, \
    oauth_mockup_server
from dolphin.models import Member, Phase, Specialty, Skill


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
        skill = Skill(title='First Skill')
        cls.specialty1 = Specialty(
            title='First Specialty',
            skill=skill,
        )

        session.add(cls.specialty1)

        cls.specialty2 = Specialty(
            title='specialty 1',
            skill=skill,
        )
        session.add(cls.specialty2)

        cls.workflow = create_workflow()
        session.add(cls.workflow)

        cls.phase1 = Phase(
            title='phase 1',
            order=1,
            specialty=cls.specialty1,
            workflow=cls.workflow,
            description='Description for phase 1',
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='phase 2',
            order=2,
            specialty=cls.specialty1,
            workflow=cls.workflow,
            description='Description for phase 2',
        )
        session.add(cls.phase2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)
        new_title = 'new title'
        new_order = self.phase1.order + 2
        new_description = 'new description'

        with oauth_mockup_server(), self.given(
            f'Updating a phase',
            f'/apiv1/workflows/workflow_id: {self.workflow.id}/' \
                f'phases/id: {self.phase1.id}',
            f'UPDATE',
            json=dict(
                title=new_title,
                specialtyId=self.specialty2.id,
                order=new_order,
                description=new_description,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == new_title
            assert response.json['order'] == new_order
            assert response.json['specialtyId'] == self.specialty2.id
            assert response.json['description'] == new_description

            when('Specialty id not in form', json=given - 'specialtyId')
            assert status == 200

            when(
                'Title is repetitive',
                json=given | dict(title=self.phase2.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Trying to pass using id is alphabetical',
                url_parameters=Update(id='not-integer')
            )
            assert status == 404

            when(
                'Phase not exit with this id',
                url_parameters=Update(id=0)
            )
            assert status == 404

            when(
                'Order is repetitive',
                json=given | dict(order=self.phase2.order)
            )
            assert status == '615 Repetitive Order'

            when(
                'Title length is more than limit',
                json=given | dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Title length is more than limit',
                json=given | dict(description=(512 + 1) * 'a')
            )
            assert status == '703 At Most 512 Characters Are Valid For Description'

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
                'Specialty is not found',
                json=given | dict(specialtyId=0),
            )
            assert status == '645 Specialty Not Found'

            when(
                'Specialty id type is wrong',
                json=given | dict(specialtyId='not-integer'),
            )
            assert status == '788 Invalid Specialty Id Type'

            when('Request is not authorized', authorization=None)
            assert status == 401

