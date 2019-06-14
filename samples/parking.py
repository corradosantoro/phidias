

# import libraries
from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class coin(Procedure): pass

class hour(Procedure): pass
class half_hour(Procedure): pass
class reset(Procedure): pass

class verify_ticket(Procedure): pass

class selected_amount(SingletonBelief): pass
class selected_time(SingletonBelief): pass

def_vars("M", "T", "C")

hour() / (selected_amount(M) & selected_time(T) ) >> \
  [
      "T = T + 1.0",
      show_line("Parking duration ", T, " hours"),
      "M = M + 100",
      +selected_time(T),
      +selected_amount(M)
  ]

half_hour() / (selected_amount(M) & selected_time(T) ) >> \
  [
      "T = T + 0.5",
      show_line("Parking duration ", T, " hours"),
      "M = M + 50",
      +selected_time(T),
      +selected_amount(M)
  ]

reset() >> [ show_line("reset"), +selected_time(0), +selected_amount(0) ]

coin(200) / (selected_amount(M) & selected_time(T) & gt(M, 0)) >> \
  [
      "M = M - 200",
      "T = T - 2",
      show_line("Inserted 2 euros"),
      verify_ticket(M, T)
  ]
coin(100) / (selected_amount(M) & selected_time(T) & gt(M, 0)) >> \
  [
      "M = M - 100",
      "T = T - 1",
      show_line("Inserted 1 euro"),
      verify_ticket(M, T)
  ]
coin(50) / (selected_amount(M) & selected_time(T) & gt(M,0) ) >> \
  [
      "M = M - 50",
      "T = T - 0.5",
      show_line("Inserted 50 cents"),
      verify_ticket(M, T)
  ]
coin(20) / (selected_amount(M) & selected_time(T) & gt(M,0) ) >> \
  [
      "M = M - 20",
      "T = T - 0.2",
      show_line("Inserted 20 cents"),
      verify_ticket(M, T)
  ]
coin(10) / (selected_amount(M) & selected_time(T) & gt(M,0) ) >> \
  [
      "M = M - 10",
      "T = T - 0.1",
      show_line("Inserted 10 cents"),
      verify_ticket(M, T)
  ]
coin(5) / (selected_amount(M) & selected_time(T) & gt(M,0) ) >> \
  [
      "M = M - 5",
      "T = T - 0.05",
      show_line("Inserted 5 cents"),
      verify_ticket(M, T)
  ]
coin(C) >> [ show_line("Please select time first") ]

verify_ticket(M, T) / leq(M, 0) >> \
  [
      show_line("Printing Ticket"),
      +selected_amount(0),
      +selected_time(0)
  ]
verify_ticket(M, T) >> \
  [
      show_line("Remaining to pay ", M, " cents"),
      +selected_amount(M),
      +selected_time(T)
  ]


PHIDIAS.assert_belief(selected_time(0))
PHIDIAS.assert_belief(selected_amount(0))

# start PHIDIAS
PHIDIAS.run()

# run the engine shell
PHIDIAS.shell(globals())
