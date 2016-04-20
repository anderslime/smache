from smache.cache import Smache


def test_representation():
    smache = Smache()

    assert str(smache) == "<Smache deps=[]>"
