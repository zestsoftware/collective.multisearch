from Products.CMFCore.utils import getToolByName

from collective.multisearch.config import DEFAULT_COLUMN


def get_column_number(context):
    pprops = getToolByName(context,
                           'portal_properties',
                           None)
    if pprops is None:
        return DEFAULT_COLUMN

    if 'multisearch_properties' not in pprops.keys():
        pprops.addPropertySheet('multisearch_properties')

    ms_props = pprops.get('multisearch_properties')

    if not ms_props.hasProperty('column_number'):
        ms_props._setProperty('column_number', DEFAULT_COLUMN, 'int')

    return ms_props.get('column_number', DEFAULT_COLUMN)
