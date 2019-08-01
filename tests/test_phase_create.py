from bddrest import status, response, when, given

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Phase, Specialty, Workflow, Skill


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
        cls.specialty = Specialty(
            title='specialty 1',
            skill=skill,
        )

        session.add(cls.specialty)

        cls.workflow1 = Workflow(title='Workflow 1')
        session.add(cls.workflow1)

        cls.workflow2 = Workflow(title='Workflow 2')
        session.add(cls.workflow2)

        cls.phase1 = Phase(
            title='phase 1',
            order=1,
            specialty=cls.specialty,
            workflow=cls.workflow1,
        )
        session.add(cls.phase1)

        cls.phase2 = Phase(
            title='phase 2',
            order=2,
            specialty=cls.specialty,
            workflow=cls.workflow2,
        )
        session.add(cls.phase2)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'new phase'
        description = 'new description'

        with oauth_mockup_server(), self.given(
            'Creating a phase',
            f'/apiv1/workflows/id: {self.workflow1.id}/phases',
            'CREATE',
            json=dict(
                title=title,
                specialtyId=self.specialty.id,
                order=self.phase1.order + 2,
                description=description
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['order'] == self.phase1.order + 2
            assert response.json['specialtyId'] == self.specialty.id
            assert response.json['description'] == description

            when(
                'Title is same as title of a phase in another workflow',
                json=given | dict(title=self.phase2.title, order=0),
            )
            assert status == 200

            when(
                'Order is same as order of a phase in another workflow',
                json=given | dict(
                    order=self.phase2.order,
                    title='another title'
                ),
            )
            assert status == 200

            when(
                'Title is repetitive',
                json=given | dict(title=self.phase1.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Order is repetitive',
                json=given | dict(order=self.phase1.order, title='new title')
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

            when('Title is not in form', json=given - 'title')
            assert status == '710 Title Not In Form'

            when(
                'Order type is wrong',
                json=given | dict(order='order', title='new title')
            )
            assert status == '741 Invalid Order Type'

            when(
                'Order is not in form',
                json=given - 'order' | dict(title='new title')
            )
            assert status == '742 Order Not In Form'

            when(
                'Workflow is not found',
                url_parameters=given | dict(id=0),
                json=given | dict(title='new title', order=3)
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

