import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from foreground_power import ES_CONTINUOUS, ES_DISPLAY_REQUIRED, ES_SYSTEM_REQUIRED, ForegroundPower


class ForegroundPowerTests(unittest.TestCase):
    def test_focus_restore_disable_and_shutdown_release_keep_awake(self):
        power = ForegroundPower.__new__(ForegroundPower)
        power.root = SimpleNamespace(winfo_ismapped=lambda: True, after=Mock())
        power.enabled = Mock(return_value=True)
        power.active = False
        power.window_api = SimpleNamespace(hwnd=lambda _: 25, zoomed=Mock(return_value=True))
        power.foreground = Mock(return_value=25)
        power.execution_state = Mock(return_value=1)
        keep = ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED

        power.refresh()
        power.execution_state.assert_called_once_with(keep)
        power.refresh()
        self.assertEqual(power.execution_state.call_count, 1)

        for changed, previous in ((power.foreground, 25), (power.window_api.zoomed, True),
                                  (power.enabled, True)):
            changed.return_value = False
            power.refresh()
            power.execution_state.assert_called_with(ES_CONTINUOUS)
            changed.return_value = previous
            power.refresh()
            power.execution_state.assert_called_with(keep)
        power.close()
        power.execution_state.assert_called_with(ES_CONTINUOUS)
        self.assertFalse(power.active)
