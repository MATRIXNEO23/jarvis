"""Acceptance of the trusted app gateway; Windows only, no live audio/account."""
import os
from pathlib import Path
import tempfile
import unittest

from addon_manager import AddonManager, AddonError
from live_capabilities import LiveCapabilityRegistry

MANIFEST = {"schema_version":1,"id":"programmi_app","name":"Programmi e app",
 "version":"0.1.0","description":"Avvia le applicazioni scelte nelle impostazioni.",
 "actions":[{"id":"addon.programmi_app.avvia","description":"Avvia un programma autorizzato dal nome richiesto.",
 "example":"avvia Netflix","core_action":"apps.launch"}]}

@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class ProgramGatewayAcceptance(unittest.TestCase):
 def test_selected_app_gateway_is_installable_off_then_validates_arguments(self):
  import json
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   package=root/'ProgrammiApp.jaddon';package.write_text(json.dumps(MANIFEST),encoding='utf-8')
   manager=AddonManager(LiveCapabilityRegistry(),root/'addons')
   error=None
   try: manager.install(package)
   except AddonError as exc: error=str(exc)
   self.assertIsNone(error,'The selected-program add-on must be supported: '+str(error))
   self.assertFalse(manager.list_installed()[0]['enabled'])
   manager.set_enabled('programmi_app',True)
   result=manager.resolve('addon.programmi_app.avvia',{'query':'Netflix'})
   self.assertEqual((result.handler,result.target),('program_apps','Netflix'))
   with self.assertRaises(ValueError):
    manager.resolve('addon.programmi_app.avvia',{'query':'Netflix','path':'cmd.exe'})
