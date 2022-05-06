from collective.multisearch import MultiSearchMessageFactory as _
from collective.multisearch.config import DEFAULT_COLUMN
from zope import schema
from zope.interface import Interface


class IAddOnInstalled(Interface):
    """A layer specific for this add-on product."""


class IMultisearchSettings(Interface):

    column_number = schema.Int(
        title=_("Number of columns"),
        description=_("Number of columns shown on the multisearch page."),
        default=DEFAULT_COLUMN,
        missing_value=DEFAULT_COLUMN,
        required=True,
    )
