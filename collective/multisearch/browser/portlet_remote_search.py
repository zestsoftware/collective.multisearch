# Remote search portlet

import feedparser
from  urllib import quote_plus
from  urllib2 import urlopen

from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base


from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.browser import portlet_local_search


class IRemoteSearchPortlet(portlet_local_search.ILocalSearchPortlet):
    remote_site_url = schema.TextLine(
        title=_('Remote site URL'),
        required=True)

    remote_site_search_url = schema.TextLine(
        title=_('Remote site search page'),
        required = False)


class Assignment(portlet_local_search.Assignment):
    implements(IRemoteSearchPortlet)

    def __init__(self,
                 dtitle = '',
                 remote_site_url='',
                 remote_site_search_url='',
                 results_number=5,
                 show_more_results=True):

        if not dtitle:
            dtitle = 'Remote results for: %s' % remote_site_url

        super(Assignment, self).__init__(dtitle, results_number, show_more_results)
        self.remote_site_url = remote_site_url
        self.remote_site_search_url = remote_site_search_url


class Renderer(portlet_local_search.Renderer):

    @property
    def extra_results_link(self):
        query = self.request.get('SearchableText', None)

        if self.data.remote_site_search_url:
            return self.data.remote_site_search_url % query
        
        return '%s/search?SearchableText=%s' % (
            self.data.remote_site_url,
            query)

    def results(self):
        query = self.request.get('SearchableText', None)
        if not query:
            return []

        search_url = '%s/search_rss?SearchableText=%s' % (
            self.data.remote_site_url,
            quote_plus(query))

        rss = urlopen(search_url).read()
        data = feedparser.parse(rss)

        return [
            {'title': x['title'],
             'url': x['links'][0]['href'],
             'desc': x['summary']}
            for x in data['items']][:self.data.results_number]


class AddForm(base.AddForm):
    form_fields = form.Fields(IRemoteSearchPortlet)
    label = "Add Remote Search Portlet"

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IRemoteSearchPortlet)
    label = "Edit Remote Search Portlet"