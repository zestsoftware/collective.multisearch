# Custom manager for the multisearch portlet manager: inactive for the moment.

from AccessControl import Unauthorized
from BTrees.OOBTree import OOBTree
from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.browser.interfaces import (
    IMultiSearchPortletAssignmentMapping,
)
from collective.multisearch.browser.interfaces import IMultisearchPortletManager
from collective.multisearch.browser.interfaces import IMultiSearchPortletManagerRenderer
from collective.multisearch.config import COLUMN_COUNT
from collective.multisearch.config import DEFAULT_COLUMN
from collective.multisearch.utils import get_column_number
from collective.multisearch.utils import set_column_number
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.manage import ManageContextualPortlets
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager
from plone.protect.auto import safeWrite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from six.moves import range
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


@adapter(
    Interface,
    IDefaultBrowserLayer,
    IManageContextualPortletsView,
    IMultisearchPortletManager,
)
class MultiSearchContextualEditPortletManagerRenderer(
    ContextualEditPortletManagerRenderer
):
    template = ViewPageTemplateFile("templates/edit-manager-contextual.pt")

    def get_column_number(self):
        return {
            "current": get_column_number(),
            "available": list(range(1, COLUMN_COUNT + 1)),
        }

    def addable_portlets(self):
        """We can't do a normal 'super', so it's a copy/paste form the base class."""
        baseUrl = self.baseUrl()
        addviewbase = baseUrl.replace(self.context_url(), "")

        def sort_key(v):
            return v.get("title")

        def check_permission(p):
            addview = p.addview
            if not addview:
                return False

            # We only use portlets that are specifically
            # designed for this manager.
            if IMultisearchPortletManager not in p.for_:
                return False

            addview = "%s/+/%s" % (
                addviewbase,
                addview,
            )
            if addview.startswith("/"):
                addview = addview[1:]
            try:
                self.context.restrictedTraverse(str(addview))
            except (
                AttributeError,
                KeyError,
                Unauthorized,
            ):
                return False
            return True

        portlets = [
            {
                "title": p.title,
                "description": p.description,
                "addview": "%s/+/%s" % (addviewbase, p.addview),
            }
            for p in self.manager.getAddablePortletTypes()
            if check_permission(p)
        ]

        portlets.sort(key=sort_key)
        return portlets


class MultiSearchManagerContextualPortlets(ManageContextualPortlets):
    def get_manager(self):
        editmanager = queryMultiAdapter(
            (self.context, self.request, self),
            IMultiSearchPortletManagerRenderer,
            "multisearch.MultisearchPortletManager",
        )

        editmanager.update()
        return editmanager.render()

    def getAssignmentsForManager(self, manager):
        assignments = getMultiAdapter(
            (self.context, manager), IMultiSearchPortletAssignmentMapping
        )
        return list(assignments.values())

    def __call__(self):
        if self.request.get("REQUEST_METHOD") != "POST":
            return self.index()

        try:
            column_count = int(self.request.form.get("column_count", DEFAULT_COLUMN))
            set_column_number(column_count)
            IStatusMessage(self.request).addStatusMessage(
                _("Properties updated"), "info"
            )
            return self.request.response.redirect("@@multisearch")
        except Exception:
            IStatusMessage(self.request).addStatusMessage(
                _("Invalid value for column number"), "error"
            )

        return self.index()


@implementer(IMultiSearchPortletAssignmentMapping)
class MultiSearchPortletAssignmentMapping(PortletAssignmentMapping):
    pass


@adapter(ILocalPortletAssignable, IPortletManager)
@implementer(IMultiSearchPortletAssignmentMapping)
def localPortletAssignmentMappingAdapter(context, manager):
    """When adapting (context, manager), get an IPortletAssignmentMapping
    by finding one in the object's annotations. The container will be created
    if necessary.
    """
    if IAnnotations.providedBy(context):
        annotations = context
    else:
        annotations = queryAdapter(context, IAnnotations)
    local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
    if local is None:
        local = annotations[CONTEXT_ASSIGNMENT_KEY] = OOBTree()
        # Prevent plone.protect phishing warning for new tree.
        safeWrite(local)
    portlets = local.get(manager.__name__, None)
    if portlets is None or not IMultiSearchPortletAssignmentMapping.providedBy(
        portlets
    ):
        if portlets is not None:
            old_items = list(portlets.items())
        else:
            old_items = []
        portlets = local[manager.__name__] = MultiSearchPortletAssignmentMapping(
            manager=manager.__name__, category=CONTEXT_CATEGORY
        )
        # Inline migration.  Might be good in an upgrade step.
        for key, value in old_items:
            portlets[key] = value
        # Prevent plone.protect phishing warning for changed tree.
        safeWrite(local)

    return portlets
