# Remote search portlet
import logging
import feedparser
import socket

import urllib2
from urllib import quote_plus

import ssl

from plone.app.portlets.portlets import base
from zope import schema
from zope.formlib import form
from zope.interface import implements

from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.browser import portlet_local_search
from collective.multisearch.config import RSS_TIMEOUT
logger = logging.getLogger(
    'collective.multisearch.browser.portlet_remote_search')


class InvalidTimeoutValue(schema.ValidationError):
    __doc__ = _(u'Please enter a timeout between 1 and 60 seconds.')


def isValidTimeout(value):
    """check for a value between 1 and 60 seconds"""
    if 0 < int(value) < 61:
        return True
    else:
        raise InvalidTimeoutValue


class InvalidSearchUrl(schema.ValidationError):
    __doc__ = _(u"Please enter a url with '%s' in it.")


def isValidSearchUrl(value):
    """Must have %s in it."""
    if value and '%s' not in value:
        raise InvalidSearchUrl
    return True


class IRemoteSearchPortlet(portlet_local_search.ILocalSearchPortlet):
    remote_site_url = schema.TextLine(
        title=_(u'Remote site URL'),
        description=_(u'URL of the site were the search is performed '
                      '(http://www.example.com)'),
        required=True)

    remote_site_search_url = schema.TextLine(
        title=_(u'Remote site search page'),
        description=_(
            u"You can specify here a custom search page. This will be used as "
            "link to extra results. If left blank, it will use the address of "
            "the remote site and append '/search?SearchableText=%s', so "
            "http://www.example.com/search?SearchableText=%s with the "
            "previous example, which is good for a Plone site. Note the '%s' "
            "part where the searched text will be filled in."),
        constraint=isValidSearchUrl,
        required=False)

    remote_site_search_rss_url = schema.TextLine(
        title=_(u'Remote site search rss feed'),
        description=_(
            u"You can specify here a custom rss search feed. This will be "
            "used to fetch the search results. If left blank, it will use "
            "the address of the remote site and append "
            "'/search_rss?SearchableText=%s', so "
            "http://www.example.com/search_rss?SearchableText=%s with the "
            "previous example, which is good for a Plone site. Note the '%s' "
            "part where the searched text will be filled in."),
        constraint=isValidSearchUrl,
        required=False
    )

    rss_timeout = schema.Int(
        title=_(u'Request timeout'),
        description=_(
            u'Number of seconds before we timeout the remote search request.'),
        required=True,
        default=RSS_TIMEOUT,
        constraint=isValidTimeout
    )

    verify_ssl = schema.Bool(
        title=_(u'Verify https request certificates'),
        description=_(
            u'For https request: should we verify the certificates? Only disable '
            u'this if you know what you are doing.'),
        required=True,
        default=True
    )

class Assignment(portlet_local_search.Assignment):
    implements(IRemoteSearchPortlet)

    # Specifying a default here avoids problems viewing or editing older assignments:
    remote_site_search_rss_url = ''
    rss_timeout = RSS_TIMEOUT
    verify_ssl = True

    def __init__(self,
                 dtitle='',
                 results_number=5,
                 show_more_results=True,
                 show_description=False,
                 allow_rss_subscription=True,
                 assigned_column=0,
                 show_if_no_results=True,
                 remote_site_url='',
                 remote_site_search_url='',
                 remote_site_search_rss_url='',
                 verify_ssl=True,
                 rss_timeout=RSS_TIMEOUT):

        if not dtitle:
            dtitle = 'Remote results for: %s' % remote_site_url

        super(Assignment, self).__init__(
            dtitle, results_number, show_more_results, assigned_column, show_if_no_results)
        self.remote_site_url = remote_site_url
        self.remote_site_search_url = remote_site_search_url
        self.remote_site_search_rss_url = remote_site_search_rss_url
        self.verify_ssl = verify_ssl

class Renderer(portlet_local_search.Renderer):

    def extra_results_link(self):
        # Note that this link is only shown if there are results, so
        # it is never needed to return an empty string like in the
        # rss_link method.
        query = self.request.get('SearchableText', '')
        query = quote_plus(query)
        if self.data.remote_site_search_url:
            try:
                return self.data.remote_site_search_url % query
            except TypeError:
                logger.warn(
                    'Cannot insert query in remote_site_search_url %s',
                    self.data.remote_site_search_url)

        return '%s/search?SearchableText=%s' % (
            self.data.remote_site_url, query)

    def rss_link(self):
        query = self.request.get('SearchableText', None)
        if query is None:
            return ''
        query = quote_plus(query)

        if self.data.remote_site_search_rss_url:
            try:
                return self.data.remote_site_search_rss_url % query
            except TypeError:
                logger.warn(
                    'Cannot insert query in remote_site_search_rss_url %s',
                    self.data.remote_site_search_rss_url)

        return '%s/search_rss?SearchableText=%s' % (
            self.data.remote_site_url, query)

    def make_results(self):
        query = self.request.get('SearchableText', None)
        if not query:
            return []

        search_url = self.rss_link()
        if not search_url:
            return []

        # turn of ssl certificate checking if explicitly turned off in the
        # portlet settings: http://stackoverflow.com/questions/19268548

        verify_ssl = getattr(self.data, "verify_ssl", True)
        if not verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
        else:
            opener = urllib2.build_opener()
        request = urllib2.Request(search_url)
        # According to the 'curl' manual, some badly done CGIs fail if
        # the User-Agent field isn't set to "Mozilla/4.0".  I
        # [Maurits] have seen this in practice in one case, so let's
        # indeed set the User-Agent header.  Note that normally the
        # header is something like 'Python-urllib/2.7'.
        request.add_header('User-Agent', 'Mozilla/4.0')
        try:
            timeout = getattr(self.data, "rss_timeout", RSS_TIMEOUT)
            rss = opener.open(request, timeout=timeout).read()
        except socket.timeout as e:
            # only works in Python 2.7
            logger.info('RSS feed timeout after %s seconds: %s' %
                        (timeout, search_url))
            return []
        except urllib2.URLError as e:
            # works for Python 2.6
            if isinstance(e.reason, socket.timeout):
                logger.info('RSS feed timeout after %s seconds: %s' %
                            (timeout, search_url))
                return []
            logger.info('Unable to open RSS feed: %s' % search_url)
            return []

        data = feedparser.parse(rss)
        return [
            {'title': x['title'],
             'url': x['links'][0]['href'],
             'desc': getattr(x, 'summary', u'')}
            for x in data['items']][:self.data.results_number]


class AddForm(base.AddForm):
    form_fields = form.Fields(IRemoteSearchPortlet)
    label = "Add Remote Search Portlet"

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IRemoteSearchPortlet)
    label = "Edit Remote Search Portlet"
