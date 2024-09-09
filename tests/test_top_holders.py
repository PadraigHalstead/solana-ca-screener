from screening.topholders import top_holders
from screening.rugcheck import rugcheck

def test_top_holders_percentage_top_10():
    rugcheck("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm")
    is_valid, reason = top_holders("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm") #WIF
    assert is_valid == False
    assert "Top 10 holder is" in reason

# def test_top_holders_percentage_top_20():
#     rugcheck("9KUu74Qb4KHdjvQ3apvnu8GTYnfN9k4hPeexJ8R8pump")
#     is_valid, reason = top_holders("9KUu74Qb4KHdjvQ3apvnu8GTYnfN9k4hPeexJ8R8pump") #HDNW
#     assert is_valid == False
#     assert "Top 20 holder is" in reason

def test_top_holders_exceeds_6():
    rugcheck("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump")
    is_valid, reason = top_holders("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump") #FWOG
    assert is_valid == False
    assert reason == "One or more holders with more than 6%. Blacklisting."

# def test_top_holders_same_amount():
#     rugcheck("A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump")
#     is_valid, reason = top_holders("A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump") #FWOG
#     assert is_valid == False
#     assert reason == "Suspicious distribution. Potential mass sell bot. Blacklisting."

# def test_top_holders_distribution():
#     rugcheck("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump")
#     is_valid, reason = top_holders("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump") #FWOG
#     assert is_valid == False
#     assert reason == "Suspicious distribution. Potential mass sell bot. Blacklisting."


def test_top_holders_pass():
    rugcheck("2vyPCxHX72KwLo2dTCTERH9fMVz9zHb7md51cas9pump")
    is_valid, reason = top_holders("2vyPCxHX72KwLo2dTCTERH9fMVz9zHb7md51cas9pump") #PEIPEI
    assert is_valid == True
    assert reason == "Top Holders Pass"