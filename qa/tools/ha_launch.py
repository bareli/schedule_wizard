"""QA-only launcher: run Home Assistant natively on Windows for frontend testing.

Windows' asyncio loops have no signal handlers; HA only uses them for SIGTERM/SIGHUP.
Throwaway dev instance, never used for anything else.
"""
import asyncio
import signal
import sys

if not hasattr(signal, 'SIGHUP'):
    signal.SIGHUP = 1  # only passed to the no-op handler registration below

for cls in (asyncio.AbstractEventLoop, asyncio.BaseEventLoop):
    cls.add_signal_handler = lambda self, *a, **k: None
    cls.remove_signal_handler = lambda self, *a, **k: False

from homeassistant.__main__ import main  # noqa: E402

sys.exit(main())
