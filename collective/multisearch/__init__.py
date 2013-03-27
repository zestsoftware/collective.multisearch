from zope.i18nmessageid import MessageFactory

MultiSearchMessageFactory = MessageFactory(u'collective.multisearch')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
