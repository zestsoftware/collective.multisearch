# Remote search portlet

import feedparser
from  urllib import quote_plus
from  urllib2 import urlopen

from zope import schema
from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base

from collective.multisearch import MultiSearchMessageFactory as _

class IRemoteSearchPortlet(IPortletDataProvider):
    remote_site_url = schema.TextLine(
        title=_('Remote site URL'),
        required=True)

    results_number = schema.Int(
        title=_('Number of results displayed'),
        required=True,
        default=5)

    show_more_results = schema.Bool(
        title=_('Show link for more results'),
        default=True
        )


class Assignment(base.Assignment):
    implements(IRemoteSearchPortlet)

    def __init__(self,
                 remote_site_url='',
                 results_number=5,
                 show_more_results=True):
        self.remote_site_url = remote_site_url
        self.show_more_results = show_more_results
        self.results_number = results_number

    @property
    def title(self):
        return _(u"Remote search")

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/remote_search.pt')

    @property
    def extra_results_link(self):
        query = self.request.get('SearchableText', None)

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
        return Assignment(
            remote_site_url=data.get('remote_site_url'),
            results_number=data.get('results_number'),
            show_more_results=data.get('show_more_results'))

class EditForm(base.EditForm):
    form_fields = form.Fields(IRemoteSearchPortlet)
    label = "Edit Remote Search Portlet"
