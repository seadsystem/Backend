#!/usr/bin/env python3

import unittest
import query_db
import importlib
import Analysis_3
import detect_events


class TestQueryRouting(unittest.TestCase):

    def setUp(self):
        importlib.reload(query_db)
        importlib.reload(Analysis_3)
        importlib.reload(detect_events)

        # start_time = end_time = data_type = subset = limit = device = granularity = None
        # diff = json = reverse = classify = list_format = events = False
        # (device_id, start_time, end_time, data_type, subset, limit, reverse, device, diff, granularity, list_format)
        self.retrieve_args = [None, None, None, None, None, None, False, None, False, None, False]

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
            "total_energy": None,
            "list_format": False,
            "granularity": None,
            "events": None
        }

    def test_missing_device_id(self):
        try:
            query_db.query({})
            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), 'Received malformed URL data: missing device_id')

    def test_total_energy(self):
        query_db.generate_total_energy = lambda device_id, start_time, end_time, device: 157
        self.assertEqual(
            query_db.query({'device_id': 4, 'total_energy': True}),
            157
        )

    def retrieve_factory(self):
        def retrieve(*args):
            self.assertEqual(args, tuple(self.retrieve_args))
            return 'retrieve called'
        return retrieve

    def classify_factory(self):
        def classify(*args):
            self.assertEqual(args, ('retrieve called',))
            return 'classify called'
        return classify

    def format_list_factory(self, results, list_format):
        def format_list(*args):
            self.assertEqual(args, (results, list_format))
            return 'format_list called: ' + str(list_format)
        return format_list

    def detect_factory(self, events):
        def detect(*args):
            self.assertEqual(args, ('retrieve called', events))
            return 'detect called'
        return detect

    def format_data_factory(self, header, results, json):
        def format_data(*args):
            self.assertEqual(args, (header, results, json))
            return 'format_data called'
        return format_data

    def test_classify(self):
        self.query_options['device_id'] = 5
        self.retrieve_args[0] = 5

        self.query_options['classify'] = True

        self.query_options['start_time'] = 6
        self.retrieve_args[1] = 6

        self.query_options['end_time'] = 7
        self.retrieve_args[2] = 7
        
        query_db.retrieve_within_filters = self.retrieve_factory()
        Analysis_3.run = self.classify_factory()

        self.assertEqual(query_db.query(self.query_options), 'classify called')

    def test_classify_missing_start_end_time(self):
        self.query_options['device_id'] = 10
        self.retrieve_args[0] = 10

        self.query_options['classify'] = True

        query_db.retrieve_within_filters = self.retrieve_factory()
        try:
            query_db.query(self.query_options)
            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), 'Received malformed URL data: missing start_time and end_time')

    def test_events_and_diff_missing_parameters(self):
        self.query_options['device_id'] = 20
        self.retrieve_args[0] = 20

        self.query_options['events'] = True

        self.query_options['diff'] = True
        self.retrieve_args[8] = True

        query_db.retrieve_within_filters = self.retrieve_factory()
        try:
            query_db.query(self.query_options)
            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), 'Event detection requires device, start_time, end_time, data_type=P, and list_format=event')

    def test_events(self):
        self.query_options['device_id'] = 30
        self.retrieve_args[0] = 30

        self.query_options['events'] = True

        self.query_options['diff'] = True
        self.retrieve_args[8] = True

        self.query_options['start_time'] = 31
        self.retrieve_args[1] = 31

        self.query_options['end_time'] = 32
        self.retrieve_args[2] = 32

        self.query_options['type'] = 'P'
        self.retrieve_args[3] = 'P'

        self.query_options['list_format'] = 'event'
        self.retrieve_args[10] = 'event'

        self.query_options['device'] = 'baz'
        self.retrieve_args[7] = 'baz'

        query_db.retrieve_within_filters = self.retrieve_factory()
        detect_events.detect = self.detect_factory(True)
        query_db.format_list = self.format_list_factory('detect called', 'event')

        self.assertEqual(query_db.query(self.query_options), 'format_list called: event')

    def test_bare_format_list(self):
        self.query_options['device_id'] = 40
        self.retrieve_args[0] = 40

        self.query_options['start_time'] = 41
        self.retrieve_args[1] = 41

        self.query_options['end_time'] = 42
        self.retrieve_args[2] = 42

        self.query_options['type'] = 'T'
        self.retrieve_args[3] = 'T'

        self.query_options['list_format'] = True
        self.retrieve_args[10] = True

        self.query_options['device'] = 'bar'
        self.retrieve_args[7] = 'bar'

        query_db.retrieve_within_filters = self.retrieve_factory()
        query_db.format_list = self.format_list_factory('retrieve called', True)

        self.assertEqual(query_db.query(self.query_options), 'format_list called: True')

    def test_format_data(self):
        self.query_options['device_id'] = 50
        self.retrieve_args[0] = 50

        self.query_options['json'] = True

        query_db.retrieve_within_filters = self.retrieve_factory()
        query_db.format_list = self.format_list_factory('retrieve called', True)
        query_db.format_data = self.format_data_factory(['time', 'I', 'W', 'V', 'T'], 'retrieve called', True)

        self.assertEqual(query_db.query(self.query_options), 'format_data called')


class TestQueryGeneration(unittest.TestCase):

    def setUp(self):
        importlib.reload(query_db)

        # start_time = end_time = data_type = subset = limit = device = granularity = None
        # diff = json = reverse = classify = list_format = events = False
        # (device_id, start_time, end_time, data_type, subset, limit, reverse, device, diff, granularity, list_format)
        self.retrieve_args = [None, None, None, None, None, None, False, None, False, None, False]

    def format_list_factory(self, query, params):
        def perform_query(*args):
            self.assertEqual(args, (query, params))
            return 'perform_query called'
        return perform_query

    def test_device_id(self):
        # device_id
        self.retrieve_args[0] = 10

        query_db.perform_query = self.format_list_factory(
            "SELECT * FROM crosstab('SELECT time, type, data from data_raw as raw WHERE "\
            "serial = %s', 'SELECT unnest(ARRAY[''I'', ''W'', ''V'', ''T''])') AS "\
            "ct_result(time TIMESTAMP, I BIGINT, W BIGINT, V BIGINT, T BIGINT) ORDER BY "\
            "time DESC;",
            (10,)
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_data_type(self):
        # device_id
        self.retrieve_args[0] = 20

        # data_type
        self.retrieve_args[3] = 'A'

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s ORDER BY time DESC;",
            (20, 'A')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_reverse(self):
        # device_id
        self.retrieve_args[0] = 30

        # data_type
        self.retrieve_args[3] = 'B'

        # reverse
        self.retrieve_args[6] = True

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s ORDER BY time ASC;",
            (30, 'B')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_limit(self):
        # device_id
        self.retrieve_args[0] = 40

        # data_type
        self.retrieve_args[3] = 'C'

        # limit
        self.retrieve_args[5] = 41

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s ORDER BY time DESC LIMIT %s;",
            (40, 'C', 41)
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_start_time(self):
        # device_id
        self.retrieve_args[0] = 50

        # data_type
        self.retrieve_args[3] = 'D'

        # start_time
        self.retrieve_args[1] = 51

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND time >= to_timestamp(%s)"\
            " AND type = %s ORDER BY time DESC;",
            (50, 51, 'D')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_end_time(self):
        # device_id
        self.retrieve_args[0] = 60

        # data_type
        self.retrieve_args[3] = 'E'

        # end_time
        self.retrieve_args[2] = 61

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND time <= to_timestamp(%s)"\
            " AND type = %s ORDER BY time DESC;",
            (60, 61, 'E')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_start_and_end_time(self):
        # device_id
        self.retrieve_args[0] = 70

        # data_type
        self.retrieve_args[3] = 'F'

        # start_time
        self.retrieve_args[1] = 71

        # end_time
        self.retrieve_args[2] = 72

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND time >= to_timestamp(%s)"\
            " AND time <= to_timestamp(%s) AND type = %s ORDER BY time DESC;",
            (70, 71, 72, 'F')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_device_seadplug(self):
        # device_id
        self.retrieve_args[0] = 80

        # data_type
        self.retrieve_args[3] = 'G'

        # device
        self.retrieve_args[7] = 'seadplug'

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s AND device IS NULL"\
            " ORDER BY time DESC;",
            (80, 'G')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_device_egauge(self):
        # device_id
        self.retrieve_args[0] = 90

        # data_type
        self.retrieve_args[3] = 'H'

        # device
        self.retrieve_args[7] = 'egauge'

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s AND device IS NOT NULL"\
            " ORDER BY time DESC;",
            (90, 'H')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_device_other(self):
        # device_id
        self.retrieve_args[0] = 100

        # data_type
        self.retrieve_args[3] = 'I'

        # device
        self.retrieve_args[7] = 'foo'

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data FROM data_raw as raw WHERE serial = %s AND type = %s AND device = %s"\
            " ORDER BY time DESC;",
            (100, 'I', 'foo')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_diff(self):
        # device_id
        self.retrieve_args[0] = 110

        # data_type
        self.retrieve_args[3] = 'J'

        # device
        self.retrieve_args[7] = 'bar'

        #diff
        self.retrieve_args[8] = True

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data  - lag(data) OVER (ORDER BY time DESC) as diff FROM data_raw as raw WHERE serial = %s"\
            " AND type = %s AND device = %s ORDER BY time DESC;",
            (110, 'J', 'bar')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_diff_reverse(self):
        # device_id
        self.retrieve_args[0] = 120

        # data_type
        self.retrieve_args[3] = 'K'

        # reverse
        self.retrieve_args[6] = True

        # device
        self.retrieve_args[7] = 'baz'

        # diff
        self.retrieve_args[8] = True

        query_db.perform_query = self.format_list_factory(
            "SELECT time, data  - lag(data) OVER (ORDER BY time ASC) as diff FROM data_raw as raw WHERE serial = %s"\
            " AND type = %s AND device = %s ORDER BY time ASC;",
            (120, 'K', 'baz')
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')

    def test_list_format_energy(self):
        # device_id
        self.retrieve_args[0] = 130

        # data_type
        self.retrieve_args[3] = 'P'

        # device
        self.retrieve_args[7] = 'qux'

        # granularity
        self.retrieve_args[9] = 131

        # list_format
        self.retrieve_args[10] = 'energy'

        query_db.perform_query = self.format_list_factory(
            "SELECT time, abs(CAST(lag(data) OVER (ORDER BY time DESC) - data AS DECIMAL) / 36e5)"\
            " FROM data_raw as raw WHERE serial = %s AND type = %s AND device = %s AND"\
            " CAST(extract(epoch from time) as INTEGER) %% %s = 0 ORDER BY time DESC;",
            (130, 'P', 'qux', 131)
        )
        self.assertEqual(query_db.retrieve_within_filters(*self.retrieve_args), 'perform_query called')


if __name__ == '__main__':
    unittest.main()
