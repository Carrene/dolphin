from bddrest import status, response, Update, when, Remove, Append

from dolphin.tests.helpers import LocalApplicationTestCase
from dolphin.controllers.root import Root
from dolphin.models import Release, Administrator


class TestRelease(LocalApplicationTestCase):
    __controller_factory__ = Root

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        administrator = Administrator(
            title='First Administrator',
            email=None,
            phone=123456789
        )
        session.add(administrator)
        session.commit()

        release = Release(
            administrator_id=administrator.id,
            title='My first release',
            description='A decription for my release',
            due_date='2020-2-20',
            cutoff='2030-2-20',
        )
        session.add(release)
        session.flush()
        cls.administrator_id = administrator.id
        session.commit()

    def test_create(self):
        assert 1 == 1
        with self.given(
            'Createing a release',
            '/apiv1/releases',
            'CREATE',
            form=dict(
                administratorId=self.administrator_id,
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
                form=Update(description='Description')
            )
            assert status == '703 At least 20 characters are needed for '\
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


