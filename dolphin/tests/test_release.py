from bddrest import status, response, Update, when, Remove, Append

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.models import Release, Manager


class TestRelease(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        manager = Manager(
            title='First Manager',
            email=None,
            phone=123456789
        )
        session.add(manager)
        session.flush()

        release = Release(
            manager_id=manager.id,
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.flush()
        cls.manager_id = manager.id
        session.commit()

    def test_create(self):
        with self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            form=dict(
                managerId=self.manager_id,
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
            assert status == '710 Title not exists'

            when(
                'Title length is more than limit',
                form=Update(
                    title='This is a title with the length more than 50 \
                    characters'
                )
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Description length is less than limit',
                form=Update(description=((512 + 1) * 'a'))
            )
            assert status == '703 At most 512 characters are valid for '\
                'description'
            when(
                'Due date format is wrong',
                form=Update(dueDate='20-20-20')
                    )
            assert status == '701 Invalid due date format'

            when(
                'Due date is not in form',
                form=Remove('dueDate')
            )
            assert status == '711 Due date not exists'

            when(
                'Cutoff format is wrong',
                form=Update(cutoff='30-20-20'),
                    )
            assert status == '702 Invalid cutoff format'

            when(
                'Due date is not in form',
                form=Remove('cutoff')
            )
            assert status == '712 Cutoff not exists'

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
                url_parameters=dict(id='no_integer')
            )
            assert status == 404


            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Title length is more than limit',
                form=Update(
                    title='This is a title with the length more than 50 \
                    characters'
                )
            )
            assert status == '704 At most 50 characters are valid for title'

            when(
                'Title is repetitive',
                form=Update(title='My interesting release')
            )
            assert status == 600
            assert status.text.startswith('Another release')

            when(
                'Description length is less than limit',
                form=Update(description=((512 + 1) * 'a'))
            )
            assert status == '703 At most 512 characters are valid for '\
                'description'

            when(
                'Due date format is wrong',
                form=Update(dueDate='20-20-20')
            )
            assert status == '701 Invalid due date format'

            when(
                'Cutoff format is wrong',
                form=Update(cutoff='30-20-20'),
            )
            assert status == '702 Invalid cutoff format'

            when(
                'Invalid status in form',
                form=Update(status='progressing')
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
                url_parameters=dict(id='no_integer')
            )
            assert status == 404

            when(
                'Intended release with integer type not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

        session = self.create_session()
        release = session.query(Release).filter(Release.id==1).one_or_none()
        assert release is None

