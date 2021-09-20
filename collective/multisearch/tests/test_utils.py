import unittest


class Assignment(object):
    def __init__(self, assigned_column):
        self.assigned_column = assigned_column


class Renderer(object):
    def __init__(self, res_count, desc_count=0):
        self.res_count = res_count
        self.desc_count = desc_count
        self.lines_count = res_count + desc_count
        if self.lines_count == 0:
            self.lines_count = 1

    def results(self):
        return [x for x in range(0, self.res_count)]

    def __repr__(self):
        return "<Renderer: %s results%s>" % (
            self.res_count,
            " (%s descs)" % self.desc_count if self.desc_count else "",
        )


class UnitTest(unittest.TestCase):
    def test_make_excerpt(self):
        from collective.multisearch.utils import make_excerpt

        # If the max length is longer than the text itself, nothing changes:
        self.assertEqual(make_excerpt("Hello world", 100), "Hello world")

        # It does not cut in the middle of words but uses spaces and dots.
        self.assertEqual(make_excerpt("Hello world", 7), "Hello&hellip;")
        self.assertEqual(
            make_excerpt("Hello world. How are you ?", 17), "Hello world. How&hellip;"
        )
        self.assertEqual(make_excerpt("Hello world. How are you ?", 12), "Hello world.")

        # If the last space is only a space added after a dot, we split on the dot:
        self.assertEqual(make_excerpt("Hello world. How are you ?", 15), "Hello world.")

        # The only case when a word is cut is when it's a single word longer
        # than the max length:
        self.assertEqual(make_excerpt("Hello world. How are you ?", 4), "Hell&hellip;")

    def _assigned_columns_output(self, portlets, column_count):
        from collective.multisearch.utils import assign_columns

        columns = []
        for col in assign_columns(portlets, column_count):
            output = [str(renderer) for renderer in col]
            columns.append(output)
        return columns

    def test_assign_columns(self):
        # Takes a list of tuples (Assignment, Renderer) and
        # returns a list of lists with the Renderers.

        # If there's no floating column, it will not try doing any balancing:
        self.assertEqual(
            self._assigned_columns_output(
                [(Assignment(1), Renderer(10)), (Assignment(2), Renderer(1))], 2
            ),
            [["<Renderer: 10 results>"], ["<Renderer: 1 results>"]],
        )

        # The system tries to obtain the best possible result to have the same number of results
        # in every column:
        self.assertEqual(
            self._assigned_columns_output(
                [
                    (Assignment(1), Renderer(10)),
                    (Assignment(2), Renderer(1)),
                    (Assignment(0), Renderer(5)),
                ],
                2,
            ),
            [
                ["<Renderer: 10 results>"],
                ["<Renderer: 1 results>", "<Renderer: 5 results>"],
            ],
        )

        self.assertEqual(
            self._assigned_columns_output(
                [
                    (Assignment(1), Renderer(10)),
                    (Assignment(2), Renderer(1)),
                    (Assignment(0), Renderer(15)),
                    (Assignment(0), Renderer(5)),
                    (Assignment(0), Renderer(5)),
                ],
                2,
            ),
            [
                [
                    "<Renderer: 10 results>",
                    "<Renderer: 5 results>",
                    "<Renderer: 5 results>",
                ],
                ["<Renderer: 1 results>", "<Renderer: 15 results>"],
            ],
        )

        # If a portlet has no results but it still shown, it is considered has having one
        # result (otherwise they'll all be stacked in the same column.
        self.assertEqual(
            self._assigned_columns_output(
                [
                    (Assignment(2), Renderer(1)),
                    (Assignment(0), Renderer(0)),
                    (Assignment(0), Renderer(0)),
                    (Assignment(0), Renderer(0)),
                ],
                2,
            ),
            [
                ["<Renderer: 0 results>", "<Renderer: 0 results>"],
                ["<Renderer: 1 results>", "<Renderer: 0 results>"],
            ],
        )

        # As we base the balancing on the 'line_count' property (and not only the results),
        # there might be less results in one column but have equivalent sizes.

        # First without descriptions:
        self.assertEqual(
            self._assigned_columns_output(
                [
                    (Assignment(0), Renderer(10)),
                    (Assignment(0), Renderer(10)),
                    (Assignment(0), Renderer(5)),
                    (Assignment(0), Renderer(5)),
                ],
                2,
            ),
            [
                ["<Renderer: 10 results>", "<Renderer: 5 results>"],
                ["<Renderer: 10 results>", "<Renderer: 5 results>"],
            ],
        )

        # Now one column has some descriptions shown:
        self.assertEqual(
            self._assigned_columns_output(
                [
                    (Assignment(0), Renderer(10)),
                    (Assignment(0), Renderer(10, desc_count=10)),
                    (Assignment(0), Renderer(5)),
                    (Assignment(0), Renderer(5)),
                ],
                2,
            ),
            [
                ["<Renderer: 10 results (10 descs)>"],
                [
                    "<Renderer: 10 results>",
                    "<Renderer: 5 results>",
                    "<Renderer: 5 results>",
                ],
            ],
        )
