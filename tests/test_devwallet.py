from screening.devwallet import devwallet


def test_devwallet_exceeds_6():
    is_valid, reason = devwallet("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump")
    assert is_valid == False
    assert reason == "Dev owns more than 6%. Blacklisting:"

def test_devwallet_pass():
    is_valid, reason = devwallet("81u251ZH4NCUe2h2ob8N2WE2cqUjnR5bybEXhMH5pump")
    assert is_valid == True
    assert reason == "Dev Holdings Pass"

def test_devwallet_dev_sold():
    is_valid, reason = devwallet("4sfkd8gh4oVT75FkRVQ5pLFPepynJdrqf332Beq5pump")
    assert is_valid == False
    assert reason == "Dev has sold. Blacklisting:"

