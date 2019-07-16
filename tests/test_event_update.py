import datetime

from bddrest import status, response, when, given

from dolphin.models import Member, EventType, Event
from .helpers import LocalApplicationTestCase, oauth_mockup_server


class TestEvent(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1,
        )
        session.add(cls.member)

        event_type1 = EventType(
            title='Type 1',
        )
        session.add(event_type1)

        cls.event_type2 = EventType(
            title='Type 2',
        )
        session.add(cls.event_type2)

        cls.event1 = Event(
            title='First event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type1,
            repeat='never',
        )
        session.add(cls.event1)

        cls.event2 = Event(
            title='Second event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type1,
            repeat='yearly',
        )
        session.add(cls.event2)
        session.commit()

    def test_add(self):
        self.login(self.member.email)
        title = 'New event'
        repeat = 'monthly'
        start_date = datetime.datetime.now().isoformat()
        end_date = datetime.datetime.now().isoformat()

        with oauth_mockup_server(), self.given(
            f'Updating an event',
            f'/apiv1/events/id: {self.event1.id}',
            f'Update',
            json=dict(
                title=title,
                startDate=start_date,
                endDate=end_date,
                repeat=repeat,
                eventTypeId=self.event_type2.id,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['startDate'] == start_date
            assert response.json['endDate'] == end_date
            assert response.json['repeat'] == repeat
            assert response.json['eventTypeId'] == self.event_type2.id

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=given | dict(title=self.event2.title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Title length is more than limit',
                json=given | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At Most 50 Characters Are Valid For Title'

            when(
                'Trying to pass with none title',
                json=given | dict(title=None)
            )
            assert status == '727 Title Is Null'

            when(
                'Start date format is wrong',
                json=given | dict(startDate='30-20-20')
            )
            assert status == '791 Invalid Start Date Format'

            when(
                'End date format is wrong',
                json=given | dict(endDate='30-20-20')
            )
            assert status == '790 Invalid End Date Format'

            when(
                'End date must be greater than start date',
                json=given | dict(
                    startDate=end_date,
                    endDate=start_date,
                    title='Another title',
                )
            )
            assert status == '657 End Date Must Be Greater Than Start Date'

            when('The event-type not found', json=given | dict(eventTypeId=0))
            assert status == '658 Event Type Not Found'

            when(
                'Invalid repeat value is in form',
                json=given | dict(repeat='a')
            )
            assert status == '910 Invalid Repeat, only one of ' \
                '"yearly, monthly, never" will be accepted'

            when('Event not found', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Intended event with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when('Request is not authorized', authorization=None)
            assert status == 401

