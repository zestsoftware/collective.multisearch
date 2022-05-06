from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer


class IMultisearchPortletManager(IPortletManager):
    """Interface for multisearch portlet manager"""


class IMultiSearchPortletManagerRenderer(IPortletManagerRenderer):
    """Interface for multisearch portlet manager renderer"""


class IMultiSearchPortletAssignmentMapping(IPortletAssignmentMapping):
    """Interface for multisearch portlet assignment mapping"""
