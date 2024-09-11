from screening.topholders import top_holders
from screening.rugcheck import rugcheck

def test_top_holders_percentage_top_10():
    rugcheck("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm")
    is_valid, reason = top_holders("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm") #WIF
    assert is_valid == False
    assert "Top 10 holder is" in reason

def test_top_holders_exceeds_6():
    rugcheck("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump")
    is_valid, reason = top_holders("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump") #FWOG
    assert is_valid == False
    assert reason == "One or more holders with more than 6%. Blacklisting:"

def test_top_holders_distribution():
    rugcheck("6nTFeymkigBZ6u28LWJcNGFFe98HqpHWvrg1Gu6Kpump")
    is_valid, reason = top_holders("6nTFeymkigBZ6u28LWJcNGFFe98HqpHWvrg1Gu6Kpump") #CWIF
    assert is_valid == False
    assert reason == "Suspicious distribution. Potential mass sell bot. Blacklisting:"


def test_top_holders_pass():
    rugcheck("2vyPCxHX72KwLo2dTCTERH9fMVz9zHb7md51cas9pump")
    is_valid, reason = top_holders("2vyPCxHX72KwLo2dTCTERH9fMVz9zHb7md51cas9pump") #PEIPEI
    assert is_valid == True
    assert reason == "Top Holders Pass"