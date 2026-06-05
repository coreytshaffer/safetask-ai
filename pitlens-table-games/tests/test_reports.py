import json
from pitlens.exports.html_report import generate_html_report
from pitlens.exports.json_export import generate_json_export

def test_json_export_structure(mocker):
    # Mock the DB calls to return empty or minimal data
    mocker.patch('pitlens.exports.json_export.get_game_sessions', return_value=[])
    
    res = generate_json_export("fake_session")
    assert res == "{}"

def test_html_report_safety(mocker):
    mocker.patch('pitlens.exports.html_report.generate_json_export', return_value='{"metadata": {"session_id": "123"}}')
    html = generate_html_report("fake_session")
    
    # Assert report language safety
    assert "cheater" not in html.lower()
    assert "fraud" not in html.lower()
    assert "Review Limitations" in html
