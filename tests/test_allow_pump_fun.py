from screening.pumpfuncheck import check_pumpfun_test

def test_allow_pump_fun_false() -> False:
    is_valid, reason = check_pumpfun_test("A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", False) #FWOG
    assert is_valid == False
    assert reason == "Pump.fun tokens not allowed. Blacklisting:"

def test_allow_pump_fun_true() -> False:
    is_valid, reason = check_pumpfun_test("A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", True) #FWOG
    assert is_valid == True
    assert reason == "Pump.fun Check Pass"

def test_allow_pump_fun_not() -> False:
    is_valid, reason = check_pumpfun_test("7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", True) #POPCAT
    assert is_valid == True
    assert reason == "Pump.fun Check Pass"

