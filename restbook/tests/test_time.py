
from unittest import TestCase

from hypothesis import given
from hypothesis.strategies import integers
from hypothesis.extra.datetime import datetimes

from restbook import time 

###############################################################################

class DateInfoTest(TestCase):

    @given(
        datetime=datetimes()
    )
    def test_date_info_fields_are_correct(self, datetime):
        '''
        Test that get_dateinfo returns a correct DateInfo tuple.
        '''
        year, week_number, iso_day = datetime.isocalendar()
        day = iso_day - 1

        dateinfo = time.get_dateinfo(datetime)

        offset = (day * 60 * 24) + (datetime.hour * 60) + datetime.minute

        assert(isinstance(dateinfo, time.DateInfo))
        assert(datetime == dateinfo.datetime)
        assert(year == dateinfo.year)
        assert(week_number == dateinfo.week)
        assert(day == dateinfo.weekday)
        assert(offset == dateinfo.offset)

###############################################################################

class MinuteOffsetUnitTest(TestCase):

    def test_minutes_in_week(self):
        '''
        Minutes in week must be accurate.
        '''

        self.assertEqual(
            time.MinuteOffset.MINUTES_IN_WEEK,
            60 * 24 * 7,
            'Minutes in week must equal 60 * 24 * 7.'
        )

##############################

    @given(
        day=integers(min_value=0, max_value=6),
        hour=integers(min_value=0, max_value=72),
        minute=integers(min_value=0, max_value=59)
    )
    def test_convert_from_ints(self, day, hour, minute):
        '''
        Should convert from three integers, one representing the
        weekday (as per the DateInfo tuple) and the other two
        representing the hour and minutes.
        '''

        day_offset = day * 60 * 24
        hour_offset = hour * 60

        expected_offset = day_offset + hour_offset + minute
        actual_offset = time.MinuteOffset.from_integers(day, hour, minute)

        assert(expected_offset == actual_offset)

##############################

    def test_conversion_from_strings(self):
        '''
        Should convert from 'Monday 00.00' to 0 or 'Monday 20.00' to 1200.
        '''

        sample = (
            (0, 'Monday 00.00'),
            (61, 'Monday 01.01'),
            (1200, 'Monday 20.00'),
            (3480, 'Wednesday 10.00'),
            (5250, 'Thursday 15.30'),
            (7020, 'Friday 21.00'),
            (10079, 'Sunday 23.59'),
            (10139, 'Sunday 24.59'), # hours should be able to wrap to next day
        )

        for example in sample:
            expected_result = example[0]
            given_string = example[1]

            self.assertEqual(
                expected_result,
                time.MinuteOffset.from_string(given_string),
                'MinuteOffset.from_string should convert '
                '"{string}" to {offset}.'.format(string=given_string,
                                                 offset=expected_result)
            )

##############################

    def test_conversion_to_strings(self):
        '''
        Should convert 0 to 'Monday 00.00' or 1200 to 'Monday 20.00'.
        '''

        sample = (
            (0, 'Monday 00.00'),
            (61, 'Monday 01.01'),
            (1200, 'Monday 20.00'),
            (3480, 'Wednesday 10.00'),
            (5250, 'Thursday 15.30'),
            (7020, 'Friday 21.00'),
            (10079, 'Sunday 23.59'),
            (10139, 'Sunday 24.59'), # hours should be able to wrap to next day
        )

        for example in sample:
            expected_result = example[1]
            given_offset = example[0]

            self.assertEqual(
                expected_result,
                str(time.MinuteOffset(given_offset)),
                'MinuteOffset.from_string should convert '
                '"{offset}" to {string}.'.format(offset=given_offset,
                                                 string=expected_result)
            )

##############################

    def test_failure_when_converting_invalid_strings(self):
        '''
        MinuteOffset.from_string should fail when given invalid day
        names or minutes that exceed 59.
        '''

        sample = (
            'Someday 00.00',
            'Monday 00.60',
        )

        for bad_example in sample:

            try:
                time.MinuteOffset.from_string(bad_example)
            except ValueError:
                pass
            else:
                self.fail(
                    'MinuteOffset.from_string should fail when '
                    'given "{invalid}".'.format(invalid=bad_example)
                )

