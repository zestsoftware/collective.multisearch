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


from collective.multisearch.browser.interfaces import IMultisearchPortletManager
from collective.multisearch.browser.interfaces import IMultiSearchPortletManagerRenderer

from plone.portlets.interfaces import IPortletManagerRenderer

class MultiSearchContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IMultisearchPortletManager)
    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')


class MultiSearchManagerContextualPortlets(ManageContextualPortlets):
    def get_manager(self):
        editmanager = queryMultiAdapter(
            (self.context, self.request, self),
            IMultiSearchPortletManagerRenderer,
            'multisearch.MultisearchPortletManager')

        editmanager.update()
        return editmanager.render()
