# Remote search portlet
import logging
import feedparser
import urllib2
from  urllib import quote_plus

from plone.app.portlets.portlets import base
from zope import schema
from zope.formlib import form
from zope.interface import implements

from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.browser import portlet_local_search

logger = logging.getLogger('collective.multisearch.browser.portlet_remote_search')


class IRemoteSearchPortlet(portlet_local_search.ILocalSearchPortlet):
    remote_site_url = schema.TextLine(
        title=_(u'Remote site URL'),
        description=_(u'URL of the site were the search is performed '
                      '(http://www.example.com)'),
        required=True)

    remote_site_search_url = schema.TextLine(
        title=_(u'Remote site search page'),
        description=_(u'You can specify here a custom search page. If left blank, '
                      'it will use the address of the remote site and append /search '
                      '(http://www.example.com/search?SearchableText=%s with the previous '
                      'example, note the %s part that allows to copy the searched text.)'),
        required = False)


class Assignment(portlet_local_search.Assignment):
    implements(IRemoteSearchPortlet)

    def __init__(self,
                 dtitle='',
                 results_number=5,
                 show_more_results=True,
                 show_description=False,
                 allow_rss_subscription=True,
                 assigned_column=0,
                 show_if_no_results=True,
                 remote_site_url='',
                 remote_site_search_url=''):

        if not dtitle:
            dtitle = 'Remote results for: %s' % remote_site_url

        super(Assignment, self).__init__(
            dtitle, results_number, show_more_results, assigned_column, show_if_no_results)
        self.remote_site_url = remote_site_url
        self.remote_site_search_url = remote_site_search_url


class Renderer(portlet_local_search.Renderer):

    def extra_results_link(self):
        query = self.request.get('SearchableText', None)

        if self.data.remote_site_search_url:
            return self.data.remote_site_search_url % query

        return '%s/search?SearchableText=%s' % (
            self.data.remote_site_url,
            quote_plus(query))

    def rss_link(self):
        query = self.request.get('SearchableText', None)
        if query is None:
            return None

        return '%s/search_rss?SearchableText=%s' % (
            self.data.remote_site_url,
            quote_plus(query))

    def make_results(self):
        query = self.request.get('SearchableText', None)
        if not query:
            return []

        search_url = '%s/search_rss?SearchableText=%s' % (
            self.data.remote_site_url,
            quote_plus(query))

        try:
            rss = urllib2.urlopen(search_url).read()
        except urllib2.URLError:
            logger.info('Unable to open rss feed: %s' % search_url)
            return []

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
