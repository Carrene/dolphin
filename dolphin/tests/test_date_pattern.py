from dolphin.validators import DATE_PATTERN as pattern


def test_date_pattern():
    assert pattern.match('2018-01-01')
    assert pattern.match('2018-1-1')
    assert pattern.match('2018-10-10')
    assert pattern.match('2018-12-31')

    assert not pattern.match('218-10-10')
    assert not pattern.match('20118-10-10')
    assert not pattern.match('2018-101-10')
    assert not pattern.match('2018-10-101')
    assert not pattern.match('2018-14-10')
    assert not pattern.match('2018-10-32')
    assert not pattern.match('s2018-10-10')
    assert not pattern.match('2018-s10-10')
    assert not pattern.match('2018-10-s10')
    assert not pattern.match('20.18-10-10')
    assert not pattern.match('2018-1.0-10')
    assert not pattern.match('2018-10-1.0')
