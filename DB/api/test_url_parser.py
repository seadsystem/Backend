#!/usr/bin/env python3

import url_parser
import unittest

class TestURLParsing(unittest.TestCase):

	def setUp(self):
		self.query_options = {
			'device_id': None,
			'start_time': None,
			'end_time': None,
			'subset': None,
			"limit": None,
			"json": False,
			"reverse": False,
			"device": None,
			"diff": False,
			"total_energy": False,
			"list_format": None,
			"granularity": None,
			"events": None
		}

	def test_missing_device_id(self):
		try:
			url_parser.parse('http://db.sead.systems:8080/')
			self.assertFail()
		except Exception as e:
			self.assertEqual(str(e), "Not Found")

	def test_device_id(self):
		self.query_options['device_id'] = 466419817
		self.assertEqual(
			self.query_options,
			url_parser.parse('http://db.sead.systems:8080/466419817')
		)

	def test_total_energy(self):
		self.query_options['device_id'] = 466419818
		self.query_options['total_energy'] = True
		self.assertEqual(
			self.query_options,
			url_parser.parse('http://db.sead.systems:8080/466419818/total_energy')
		)

	def test_boolean_parameters(self):
		self.query_options['device_id'] = 466419819
		self.query_options['json'] = True
		self.query_options['reverse'] = True
		self.query_options['classify'] = True
		self.query_options['diff'] = True
		self.assertEqual(
			self.query_options,
			url_parser.parse(
				'http://db.sead.systems:8080/466419819?json=%20&reverse=2&classify=0&diff=foo'
			)
		)

	def test_string_parameters(self):
		self.query_options['device_id'] = 466419820
		self.query_options['type'] = 'foo'
		self.query_options['device'] = '0'
		self.query_options['list_format'] = ' '
		self.assertEqual(
			self.query_options,
			url_parser.parse(
				'http://db.sead.systems:8080/466419820?type=foo&device=0&list_format=%20'
			)
		)

	def test_int_parameters(self):
		self.query_options['device_id'] = 466419821
		self.query_options['start_time'] = 0
		self.query_options['end_time'] = -1
		self.query_options['subset'] = 1
		self.query_options['limit'] = 468
		self.query_options['granularity'] = -957
		self.assertEqual(
			self.query_options,
			url_parser.parse(
				'http://db.sead.systems:8080/466419821?start_time=0&end_time=-1&subset=1&limit=468&granularity=-957'
			)
		)

	def test_float_parameters(self):
		self.query_options['device_id'] = 466419822
		self.query_options['events'] = 15.4
		self.assertEqual(
			self.query_options,
			url_parser.parse(
				'http://db.sead.systems:8080/466419822?events=15.4'
			)
		)

if __name__ == '__main__':
	unittest.main()
