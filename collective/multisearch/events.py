# More or less a copy/paste of plone.portlets.events except we use our
# custom interface for the PortletManagerRenderer.

from plone.portlets.interfaces import IPortletManager
from zope.component import adapter
from zope.component import subscribers
from zope.component.interfaces import IRegistered
from zope.component.interfaces import IRegistrationEvent
from zope.component.interfaces import IUnregistered
from zope.component.interfaces import IUtilityRegistration
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from collective.multisearch.browser.interfaces import IMultiSearchPortletManagerRenderer


@adapter(IUtilityRegistration, IRegistrationEvent)
def dispatchToComponent(registration, event):
    """When a utility is registered, dispatch to an event handler registered for
    the particular component registered, the registration and the event.
    """
    handlers = subscribers((registration.component, registration, event), None)
    for handler in handlers:
        pass  # getting them does the work


@adapter(IPortletManager, IUtilityRegistration, IRegistered)
def registerPortletManagerRenderer(manager, registration, event):
    """When a portlet manager is registered as a utility, make an appropriate
    adapter registration for its IPortletManagerRenderer so that the
    provider: expression can find it, and ensure the manager's __name__ is
    the same as the name of the utility, which will also be the name of the
    adapter.
    """
    if registration.name != 'multisearch.MultisearchPortletManager':
        return

    manager.__name__ = registration.name
    registry = registration.registry
    registry.registerAdapter(factory=manager,
                             required=(Interface, IBrowserRequest,
                                       IBrowserView),
                             provided=IMultiSearchPortletManagerRenderer,
                             name=registration.name)


@adapter(IPortletManager, IUtilityRegistration, IUnregistered)
def unregisterPortletManagerRenderer(manager, registration, event):
    """When a portlet manager is unregistered as a utility, unregister its
    IPortletManagerRenderer.
    """
    if registration.name != 'multisearch.MultisearchPortletManager':
        return

    registry = registration.registry
    registry.unregisterAdapter(factory=manager,
                               required=(Interface, IBrowserRequest,
                                         IBrowserView),
                               provided=IMultiSearchPortletManagerRenderer,
                               name=registration.name)
