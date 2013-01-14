# Local search portlet: customized for the multi_search view.

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.config import COLUMN_COUNT

columnVocabulary = SimpleVocabulary.fromItems(
    [(_('No prefered column'), 0)] +
    [(x+1, x+1) for x in range(0, COLUMN_COUNT)])

class ILocalSearchPortlet(IPortletDataProvider):
    dtitle = schema.TextLine(
        title=_('Title for the portlet'),
        required=False)
    
    results_number = schema.Int(
        title=_('Number of results displayed'),
        required=True,
        default=5)

    show_more_results = schema.Bool(
        title=_('Show link for more results'),
        default=True
        )

    assigned_column = schema.Choice(
        title=_('Column where the portlet is rendered'),
        required=True,
        vocabulary=columnVocabulary
        )


class Assignment(base.Assignment):
    implements(ILocalSearchPortlet)

    def __init__(self,
                 dtitle='',
                 results_number=5,
                 show_more_results=True,
                 assigned_column=0):
        if not dtitle:
            dtitle = _('Local results')

        self.dtitle = dtitle
        self.show_more_results = show_more_results
        self.results_number = results_number
        self.assigned_column = assigned_column

    @property
    def title(self):
        return self.dtitle
    

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/results_portlet.pt')

    def extra_results_link(self):
        query = self.request.get('SearchableText', None)

        return '%s/search?SearchableText=%s' % (
            self.context.absolute_url(),
            query)

    def show_more_results(self):
        return self.data.show_more_results and len(self.make_results()) > 0

    def make_results(self):
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

    def results(self):
        if not hasattr(self, '_results'):
            self._results = self.make_results()

        return self._results


class AddForm(base.AddForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Add Local Search Portlet"

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Edit Local Search Portlet"
