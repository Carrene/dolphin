import datetime

from bddrest import status, response, when, given

from dolphin.models import Member, EventType
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

        cls.event_type = EventType(
            title='Type 1',
        )
        session.add(cls.event_type)
        session.commit()

    def test_add(self):
        self.login(self.member.email)
        title = 'Event 1'
        description = 'A description for an event'
        repeat = 'never'
        start_date = datetime.datetime.now().isoformat()
        end_date = datetime.datetime.now().isoformat()

        with oauth_mockup_server(), self.given(
            'Adding an event',
            '/apiv1/events',
            'ADD',
            json=dict(
                title=title,
                eventTypeId=self.event_type.id,
                startDate=start_date,
                endDate=end_date,
                repeat=repeat,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['title'] == title
            assert response.json['startDate'] == start_date
            assert response.json['endDate'] == end_date
            assert response.json['repeat'] == repeat

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Trying to pass with repetitive title',
                json=given | dict(title=title),
            )
            assert status == '600 Repetitive Title'

            when(
                'Trying to pass without title',
                json=given - 'title',
            )
            assert status == '710 Title Not In Form'

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
                'Trying to pass without start date',
                json=given - 'startDate',
            )
            assert status == '792 Start Date Not In Form'

            when(
                'Trying to pass without end date',
                json=given - 'endDate',
            )
            assert status == '793 End Date Not In Form'

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
                'Trying to pass without event-type id',
                json=given - 'eventTypeId'
            )
            assert status == '794 Type Id Not In Form'

            when(
                'Trying to pass without repeat',
                json=given - 'repeat'
            )
            assert status == '911 Repeat Not In Form'

            when(
                'Invalid repeat value is in form',
                json=given | dict(repeat='a')
            )
            assert status == '910 Invalid Repeat, only one of ' \
                '"yearly, monthly, never" will be accepted'

            when('Request is not authorized', authorization=None)
            assert status == 401

