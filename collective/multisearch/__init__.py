# -*- extra stuff goes here -*-
from zope.i18nmessageid import MessageFactory
MultiSearchMessageFactory = MessageFactory(u'collective.multisearch')

from collective.multisearch import patches
patches.apply_all()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
