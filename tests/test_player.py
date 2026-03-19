from unittest import mock

from resources.lib.ui.player import play_source


def test_play_source_without_url(monkeypatch):
    # call with no source should return safely
    play_source('', 'movie', title='Dummy')


@mock.patch('resources.lib.ui.player.xbmcgui')
@mock.patch('resources.lib.ui.player.xbmc')
def test_play_source_resume_prompt(mock_xbmc, mock_xbmcgui):
    # simulate user chooses to resume
    mock_xbmcgui.Dialog.return_value.yesno.return_value = True
    player_mock = mock_xbmc.Player.return_value

    # patch _resolve_debrid to return direct link without API call
    from resources.lib.ui.player import _resolve_debrid
    with mock.patch('resources.lib.ui.player._resolve_debrid', return_value='http://test.stream'):
        play_source('http://source', 'movie', title='Dummy', resume_seconds=120)

    mock_xbmcgui.Dialog.return_value.yesno.assert_called_once()
    player_mock.seekTime.assert_called_once_with(120)
