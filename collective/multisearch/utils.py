from .config import DEFAULT_COLUMN
from .interfaces import IMultisearchSettings
from plone import api
from six.moves import range


def get_column_number():
    return api.portal.get_registry_record(name="collective.multisearch.column_number")


def set_column_number(value):
    return api.portal.set_registry_record(
        name="collective.multisearch.column_number", value=value
    )


def make_excerpt(text, max_length, ellipsis=None):
    """Makes a clean cut in words."""
    if ellipsis is None:
        ellipsis = "&hellip;"

    if len(text) <= max_length:
        return text

    short = text[:max_length]

    dot_split = short.split(".")
    space_split = short.split(" ")

    if len(dot_split) == len(space_split) == 1:
        # Well, no dots not spaces in the description,
        # should be a single word.
        return "%s%s" % (short, ellipsis)

    if len(dot_split[-1]) > len(space_split[-1]):
        # As spaces are generally added just after the dots,
        # we check we're not i that case.
        if dot_split[-1] == " %s" % space_split[-1]:
            return "%s." % ".".join(dot_split[:-1])

        # There's a space after the last dot.
        return "%s%s" % (" ".join(space_split[:-1]), ellipsis)

    return "%s." % ".".join(dot_split[:-1])


def assign_columns(portlets, column_count):
    """Turn portlets and column counts into a list of renderers.

    Input is a list of tuples (Assignment, Renderer), plus a column count.
    Currently the UI only supports a column count of 1 or 2.

    It returns a list of lists with the Renderers per column.
    """
    columns = dict([(index, []) for index in range(0, column_count + 1)])

    for assignment, renderer in portlets:
        assignment_column = max(0, min(assignment.assigned_column, column_count))
        columns[assignment_column].append(renderer)

    if columns[0]:
        # We need to place the portlets in the existing columns.
        # First we sort them by size.
        unplaced = sorted(
            [(renderer, renderer.lines_count) for renderer in columns[0]],
            key=lambda x: x[1],
            reverse=True,
        )

        sizes = dict(
            [
                (index, sum([renderer.lines_count for renderer in columns[index]]))
                for index in columns.keys()
                if index
            ]
        )

        for portlet, p_size in unplaced:
            col_index = sorted(list(sizes.items()), key=lambda x: x[1])[0][0]

            columns[col_index].append(portlet)
            sizes[col_index] += p_size

    return [columns[index] for index in sorted(columns.keys()) if index]
