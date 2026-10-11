import pytest
from nodes import _extract_source_numbers, _find_source_url


class TestExtractSourceNumbers:
    def test_two_single_tags(self):
        text = "Evergy beat estimates [Source 1] and expanded [Source 3]"
        assert _extract_source_numbers(text) == [1, 3]

    def test_repeated_tags(self):
        text = (
            "Evergy beat estimates [Source 1] and expanded [Source 3], "
            "new infra project [Source 3], new gov funding [Source 3]"
        )
        assert _extract_source_numbers(text) == [1, 3, 3, 3]

    def test_tags_outside_typical_range(self):
        text = "Evergy beat estimates [Source 0] and expanded [Source 9]"
        assert _extract_source_numbers(text) == [0, 9]

    def test_missing_space_in_tag_not_matched(self):
        text = "Evergy beat estimates [Source1]"
        assert _extract_source_numbers(text) == []

    def test_combined_citation_silently_dropped(self):
        text = "Evergy expanded its grid [Source 1, 3]"
        assert _extract_source_numbers(text) == []

    def test_empty_string(self):
        assert _extract_source_numbers("") == []


def _url_tags(result):
    return {
        "sources": [{"url": s["url"], "tags": s["tags"]} for s in result["sources"]],
        "invalid_tags": result["invalid_tags"],
    }


class TestFindSourceUrl:
    @pytest.fixture
    def chunks(self):
        return [
            {"url": "a.com", "title": "t1", "source_name": "s1", "published_at": "2026-01-01"},
            {"url": "a.com", "title": "t2", "source_name": "s2", "published_at": "2026-01-02"},
            {"url": "b.com", "title": "t3", "source_name": "s3", "published_at": "2026-01-03"},
        ]

    def test_groups_tags_by_url(self, chunks):
        result = _find_source_url([1, 2, 3], chunks)
        assert _url_tags(result) == {
            "sources": [
                {"url": "a.com", "tags": [1, 2]},
                {"url": "b.com", "tags": [3]},
            ],
            "invalid_tags": [],
        }

    def test_out_of_range_tags_are_invalid_not_a_crash(self, chunks):
        result = _find_source_url([1, 0, 4], chunks)
        assert _url_tags(result) == {
            "sources": [{"url": "a.com", "tags": [1]}],
            "invalid_tags": [0, 4],
        }

    def test_duplicate_tag_not_repeated(self, chunks):
        result = _find_source_url([1, 1], chunks)
        assert _url_tags(result) == {
            "sources": [{"url": "a.com", "tags": [1]}],
            "invalid_tags": [],
        }

    def test_empty_tag_list(self, chunks):
        result = _find_source_url([], chunks)
        assert result == {"sources": [], "invalid_tags": []}

    def test_empty_chunks(self):
        result = _find_source_url([1], [])
        assert result == {"sources": [], "invalid_tags": [1]}
