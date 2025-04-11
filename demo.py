from speechorder.localsod import t
from speechorder import *
import time

lcod = t()
lcod.SetASR( SherpaONNX )

while True:
    cmd = input()
    md = cmd[0:4]
    text = cmd[4:]
    print( f" Cmd: m/{md} tx/{text}" )
    time.sleep( 1/60 )
    pass