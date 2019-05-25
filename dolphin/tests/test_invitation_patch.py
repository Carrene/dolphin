from bddrest import status, when

from dolphin.models import Member, Organization, OrganizationMember
from dolphin.tests.helpers import LocalApplicationTestCase


class TestInvitation(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member1 = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member1)

        cls.member2 = Member(
            title='Second Member',
            email='member2@example.com',
            phone=123456788,
            password='123ABCabc',
        )
        session.add(cls.member2)

        cls.member3 = Member(
            title='Third Member',
            email='member3@example.com',
            phone=123456787,
            password='123ABCabc',
        )
        session.add(cls.member3)

        cls.organization = Organization(
            title='organization-title',
        )
        session.add(cls.organization)
        session.flush()

        organization_member1 = OrganizationMember(
            organization_id=cls.organization.id,
            member_id=cls.member1.id,
            role='owner'
        )
        session.add(organization_member1)
        session.commit()

    def test_invite(self):
        self.login(email=self.member1.email)

        with self.given(
            f'Inviting to the organization has successfully created',
            f'/apiv1/organizations/id: {self.organization.id}/invitations',
            f'PATCH',
            json=[
                dict(
                    op='CREATE',
                    path='',
                    value=dict(
                        email=self.member2.email,
                        role='member',
                        scopes='title,email',
                        applicationId=1,
                        redirectUri='www.example.com',
                    )
                ),
                dict(
                    op='CREATE',
                    path='',
                    value=dict(
                        email=self.member3.email,
                        role='member',
                        scopes='title,email',
                        applicationId=1,
                        redirectUri='www.example.com',
                    )
                ),
            ]
        ):
            assert status == 200

            when(
                'One of requests response faces non 200 OK',
                json=[
                    dict(
                        op='CREATE',
                        path='',
                        value=dict(
                            email=self.member1.email,
                            role='member',
                            scopes='title,email',
                            applicationId=1,
                            redirectUri='www.example.com',
                        )
                    )
                ]
            )
            assert status == '628 Already In This Organization'

