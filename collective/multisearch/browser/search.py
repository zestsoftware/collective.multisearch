from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletRetriever
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter

from collective.multisearch.config import CHARACTERS_PER_LINE
from collective.multisearch.utils import assign_columns
from collective.multisearch.utils import get_column_number


class MultiSearchView(BrowserView):

    def can_manage_portlets(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plone.app.portlets.ManagePortlets',
                                     self.context)

    def get_column_number(self):
        return get_column_number(self.context)

    def get_portlets(self):
        manager = getUtility(IPortletManager,
                             name='multisearch.MultisearchPortletManager',
                             context=self.context)

        retriever = getMultiAdapter((self.context, manager),
                                    IPortletRetriever)

        columns_number = get_column_number(self.context)
        max_length = CHARACTERS_PER_LINE / columns_number
        portlets = []

        for portlet in retriever.getPortlets():
            assignment = portlet.get('assignment', None)
            if assignment is None:
                continue

            renderer = queryMultiAdapter(
                (self.context, self.request, self, manager, assignment),
                IPortletRenderer)
            renderer.max_length = max_length

            if not renderer.available:
                continue

            renderer.update()
            portlets.append((assignment, renderer))

        return assign_columns(portlets, columns_number)
