# Custom manager for the multisearch portlet manager: inactive for the moment.

from zope import component
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.interface import Interface

from plone.app.portlets.browser.manage  import ManageContextualPortlets

from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletManager
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView

from collective.multisearch.config import COLUMN_COUNT
from collective.multisearch.utils import get_column_number
from collective.multisearch.browser.interfaces import IMultisearchPortletManager
from collective.multisearch.browser.interfaces import IMultiSearchPortletManagerRenderer

from plone.portlets.interfaces import IPortletManagerRenderer

class MultiSearchContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IMultisearchPortletManager)
    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')

    def get_column_number(self):
        return {'current': get_column_number(self.context),
                'available': range(1, COLUMN_COUNT+1)}


class MultiSearchManagerContextualPortlets(ManageContextualPortlets):
    def get_manager(self):
        editmanager = queryMultiAdapter(
            (self.context, self.request, self),
            IMultiSearchPortletManagerRenderer,
            'multisearch.MultisearchPortletManager')

        editmanager.update()
        return editmanager.render()
