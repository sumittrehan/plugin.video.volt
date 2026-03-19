import pytest
from unittest import mock

import resources.lib.ui.home as home_mod
from resources.lib.ui.home import show_home


def test_show_home(monkeypatch):
    # Simulate running inside Kodi with a valid handle
    monkeypatch.setattr(home_mod, 'xbmcplugin', mock.Mock(), raising=False)
    monkeypatch.setattr(home_mod, 'xbmcgui', mock.Mock(), raising=False)
    monkeypatch.setattr(home_mod, 'HANDLE', 1, raising=False)
    mock_plugin = home_mod.xbmcplugin

    show_home()

    # show_home adds 5 menu entries
    assert mock_plugin.addDirectoryItem.call_count == 5


