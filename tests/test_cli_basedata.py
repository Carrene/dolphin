from .helpers import LocalApplicationTestCase
from dolphin.models import Member, Workflow, Specialty, Group, Phase, Skill, \
    Tag, EventType


class TestDatabaseCLI(LocalApplicationTestCase):

    def test_basedata(self):
        self.__application__.insert_basedata()

        session = self.create_session()
        assert session.query(Group).filter(Group.title == 'Public').one()
        assert session.query(Skill).filter(Skill.title == 'Developer').one()
        assert session.query(Member).filter(Member.title == 'GOD').one()
        assert session.query(Member).count() == 1
        assert session.query(Phase).count() == 3
        assert session.query(Tag).count() == 3
        assert session.query(EventType).count() == 2

        assert session.query(EventType) \
            .filter(EventType.title == 'Personal') \
            .one()
        assert session.query(EventType) \
            .filter(EventType.title == 'Company-Wide') \
            .one()
        assert session.query(Specialty) \
            .filter(Specialty.title == 'front-end') \
            .one()
        assert session.query(Workflow) \
            .filter(Workflow.title == 'Default') \
            .one()

    def test_mockup(self):
        self.__application__.insert_mockup()

        session = self.create_session()
        assert session.query(Member).count() == 10

