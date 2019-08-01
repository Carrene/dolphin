from bddrest import status, response, when, Update

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, Workflow


class TestWorkflow(LocalApplicationTestCase):

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

        cls.workflow1 = Workflow(
            title='Already-added',
            description='A description for workflow',
        )
        session.add(cls.workflow1)

        cls.workflow2 = Workflow(
            title='Second workflow',
            description='A description for second workflow',
        )
        session.add(cls.workflow2)
        session.commit()

    def test_update(self):
        self.login(self.member.email)
        title = 'first workflow'
        description = 'Another description'

        with oauth_mockup_server(), self.given(
            'Updating a workflow',
            f'/apiv1/workflows/id: {self.workflow1.id}',
            'UPDATE',
            json=dict(
                title=title,
                description=description,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['description'] == description

            when('Workflow not found', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Intended workflow with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when('There is no parameters in form', json={})
            assert status == '708 Empty Form'

            when(
                'There is invalid form parameters',
                json=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description'

            when(
                'Title is repetitive',
                json=dict(title=self.workflow2.title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Title is null',
                json=dict(title=None)
            )
            assert status == '727 Title Is Null'

            when(
                'Description length is more than limit',
                json=Update(description=((8192 + 1) * 'a'))
            )
            assert status == '703 At Most 8192 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

