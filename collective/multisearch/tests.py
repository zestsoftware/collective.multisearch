import unittest
import doctest

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
from zope.component import testing
from zope.testing import doctestunit

import collective.multisearch

ptc.setupPloneSite()
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.multisearch)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        # doctestunit.DocFileSuite(
        #    'README.txt', package='collective.multisearch',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='collective.multisearch.utils',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=OPTIONFLAGS),


        # Integration tests that use PloneTestCase
        # ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.multisearch',
        #    test_class=TestCase),

        # ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.multisearch',
        #    test_class=TestCase),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
