import datetime

from bddrest import status, response, when, given

from dolphin.models import Member
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestTimecard(LocalApplicationTestCase):

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
        session.commit()

    def test_create(self):
        self.login(self.member.email)
        start_date = datetime.datetime.now().isoformat()
        end_date = datetime.datetime.now().isoformat()
        summary = 'Some summary'

        with oauth_mockup_server(), self.given(
            'Creating a timecard',
            '/apiv1/timecards',
            'CREATE',
            json=dict(
                startDate=start_date,
                endDate=end_date,
                estimatedTime=2,
                summary=summary,
            ),
        ):
            assert status == 200
            assert response.json['id'] is not None
            assert response.json['startDate'] == start_date
            assert response.json['endDate'] == end_date
            assert response.json['estimatedTime'] == 2
            assert response.json['summary'] == summary

            when('Trying to pass without form parameters', json={})
            assert status == '708 Empty Form'

            when(
                'Summary length is less than limit',
                json=given | dict(summary=(1024 + 1) * 'a'),
            )
            assert status == '902 At Most 1024 Characters Are Valid For ' \
                'Summary'

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
                'Trying to pass without summary',
                json=given - 'summary',
            )
            assert status == '799 Summary Not In Form'

            when(
                'Trying to pass without estimated time',
                json=given - 'estimatedTime',
            )
            assert status == '901 Estimated Time Not In Form'

            when(
                'Estimated time type is wrong',
                json=given | dict(estimatedTime='time'),
            )
            assert status == '900 Invalid Estimated Time Type'

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
                )
            )
            assert status == '657 End Date Must Be Greater Than Start Date'

            when('Start date is null', json=given | dict(startDate=None))
            assert status == '905 Start Date Is Null'

            when('End date is null', json=given | dict(endDate=None))
            assert status == '906 End Date Is Null'

            when('Estimated time is null', json=given | dict(estimatedTime=None))
            assert status == '904 Estimated Time Is Null'

            when('Summary is null', json=given | dict(summary=None))
            assert status == '903 Summary Is Null'

            when('Request is not authorized', authorization=None)
            assert status == 401

