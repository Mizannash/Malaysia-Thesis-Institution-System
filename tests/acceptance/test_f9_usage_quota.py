"""Acceptance tests: Usage Quota (use case UC9 in docs/REQUIREMENTS.md)

Used by: Student / Researcher. Limits free trial users to 3 generations/day; resets daily
Placeholders from GigaLab: each fails until it is replaced by a real test in its milestone. Never delete one to make it pass.
"""
import pytest


def test_ac9_1():
    pytest.fail("Not written yet: Given a free-trial user who has used 3 generations today, when they attempt a 4th, then they are blocked with an upgrade/wait message and quota resets after midnight")
