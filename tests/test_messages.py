class TestCardRequestInfo:

    def test_card_request_info_init(self, card_request_info_obj):
        assert card_request_info_obj.rows == []

    def test_card_request_info_format(self, card_request_info_obj):
        card_request_info_obj.format()
        assert card_request_info_obj.classes.format('Demon Hunter,Mage') in card_request_info_obj.rows
        assert card_request_info_obj.ctype.format('Minion') in card_request_info_obj.rows
        assert card_request_info_obj.rarity.format('Common') in card_request_info_obj.rows
        assert card_request_info_obj.attack.format('4') in card_request_info_obj.rows
        assert card_request_info_obj.health.format('3') in card_request_info_obj.rows
        assert card_request_info_obj.cost.format('3') in card_request_info_obj.rows
        assert card_request_info_obj.name.format('A') in card_request_info_obj.rows
        assert card_request_info_obj.cset.format('Voyage to the Sunken City') in card_request_info_obj.rows


class TestCardListInfo:

    def test_card_list_info_init(self, card_list_info_obj):
        assert card_list_info_obj.rows == []
        assert card_list_info_obj.page == 2
        assert card_list_info_obj.total == 15

    def test_card_list_info_format(self, card_list_info_obj):
        card_list_info_obj.format()
        assert len(card_list_info_obj.rows) == 1 + 6 + 1    # header row + card rows + footer row


class TestCardDetailInfo:

    def test_card_detail_info_init(self, card_detail_info_obj):
        assert card_detail_info_obj.rows == []
        assert card_detail_info_obj.text
        assert card_detail_info_obj.flavor
        assert card_detail_info_obj.tribe
        assert not card_detail_info_obj.spellschool
        assert card_detail_info_obj.artist
        assert card_detail_info_obj.mechanics
        assert '5' in card_detail_info_obj.stats
        assert '3' in card_detail_info_obj.stats
        assert '2' in card_detail_info_obj.stats

    def test_card_detail_info_format(self, card_detail_info_obj):
        card_detail_info_obj.format()
        assert card_detail_info_obj.rows
