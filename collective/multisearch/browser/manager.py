# Custom manager for the multisearch portlet manager: inactive for the moment.

from zope import component
from zope.interface import implements

from plone.portlets.manager import PortletManager
from plone.portlets.interfaces import IPortletManager

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from collective.multisearch.browser.interfaces import IMultisearchPortletManager

class MultisearchPortletManager(PortletManager):
    component.adapts(IPloneSiteRoot)
    implements(IMultisearchPortletManager)

    def getAddablePortletTypes(self):
        return super(MultisearchManager, self).getAddablePortletTypes()
