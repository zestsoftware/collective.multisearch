Changelog
=========

2.0.0a2 (2022-05-06)
--------------------

- Register a bundle in the resource registry instead of using portal_css.  [maurits]

- Use the configuration registry instead of portal_properties.  [maurits]

- Fixed zope.component ImportErrors in Plone 6.  [maurits]


2.0.0a1 (2021-09-20)
--------------------

- Updated to Plone 5.2 and Python 2/3.
  TODO: load css, and replace portal_properties use with registry.
  [maurits]


1.3 (2018-03-09)
----------------

- Catch socket errors when requesting a remote search source. If we don't the
  whole search results page fails with an error/traceback. [fredvd]


1.2 (2016-12-23)
----------------

- Don't double urlquote the parameters in the link to more search results in
  the local search portlet. [fredvd]


1.1 (2016-04-11)
----------------

- Add uninstall profile. Doesn't remove portlet assignments yet.
  [fredvd]

- Bring search results page more in line with Plone 4.3 html/css. Default
  view should already be reasonable.
  [fredvd]

- Add viewlets.xml ordering that hides the default plone.searchbox viewlet and
  adds the collective.multisearch widget on the same location (no upgrade step
  on purpose, installed base should be fine and already have catered for this)
  [fredvd]

- Add browserlayer for add'on installed and register the viewlets/views on this
  specific layer so we don't pollute the site when nothing is installed.
  [fredvd]

- Always disable liveview on multisearch viewlet.
  [fredvd]

- Remove dependency on five.grok.
  [fredvd]

- Add verify_ssl option to remote search portlet to disable ssl certificate
  validation when you have to query a 'secure' internal site over firewalls
  that ruin the certificate chain.
  [fredvd]

- Give validation error when inputting a search url without ``%s``.
  [maurits]

- Catch "TypeError: not all arguments converted during string
  formatting" when the ``remote_site_search_url`` or the
  ``remote_site_search_rss_url`` does not contain a ``%s``.
  [maurits]

- Added PloneTestCase to test requirements.
  [maurits]


1.0.3 (2013-11-21)
------------------

- Don't crash the remote search portlet if a feed item does not contain a
  summary field. Happens when reading search results from a Plone 3.3.X site.
  [f.vandijk]


1.0.2 (2013-11-21)
------------------

- Add field ``remote_site_search_rss_url`` so you can set an explicit
  rss url that we use for querying the remote site, instead of
  appending a hardcoded ``search_rss`` to the site url.  This means we
  support non-Plone sites now.
  [maurits]

- Set the User-Agent string to 'Mozilla/4.0' when querying remote
  servers.  Otherwise, some bad servers return a 403 Forbidden error.
  [maurits]

- Add timeout value for remote RSS portlet searches. Default is 5 seconds.
  [fredvd]

- Load the zcml of some packages so Plone starts up correctly.
  [maurits]


1.0.1 (2013-03-27)
------------------

- Removed our ManagePortletAssignments override.  It was meant for
  returning to the correct url (``@@manage-multisearch``) after
  changing a portlet, but it had an error so it did not work.  Also,
  it is not needed anymore after plone.app.portlets 2.4.3 is released.
  [maurits]


1.0 (2013-03-11)
----------------

- Initial public release
