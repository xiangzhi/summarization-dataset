from constructor import utils


def test_combination():
    
    assert utils.list_objects_in_str(["one"]) == "one"
    assert utils.list_objects_in_str(["one", "two"]) == "one and two"
    assert utils.list_objects_in_str(["one", "two", "three"]) == "one, two, and three"

