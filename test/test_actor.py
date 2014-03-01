from __future__ import unicode_literals
from datetime import datetime
from unittest import TestCase

from pygrit.actor import Actor


class TestActor(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # output
    def test_output_adds_tz_offset(self):
        t = datetime.now()
        a = Actor("A R", "ar@example.com")
        _ = a.output(t).split(" ")
        offset = _.pop()
        output = " ".join(_)
        self.assertEqual("A R <ar@example.com> {}".\
                         format(t.strftime("%s")), output)
        self.assertRegexpMatches(offset, r'-?\d{4}')

    # from_string
    def test_from_string_should_seperate_name_and_email(self):
        a = Actor.from_string("A R <ar@example.com>")
        self.assertEqual("A R", a.name)
        self.assertEqual("ar@example.com", a.email)

    # __repr__
    def test_repr(self):
        a = Actor.from_string("A R <ar@example.com>")
        self.assertEqual('#<pygrit.Actor "A R <ar@example.com>">', a.__repr__())

    # str()
    def test_to_s_should_alias_name(self):
        a = Actor.from_string("A R <ar@example.com>")
        self.assertEqual(a.name, str(a))
