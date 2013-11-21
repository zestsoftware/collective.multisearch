Changelog
=========

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
