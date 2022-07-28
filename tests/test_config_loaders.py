import pytest

from app.config import hs_data
from app.exceptions import ArgumentError


class TestHsData:

    def test_hs_data_gettype(self):
        with pytest.raises(StopIteration):
            hs_data.gettype(sign='UNKNOWN_SIGN')

        with pytest.raises(StopIteration):
            hs_data.gettype(name='UNKNOWN_NAME')

        with pytest.raises(ArgumentError):
            hs_data.gettype()

        with pytest.raises(ArgumentError):
            hs_data.gettype(sign='M', name='Minion')

        assert hs_data.gettype(sign='M').en == 'Minion'
        assert hs_data.gettype(sign='S').en == 'Spell'
        assert hs_data.gettype(sign='W').en == 'Weapon'
        assert hs_data.gettype(sign='H').en == 'Hero'
        assert hs_data.gettype(sign='L').en == 'Location'

        assert hs_data.gettype(name='Minion').sign == 'M'
        assert hs_data.gettype(name='Spell').sign == 'S'
        assert hs_data.gettype(name='Weapon').sign == 'W'
        assert hs_data.gettype(name='Hero').sign == 'H'
        assert hs_data.gettype(name='Location').sign == 'L'

    def test_hs_data_getrarity(self):
        with pytest.raises(StopIteration):
            hs_data.getrarity(sign='UNKNOWN_SIGN')

        with pytest.raises(StopIteration):
            hs_data.getrarity(name='UNKNOWN_NAME')

        with pytest.raises(ArgumentError):
            hs_data.getrarity()

        with pytest.raises(ArgumentError):
            hs_data.getrarity(sign='L', name='Legendary')

        assert hs_data.getrarity(sign='L').en == 'Legendary'
        assert hs_data.getrarity(sign='E').en == 'Epic'
        assert hs_data.getrarity(sign='R').en == 'Rare'
        assert hs_data.getrarity(sign='C').en == 'Common'
        assert hs_data.getrarity(sign='NO').en == 'No rarity'

        assert hs_data.getrarity(name='Legendary').sign == 'L'
        assert hs_data.getrarity(name='Epic').sign == 'E'
        assert hs_data.getrarity(name='Rare').sign == 'R'
        assert hs_data.getrarity(name='Common').sign == 'C'
        assert hs_data.getrarity(name='No rarity').sign == 'NO'
