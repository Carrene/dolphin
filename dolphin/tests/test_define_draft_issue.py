from bddrest import status, response, when

from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member


class TestDraftIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(cls.member1)
        session.commit()

    def test_define(self):
        self.login(self.member1.email)

        with oauth_mockup_server(), self.given(
            'Define a draft issue',
            '/apiv1/draftissues',
            'DEFINE',
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['issueId'] is None

            when(
                'Trying to pass with invalid form parameres',
                form=dict(a='a'),
            )
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description, kind, days, status, projectId,' \
                ' dueDate, priority'

            when('Request is not authorized', authorization=None)
            assert status == 401

