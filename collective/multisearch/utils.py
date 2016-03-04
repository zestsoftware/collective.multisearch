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


def make_excerpt(text, max_length, ellipsis=None):
    """ Makes a clean cut in words.

    If the max length is longer than the text itself, nothing changes:
    >>> make_excerpt('Hello world', 100)
    'Hello world'

    It does not cut in the middle of words but uses spaces and dots.
    >>> make_excerpt('Hello world', 7)
    'Hello&hellip;'

    >>> make_excerpt('Hello world. How are you ?', 17)
    'Hello world. How&hellip;'

    >>> make_excerpt('Hello world. How are you ?', 12)
    'Hello world.'

    If the last space is only a space added after a dot, we split on the dot:
    >>> make_excerpt('Hello world. How are you ?', 15)
    'Hello world.'

    The only case when a word is cut is when it's a single word longer
    than the max length:
    >>> make_excerpt('Hello world. How are you ?', 4)
    'Hell&hellip;'
    """
    if ellipsis is None:
        ellipsis = '&hellip;'

    if len(text) <= max_length:
        return text

    short = text[:max_length]

    dot_split = short.split('.')
    space_split = short.split(' ')

    if len(dot_split) == len(space_split) == 1:
        # Well, no dots not spaces in the description,
        # should be a single word.
        return '%s%s' % (short, ellipsis)

    if len(dot_split[-1]) > len(space_split[-1]):
        # As spaces are generally added just after the dots,
        # we check we're not i that case.
        if dot_split[-1] == ' %s' % space_split[-1]:
            return '%s.' % '.'.join(dot_split[:-1])

        # There's a space after the last dot.
        return '%s%s' % (
            ' '.join(space_split[:-1]),
            ellipsis)

    return '%s.' % '.'.join(dot_split[:-1])


def assign_columns(portlets, column_count):
    """ Takes a list of tuples (Assignment, Renderer) and
    returns a list of lists with the Renderer output.

    Let's do a bit of mockup for testing.

    >>> class Assignment(object):
    ...     def __init__(self, assigned_column):
    ...         self.assigned_column = assigned_column

    >>> class Renderer(object):
    ...     def __init__(self, res_count, desc_count=0):
    ...         self.res_count = res_count
    ...         self.desc_count = desc_count
    ...         self.lines_count = res_count + desc_count
    ...         if self.lines_count == 0:
    ...             self.lines_count = 1
    ...     def results(self):
    ...         return [x for x in range(0, self.res_count)]
    ...     def __repr__(self):
    ...         return '<Renderer: %s results%s>' % (
    ...             self.res_count,
    ...             ' (%s descs)' % self.desc_count if self.desc_count else '')

    If there's no floating column, it will no try doing any balancing:
    >>> assign_columns([(Assignment(1), Renderer(10)),
    ...                 (Assignment(2), Renderer(1))], 2)
    [[<Renderer: 10 results>], [<Renderer: 1 results>]]

    The system tries to obtain the best possible result to have the same number of results
    in every column:
    >>> assign_columns([(Assignment(1), Renderer(10)),
    ...                 (Assignment(2), Renderer(1)),
    ...                 (Assignment(0), Renderer(5))], 2)
    [[<Renderer: 10 results>],
     [<Renderer: 1 results>, <Renderer: 5 results>]]

    >>> assign_columns([(Assignment(1), Renderer(10)),
    ...                 (Assignment(2), Renderer(1)),
    ...                 (Assignment(0), Renderer(15)),
    ...                 (Assignment(0), Renderer(5)),
    ...                 (Assignment(0), Renderer(5))], 2)
    [[<Renderer: 10 results>, <Renderer: 5 results>, <Renderer: 5 results>],
     [<Renderer: 1 results>, <Renderer: 15 results>]]

    If a portlet has no results but it still shown, it is considered has having one
    result (otherwise they'll all be stacked in the same column.
    >>> assign_columns([(Assignment(2), Renderer(1)),
    ...                 (Assignment(0), Renderer(0)),
    ...                 (Assignment(0), Renderer(0)),
    ...                 (Assignment(0), Renderer(0))], 2)
    [[<Renderer: 0 results>, <Renderer: 0 results>],
     [<Renderer: 1 results>, <Renderer: 0 results>]]


    As we base the balancing on the 'line_count' property (and not only the results),
    there might be less results in one column but have equivalent sizes.

    First without descriptions:
    >>> assign_columns([(Assignment(0), Renderer(10)),
    ...                 (Assignment(0), Renderer(10)),
    ...                 (Assignment(0), Renderer(5)),
    ...                 (Assignment(0), Renderer(5))], 2)
    [[<Renderer: 10 results>, <Renderer: 5 results>],
     [<Renderer: 10 results>, <Renderer: 5 results>]]

    Now one column has some descriptions shown:
    >>> assign_columns([(Assignment(0), Renderer(10)),
    ...                 (Assignment(0), Renderer(10, desc_count=10)),
    ...                 (Assignment(0), Renderer(5)),
    ...                 (Assignment(0), Renderer(5))], 2)
    [[<Renderer: 10 results (10 descs)>],
     [<Renderer: 10 results>, <Renderer: 5 results>, <Renderer: 5 results>]]

    """
    columns = dict([(index, []) for index in
                    range(0, column_count + 1)])

    for assignment, renderer in portlets:
        assignment_column = max(
            0, min(assignment.assigned_column, column_count))
        columns[assignment_column].append(renderer)

    if columns[0]:
        # We need to place the portlets in the existing columns.
        # First we sort them by size.
        unplaced = sorted(
            [(renderer, renderer.lines_count)
             for renderer in columns[0]],
            key=lambda x: x[1],
            reverse=True)

        sizes = dict(
            [(index, sum([renderer.lines_count
                          for renderer in columns[index]]))
             for index in columns.keys() if index])

        for portlet, p_size in unplaced:
            col_index = sorted(sizes.items(),
                               key=lambda x: x[1])[0][0]

            columns[col_index].append(portlet)
            sizes[col_index] += p_size

    return [columns[index] for index in sorted(columns.keys()) if index]
