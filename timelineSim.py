
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class TimeLine( gtBase.GLtoast ):
    ''' A nice looking timeline:
        # BG with graticules
        # sub region display [log, active, cached]
        # marks in log region
        # moving play head
        # IN/OUT indicators
        # Magnifying Glass
        # Rate stretch (Multiplier) Control
        
        Respecting AVID shortcuts:
        # [Space] = toggle Play Pause
        # [I], [O] = Mark main In/Out
        # [Shift] + [I], [O] = append In/Out region to regions list
        # [J], [K], [L] ->
            K tapped: toggle Play Pause 1x
            K Held: Play at 1x, enable Multipliers
            K released: Pause, reset to 1x
            J/L tapped: step 1 frame < or >
            J/L held: Play 1x in < or >
            K Held, and and J/L Tapped: temporary inc or dec Multiplier
                                        multi taps = doubling of inc/dec
        # [<], [>] = multiplier dec/inc 
        # [[], []] = Magnify dec/inc
        # [T] = promote select region to active sub-region
        # [Shift]+[T] = extract select region from active sub0region
        
        Click Handlers ?
        # We could do this, invisible rect on top of 'hit' regions?
        # or not bother, this is just an experiment
        
        
    '''
    
    COLOURS = {
        "BACK"    : "#bfcfe1",
        "TEXT"    : "#000000",
        "IN_TICK" : "#009240",
        "OUT_TICK": "#da251d",
        "PLAY"    : "#29166f",
        "LENS"    : "#007cc3",
        "IN_BG"   : "#70c564",
        "OUT_BG"  : "#ff9696",
        "TIME_BG" : "#96b5ed"
    }
    
    
    def __init__(self):
        super( HenchSim, self ).__init__()
        
         
    def init( self ):
        # super
        super( HenchSim, self ).init()
        # set up HUD LOG
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF") )
        
        # my Vars
        # #######
        
        # draw control
        self._border_pad = 5
        
        # playback
        self.end_frame  = 3600 # factors to 24, 25, 30 fps
        self.cur_frame  = 1    # anims count from 1
        self.play_multi = 1.   # multiplier
        self.skip_multi = 1.
        
        # Markings
        self.mark_in  = -1
        self.mark_out = -1
        self.mark_active = [] # List of [in,out] pairs, in order
        self.mark_cached = [] #  ditto
        
        # timing
        self.native_frame_dur = 0.04 # 25fps
        
        
        # Register keys / Callback into the key_man

        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        self._hud_man.addMsg( "LOG", "Ready!" )        
        
        
    def end( self ):
        exit(0)      
        
        
    def _draw( self ):
        # Reset canvas
        self._clear()
    
        # Draw Stuff
        self.set2D()
        
        # do lists
        self.paintLists()
        
        # swap buffers & clean up
        super( HenchSim, self )._draw()
        
        
myApp = TimeLine()
myApp._title = "Optimal Timeline Experiment"
myApp._bg = tuple( CT.web24f("#D4D0C8") )
myApp._log_col = "#000000"
myApp._center = True
myApp._wh = ( 500, 95 )

myApp.init()
myApp.prep()
myApp.exe()

"""
































































"""
