from datetime import datetime
import unittest

from sveglia.service import next_alarm, parse_command


class AlarmTests(unittest.TestCase):
    def test_clock_and_alarm_commands_are_distinct(self):
        self.assertEqual(parse_command("Che ore sono?"), ("clock", ""))
        self.assertEqual(parse_command("imposta la sveglia alle 7:30"), ("set", "7:30"))
        self.assertEqual(parse_command("ferma la sveglia"), ("stop", ""))
        self.assertIsNone(parse_command("non impostare la sveglia alle 7"))

    def test_alarm_uses_next_occurrence_and_rejects_invalid_values(self):
        now = datetime(2026, 11, 6, 23, 30)
        self.assertEqual(next_alarm("23:45", now), datetime(2026, 11, 6, 23, 45))
        self.assertEqual(next_alarm("7 30", now), datetime(2026, 11, 7, 7, 30))
        with self.assertRaises(ValueError):
            next_alarm("24:60", now)
