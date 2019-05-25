from bddrest import status, response, when, given

from dolphin.models import Member, EventType
from dolphin.tests.helpers import LocalApplicationTestCase


class TestEventType(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        cls.event_type1 = EventType(
            title='Type1',
        )
        session.add(cls.event_type1)

        cls.event_type2 = EventType(
            title='type2',
        )
        session.add(cls.event_type2)
        session.commit()

    def test_update(self):
        self.login(self.member.email, self.member.password)
        new_title = 'New title'
        new_description = 'A description for event type'

        with self.given(
            f'Updating an event type',
            f'/apiv1/eventtypes/id: {self.event_type1.id}',
            f'UPDATE',
            json=dict(
                title=new_title,
                description=new_description,
            ),
        ):
            assert status == 200
            assert response.json['id'] == self.event_type1.id
            assert response.json['title'] == new_title
            assert response.json['description'] == new_description

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group with integer type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when('Trying to pass with same title')
            assert status == 200

            when(
                'Title is repetitive',
                json=given | dict(title=self.event_type2.title)
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=given | dict(title=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when('Invalid parameter is in the form', json=dict(a='a'))
            assert status == '707 Invalid field, only following fields are ' \
                'accepted: title, description'

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with none title',
                json=dict(title=None)
            )
            assert status == '727 Title Is Null'

            when(
                'Description length is less than limit',
                json=given | dict(description=(512 + 1) * 'a'),
            )
            assert status == '703 At Most 512 Characters Are Valid For ' \
                'Description'

            when('Request is not authorized', authorization=None)
            assert status == 401

