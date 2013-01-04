# Local search portlet: customized for the multi_search view.

from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.app.portlets.portlets import search

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.multisearch import MultiSearchMessageFactory as _

class ILocalSearchPortlet(search.ISearchPortlet):
    results_number = schema.Int(
        title=_('Number of results displayed'),
        required=True,
        default=5)

    show_more_results = schema.Bool(
        title=_('Show link for more results'),
        default=True
        )


class Assignment(search.Assignment):
    implements(ILocalSearchPortlet)

    def __init__(self,
                 results_number=5,
                 show_more_results=True):
        self.show_more_results = show_more_results
        self.results_number = results_number

    @property
    def title(self):
        return _(u"Local search")


class Renderer(search.Renderer):
    render = ViewPageTemplateFile('templates/local_search.pt')

    def extra_results_link(self):
        query = self.request.get('SearchableText', None)

        return '%s/search?SearchableText=%s' % (
            self.context.absolute_url(),
            query)

    def results(self):
        query = self.request.get('SearchableText', None)
        if not query:
            return []

        search_view = self.context.restrictedTraverse('@@search')
        results = search_view.results(b_size=self.data.results_number)

        return [
            {'title': x.Title(),
             'url': x.getURL(),
             'desc': x.Description()}
            for x in results]


class AddForm(search.AddForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Add Local Search Portlet"

    def create(self, data):
        return Assignment(
            results_number=data.get('results_number'),
            show_more_results=data.get('show_more_results'))


class EditForm(search.EditForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Edit Local Search Portlet"
