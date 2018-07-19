from restfulpy.testing import ApplicableTestCase

from dolphin import Dolphin


class LocalApplicationTestCase(ApplicableTestCase):
    __application_factory__ = Dolphin

