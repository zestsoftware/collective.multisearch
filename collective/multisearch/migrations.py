from .utils import set_column_number
from plone import api
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from zope.component import getMultiAdapter
from zope.component import getUtility

import logging


PROFILE_ID = "profile-collective.multisearch:default"

logger = logging.getLogger("collective.multisearch")


def update_schemas(context, new_fields=[]):
    manager = getUtility(
        IPortletManager, name="multisearch.MultisearchPortletManager", context=context
    )

    retriever = getMultiAdapter((context, manager), IPortletRetriever)

    portlets = retriever.getPortlets()

    for portlet in portlets:
        assignment = portlet.get("assignment", None)
        if assignment is None:
            continue

        for field_name, default_value in new_fields:
            if hasattr(assignment, field_name):
                continue

            setattr(assignment, field_name, default_value)


def add_show_description_field(context):
    update_schemas(context, [("show_description", False)])


def add_allow_subscription_field(context):
    update_schemas(context, [("allow_rss_subscription", True)])


def reapply_portlets_step(context):
    context.runImportStepFromProfile(PROFILE_ID, "portlets")


def run_browserlayer_step(context):
    context.runImportStepFromProfile(PROFILE_ID, "browserlayer")
    logger.info("Add browserlayer for collective.multisearch")


def add_verify_ssl_field(context):
    update_schemas(context, [("verify_ssl", True)])
    logger.info("Added verify_ssl field to search portlets")


def migrate_to_configuration_registry(context):
    # Move our settings from portal_properties to the registry.
    try:
        pprops = api.portal.get_tool("portal_properties")
    except api.exc.InvalidParameterError:
        return
    sheet_name = "multisearch_properties"
    if sheet_name not in list(pprops.keys()):
        return
    ms_props = pprops.get(sheet_name)
    if not ms_props.hasProperty("column_number"):
        return
    old_value = ms_props.column_number
    # This saves it to the registry:
    set_column_number(old_value)
    # Remove the old sheet.
    pprops._delObject(sheet_name)
