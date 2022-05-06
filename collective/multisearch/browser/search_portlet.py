from collective.multisearch import MultiSearchMessageFactory as _
from plone.app.portlets.portlets import search
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class ISearchPortlet(search.ISearchPortlet):
    pass


@implementer(ISearchPortlet)
class Assignment(search.Assignment):
    @property
    def title(self):
        return _(u"MultiSearch")


class Renderer(search.Renderer):
    render = ViewPageTemplateFile("templates/search_portlet.pt")

    def search_action(self):
        return "%s/@@multisearch" % self.navigation_root_url


class AddForm(search.AddForm):
    def create(self, data):
        return Assignment()


class EditForm(search.EditForm):
    pass
