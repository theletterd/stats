from statsapp.tools import util

def test_convert_kg_to_lbs_with_zero():
    lbs = util.convert_kg_to_lbs(0)
    assert lbs == 0

def test_convert_kg_to_lbs_with_454():
    lbs = util.convert_kg_to_lbs(454)
    assert lbs == 1000

