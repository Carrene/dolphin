from bddrest import status, response, Update, when, Remove, Append, given_form

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Release, Manager


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        release1 = Release(
            title='My first release',
            description='A decription for my first release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        release2 = Release(
            title='My second release',
            description='A decription for my second release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        release3 = Release(
            title='My third release',
            description='A decription for my third release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )

        release4 = Release(
            title='My fourth release',
            description='A decription for my fourth release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add_all([release1, release2, release3, release4])
        session.commit()

    def test_create(self):
        with self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            form=dict(
                title='My awesome release',
                description='Decription for my release',
                dueDate='2020-2-20',
                cutoff='2030-2-20'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My awesome release'
            assert response.json['description'] == 'Decription for my release'
            assert response.json['dueDate'] == '2020-02-20T00:00:00'
            assert response.json['cutoff'] == '2030-02-20T00:00:00'
            assert response.json['status'] is None

            when(
                'Title is not in form',
                form=Remove('title')
            )
            assert status == '710 Title not in form'

            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At most 512 characters are valid for ' \
                'description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid due date format'

            when(
                'Due date is not in form',
                form=given_form - 'dueDate' | dict(title='Another title')
            )
            assert status == '711 Due date not in form'

            when(
                'Cutoff format is wrong',
                form=given_form | dict(
                    cutoff='30-20-20',
                    title='Another title'
                )
            )
            assert status == '702 Invalid cutoff format'

            when(
                'Due date is not in form',
                form=given_form - 'cutoff' | dict(title='Another title')
            )
            assert status == '712 Cutoff not in form'

            when(
                'Invalid status in form',
                form=given_form | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')


    def test_update(self):
        with self.given(
            'Updating a release',
            '/apiv1/releases/id:1',
            'UPDATE',
            form=dict(
                title='My interesting release',
                description='This is my new awesome release',
                dueDate='2200-2-2',
                cutoff='2300-2-2',
                status='in-progress'
            )
        ):
            assert status == 200
            assert response.json['title'] == 'My interesting release'
            assert response.json['description'] == 'This is my new awesome release'
            assert response.json['dueDate'] == '2200-02-02T00:00:00'
            assert response.json['cutoff'] == '2300-02-02T00:00:00'
            assert response.json['status'] == 'in-progress'

            when(
                'Intended release with string type not found',
                form=given_form | dict(title='Another title'),
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                form=given_form | dict(title='Another title'),
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title length is more than limit',
                form=given_form | dict(title=((50 + 1) * 'a'))
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Title is repetitive',
                form=Update(title='My interesting release')
            )
            assert status == 600
            assert status.text.startswith('Another release with title')

            when(
                'Description length is less than limit',
                form=given_form | dict(
                    description=((512 + 1) * 'a'),
                    title='Another title'
                )
            )
            assert status == '703 At most 512 characters are valid for '\
                'description'

            when(
                'Due date format is wrong',
                form=given_form | dict(
                    dueDate='20-20-20',
                    title='Another title'
                )
            )
            assert status == '701 Invalid due date format'

            when(
                'Cutoff format is wrong',
                form=given_form | dict(
                    cutoff='30-20-20',
                    title='Another title'
                )
            )
            assert status == '702 Invalid cutoff format'

            when(
                'Invalid status in form',
                form=given_form | dict(
                    status='progressing',
                    title='Another title'
                )
            )
            assert status == 705
            assert status.text.startswith('Invalid status')

        with self.given(
            'Send HTTP request with empty form parameter',
            '/apiv1/releases/id:1',
            'UPDATE',
            form=dict()
        ):
            assert status == '708 No parameter exists in the form'

    def test_abort(self):
        with self.given(
            'Aborting a release',
            '/apiv1/releases/id:1',
            'ABORT'
        ):
            assert status == 200

            when(
                'Intended release with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form not allowed'

        session = self.create_session()
        release = session.query(Release).filter(Release.id == 1).one_or_none()
        assert release is None

    def test_list(self):
        with self.given(
            'List releases',
            '/apiv1/releases',
            'LIST'
        ):
            assert status == 200
            assert len(response.json) == 4

        with self.given(
            'Sort releases by title',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='title')
        ):
            assert response.json[0]['title'] == 'My awesome release'

            when(
                'Reverse sorting titles by alphabet',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'My third release'

        with self.given(
            'Filter releases',
            '/apiv1/releases',
            'LIST',
            query=dict(sort='id', take=1, skip=2)
        ):
            assert response.json[0]['title'] == 'My fourth release'

            when(
                'List releases except one of them',
                query=dict(title='!My second release')
            )
            assert response.json[0]['title'] == 'My third release'

        with self.given(
             'Issues pagination',
             '/apiv1/releases',
             'LIST',
             query=dict(sort='id', take=1, skip=2)
         ):
            assert response.json[0]['title'] == 'My fourth release'

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-title', take=1, skip=2)
            )
            assert response.json[0]['title'] == 'My fourth release'


