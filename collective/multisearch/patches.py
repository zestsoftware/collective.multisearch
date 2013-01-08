from zope.component import getMultiAdapter
from plone.app.portlets.browser.manage import ManageContextualPortlets

def set_blacklist_status(self, manager, group_status, content_type_status, context_status):
    self.old_set_blacklist_status(manager, group_status, content_type_status, context_status)

    if manager == 'multisearch.MultisearchPortletManager':
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        self.request.response.redirect(baseUrl + '/@@multisearch')

    return ''

def patch_redirection():
    ManageContextualPortlets.old_set_blacklist_status = ManageContextualPortlets.set_blacklist_status
    ManageContextualPortlets.set_blacklist_status = set_blacklist_status

def unpatch_redirection():
    ManageContextualPortlets.set_blacklist_status = ManageContextualPortlets.old_set_blacklist_status

def apply_all():
    patch_redirection()
