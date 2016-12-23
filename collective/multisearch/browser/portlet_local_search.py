# Local search portlet: customized for the multi_search view.
from urllib import quote_plus

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.config import CHARACTERS_PER_LINE
from collective.multisearch.config import COLUMN_COUNT
from collective.multisearch.utils import make_excerpt

columnVocabulary = SimpleVocabulary.fromItems(
    [(_('No prefered column'), 0)] +
    [(x + 1, x + 1) for x in range(0, COLUMN_COUNT)])


class ILocalSearchPortlet(IPortletDataProvider):
    dtitle = schema.TextLine(
        title=_(u'Title for the portlet'),
        description=_(u'Title shown in the header of the portlet'),
        required=False)

    results_number = schema.Int(
        title=_(u'Number of results displayed'),
        description=_(u'Maximum number of results displayed'),
        required=True,
        default=5)

    show_description = schema.Bool(
        title=_(u'Show result description'),
        description=_(u'If selected, show a excerpt of the description'),
        default=False,
    )

    allow_rss_subscription = schema.Bool(
        title=_(u'Allow RSS subscription'),
        description=_(u'If selected, show an RSS icon in the title'),
        default=True,
    )

    show_more_results = schema.Bool(
        title=_(u'Show link for more results'),
        description=_(
            u'Show a link in the portlet footer to show more results'),
        default=True
    )

    assigned_column = schema.Choice(
        title=_(u'Column where the portlet is rendered'),
        description=_(u'Assign the portlet to a fixed column. Otherwise '
                      u'multisearch will try to balance the result portlets '
                      u'to fill up the page the portlet is assigned to a '
                      u'particular column'),
        required=True,
        vocabulary=columnVocabulary
    )

    show_if_no_results = schema.Bool(
        title=_(u'Show portlet even if no results are returned.'),
        description=_(u'The portlet shows a message '
                      u'that no results were found. Default behaviour is '
                      u'to remove the portlet from the page results'),
        required=False,
        default=True
    )


class Assignment(base.Assignment):
    implements(ILocalSearchPortlet)

    def __init__(self,
                 dtitle='',
                 results_number=5,
                 show_more_results=True,
                 show_description=False,
                 allow_rss_subscription=True,
                 assigned_column=0,
                 show_if_no_results=True):
        if not dtitle:
            dtitle = _('Local results')

        self.dtitle = dtitle
        self.show_more_results = show_more_results
        self.show_description = show_description
        self.allow_rss_subscription = allow_rss_subscription
        self.results_number = results_number
        self.assigned_column = assigned_column
        self.show_if_no_results = show_if_no_results

    @property
    def title(self):
        return self.dtitle


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/results_portlet.pt')

    @property
    def has_results(self):
        return len(self.results()) > 0

    @property
    def available(self):
        if self.has_results:
            return True

        return self.data.show_if_no_results

    @property
    def lines_count(self):
        """ Count the number of lines displayed.
        Basically, the number of results + the number of
        available short description.
        Return 1 when there is no results (in order to take
        the header into account).
        """
        results = self.results()
        if not results:
            return 1

        count = 0
        for res in results:
            count += 1
            if res['s_desc']:
                count += 1

        return count

    def extra_results_link(self):
        # Note that this link is only shown if there are results, so
        # it is never needed to return an empty string like in the
        # rss_link method.
        query = self.request.get('SearchableText', '')
        return '%s/search?SearchableText=%s' % (
            self.context.absolute_url(),
            quote_plus(query))

    def rss_link(self):
        query = self.request.get('SearchableText', None)
        if query is None:
            return ''
        return '%s/search_rss?SearchableText=%s' % (
            self.context.absolute_url(),
            quote_plus(query))

    def show_more_results(self):
        return self.data.show_more_results and self.has_results

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

    def make_excerpt(self, desc):
        if not self.data.show_description or not desc:
            return
        max_length = getattr(self, 'max_length', CHARACTERS_PER_LINE)
        return make_excerpt(desc, max_length)

    def results(self):
        if not hasattr(self, '_results'):
            results = self.make_results()
            for res in results:
                res['s_desc'] = self.make_excerpt(res.get('desc', ''))

            self._results = results

        return self._results


class AddForm(base.AddForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Add Local Search Portlet"

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ILocalSearchPortlet)
    label = "Edit Local Search Portlet"
