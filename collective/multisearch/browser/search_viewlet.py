from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common


class SearchBoxViewlet(common.SearchBoxViewlet):
    index = ViewPageTemplateFile('templates/searchbox_viewlet.pt')

    def update(self):
        super(SearchBoxViewlet, self).update()

        # Disable live search as we don't know the sources yet
        self.search_input_id = "nolivesearchGadget" # don't use "" here!
        