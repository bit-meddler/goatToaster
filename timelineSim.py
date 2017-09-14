
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class TimeLine( gtBase.GLtoast ):
    ''' 
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

        
        # timing

        
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
