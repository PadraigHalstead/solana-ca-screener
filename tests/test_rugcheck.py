from screening.rugcheck import rugcheck
from time import sleep

def test_rugcheck_pass() -> False:
    is_valid, reason = rugcheck("7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr") #POPCAT
    assert is_valid == True
    assert reason == "Rugcheck Pass"

def test_rugcheck_freeze_authority_enabled() -> False:
    is_valid, reason = rugcheck("27U6QrXakgCAB4KjGT9ZWzAB3Ucw1oA7Sk7trGouFZu9") #WARROOM
    assert is_valid == False
    assert reason == "Freeze Authority is enabled. Blacklisting:"

def test_rugcheck_mint_authority_enabled() -> False:
    is_valid, reason = rugcheck("DytyRjGoqNfv96mikY6bJ489b8PF6D6ASR2KxYhHWKCo") #DMDPEPE
    assert is_valid == False
    assert reason == "Mint Authority is enabled. Blacklisting:"

def test_rugcheck_mutable_metadata() -> False:
    is_valid, reason = rugcheck("AiA6KKDVhYAFKrUVhUH9BgyF8v3rKLVhrsfdF9U4gw3S") #FLOSSIE
    assert is_valid == False
    assert reason == "Metadata is mutable. Blacklisting:"

def test_rugcheck_low_liquidity() -> False:
    is_valid, reason = rugcheck("4JijZiX1s5PNwSpbGUjf5BQSrRV6DnVH4MsggM4AuajW") #PETATE
    assert is_valid == False
    assert reason == "Token has very Low Liquidity. Blacklisting:"

def test_rugcheck_copy_cat() -> False:
    is_valid, reason = rugcheck("8JAoMxhNwJbMPMHTtdUnHafUhr43rbF6odddfFFfzb3N") #ZION
    assert is_valid == False
    assert reason == "Token is copying a verifed token symbol. Blacklisting:"

def test_rugcheck_lp_not_locked() -> False:
    is_valid, reason = rugcheck("7fc26zrkcpatx9e62qxjmw3hk1cm1jlqwukpyfp4vwl5") #CNPEPE
    assert is_valid == False
    assert reason == "Deployer is holding LP. Blacklisting:"

# def test_rugcheck_insiders() -> False:
#     is_valid, reason = rugcheck()
#     assert is_valid == False
#     assert "Insider holdings are too high" in reason 