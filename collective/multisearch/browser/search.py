from five import grok

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from collective.multisearch.config import COLUMN_COUNT
from collective.multisearch.utils import get_column_number

class MultiSearchView(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('multisearch')
    grok.require('zope2.View')

    def can_manage_portlets(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plone.app.portlets.ManagePortlets',
                                     self.context)

    def get_column_number(self):
        return get_column_number(self.context)

    def get_portlets(self):
        column = getUtility(IPortletManager,
                             name='multisearch.MultisearchPortletManager',
                             context=self.context)

        retriever = getMultiAdapter((self.context, column),
                                    IPortletRetriever)

        column_number = get_column_number(self.context)
        columns = dict([(index, []) for index in range(0, column_number + 1)])

        for portlet in retriever.getPortlets():
            assignment = portlet.get('assignment', None)
            if assignment is None:
                continue

            # Column number must be btween 0 and COLUMN_COUNT
            assignment_column = max(0, min(assignment.assigned_column, column_number))
            renderer = queryMultiAdapter((self.context, self.request, self, column, assignment),
                                         IPortletRenderer)
            if not renderer.available:
                continue

            renderer.update()

            columns[assignment_column].append(renderer)

        if columns[0]:
            # We need to place the portlets in the existing columns.
            # First we sort them by size.
            unplaced = sorted(
                [(renderer, len(renderer.results()) or 1)
                 for renderer in columns[0]],
                key = lambda x: x[1],
                reverse=True)

            sizes = dict(
                [(index, sum([len(renderer.results()) or 1 for renderer in columns[index]]))
                 for index in columns.keys() if index])

            for portlet, p_size in unplaced:
                col_index = sorted(sizes.items(),
                                   key = lambda x: x[1])[0][0]

                columns[col_index].append(portlet)
                sizes[col_index] += p_size

        return [columns[index] for index in sorted(columns.keys()) if index]
