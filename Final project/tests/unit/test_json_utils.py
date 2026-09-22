from data.json_utils import extract_json


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_json_strips_markdown_fence():
    text = '```json\n{"a": 1}\n```'
    assert extract_json(text) == '{"a": 1}'


def test_extract_json_strips_surrounding_prose():
    text = 'Here you go:\n{"a": 1}\nHope that helps!'
    assert extract_json(text) == '{"a": 1}'
