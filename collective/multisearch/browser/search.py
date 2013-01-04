from five import grok

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

class MultiSearchView(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('multi_search')
    grok.require('zope2.View')
