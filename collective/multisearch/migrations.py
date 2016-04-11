import logging

from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever

PROFILE_ID = 'profile-collective.multisearch:default'

logger = logging.getLogger("collective.multisearch")


def update_schemas(context, new_fields=[]):
    manager = getUtility(IPortletManager,
                         name='multisearch.MultisearchPortletManager',
                         context=context)

    retriever = getMultiAdapter((context, manager),
                                IPortletRetriever)

    portlets = retriever.getPortlets()

    for portlet in portlets:
        assignment = portlet.get('assignment', None)
        if assignment is None:
            continue

        for field_name, default_value in new_fields:
            if hasattr(assignment, field_name):
                continue

            setattr(assignment, field_name, default_value)


def add_show_description_field(context):
    update_schemas(context, [('show_description', False)])

def add_allow_subscription_field(context):
    update_schemas(context, [('allow_rss_subscription', True)])

def reapply_portlets_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'portlets')

def run_browserlayer_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'browserlayer')
    logger.info("Add browserlayer for collective.multisearch")
    
def add_verify_ssl_field(context):
    update_schemas(context, [('verify_ssl', True)])
    logger.info("Added verify_ssl field to search portlets")