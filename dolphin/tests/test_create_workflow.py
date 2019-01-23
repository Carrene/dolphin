from bddrest import status, response, when

from dolphin.models import Member
from dolphin.tests.helpers import create_workflow, LocalApplicationTestCase, \
    oauth_mockup_server


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

        cls.workflow = create_workflow()
        session.add(cls.workflow)
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        title = 'first workflow'

        with oauth_mockup_server(), self.given(
            'Creating a workflow',
            '/apiv1/workflows',
            'CREATE',
            json=dict(title=title),
        ):
            assert status == 200
            assert response.json['title'] == title

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=dict(title=self.workflow.title),
            )
            assert status == '600 Repetitive Title'

            when('The title format is invalid', form=dict(title=' a'))
            assert status == '747 Invalid Title Format'

            when(
                'Trying to pass without title',
                json=dict(a='a'),
            )
            assert status == '710 Title Not In Form'

            when(
                'Title length is more than limit',
                json=dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Trying to pass with none title',
                json=dict(title=None)
            )
            assert status == '727 Title Is None'

            when('Request is not authorized', authorization=None)
            assert status == 401

