#!/usr/bin/env python
# # -*- coding: utf-8 -*- 

# test_username.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Tests that username validation returns errors for unsupported characters
#

import unittest

import sys
sys.path.insert(1, '..')

from kano_init.tasks.flow import _validate_username

class TestUsername(unittest.TestCase):

    def test_username_empty(self):
        name, msg = _validate_username('')
        self.assertIsNotNone(msg)

    def test_username_n_with_tilde(self):
        name, msg = _validate_username('Iñaki')
        self.assertIsNotNone(msg)
                
    def test_username_with_accents(self):
        name, msg = _validate_username('José')
        self.assertIsNotNone(msg)
        name, msg = _validate_username('Mercè')
        self.assertIsNotNone(msg)

    def test_username_with_spaces(self):
        name, msg = _validate_username('Carlos Espacio')
        self.assertIsNone(msg, msg=msg)
        self.assertEqual(name, 'CarlosEspacio')

    def test_username_with_commas(self):
        name, msg = _validate_username('Esth,er')
        self.assertIsNotNone(msg, msg=msg)
        name, msg = _validate_username(',Francesc')
        self.assertIsNotNone(msg, msg=msg)
        name, msg = _validate_username(',Mathias,')
        self.assertIsNotNone(msg, msg=msg)

if __name__ == '__main__':
    unittest.main()
