from Products.CMFCore.utils import getToolByName

from collective.multisearch.config import DEFAULT_COLUMN

def get_ms_props(context):
    pprops = getToolByName(context,
                           'portal_properties',
                           None)
    if pprops is None:
        return DEFAULT_COLUMN

    if 'multisearch_properties' not in pprops.keys():
        pprops.addPropertySheet('multisearch_properties')

    return pprops.get('multisearch_properties')


def get_column_number(context):
    ms_props = get_ms_props(context)
    if not ms_props.hasProperty('column_number'):
        ms_props._setProperty('column_number', DEFAULT_COLUMN, 'int')

    return ms_props.column_number


def set_column_number(context, value):
    ms_props = get_ms_props(context)
    ms_props._setPropValue('column_number', value)
    
