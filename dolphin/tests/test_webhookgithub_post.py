from bddrest import status

from dolphin.tests.helpers import LocalApplicationTestCase


class TestGithubWebhook(LocalApplicationTestCase):

#    @classmethod
#    @AuditLogContext(dict())
#    def mockup(cls):
#        session = cls.create_session()
#
#        cls.member = Member(
#            title='First Member',
#            email='member1@example.com',
#            access_token='access token 1',
#            phone=123456789,
#            reference_id=1
#        )
#        session.add(cls.member)
#        session.commit()

 def test_github_webhook(self):

        with self.given(
            f'POST all action in organization github',
            f'/ghv3/githubs',
            f'POST',
            json=dict(
                roomId='1',
                memberReferenceId='fd',
            )
        ):
            assert status == 200

