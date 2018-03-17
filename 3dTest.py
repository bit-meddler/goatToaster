
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class Dimentions( gtBase.GLtoast ):
    '''
       3D experiment 
        
    '''
    
    COLOURS = {
        
    }
    
    
    def __init__(self):
        super( Dimentions, self ).__init__()
        
         
    def init( self ):
        # super
        super( Dimentions, self ).init()
        # set up HUD LOG
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF"), -1 )
        
        # my Vars
        # #######
        
               
        
        # Register keys / Callback into the key_man

        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        self._hud_man.addMsg( "LOG", "Ready!", overide_life=33 )        
        
        
    def end( self ):
        exit(0)      
        
        
    def _draw( self ):
        # Reset canvas
        self._clear()
        
        # Draw 3D
        self.set3D()
        
        # do 3d elements
        
        # Draw 2D UI
        self.set2D()
        
        # do UI lists
        self.paintLists()
        
        # swap buffers & clean up
        super( Dimentions, self )._draw()
        
        
myApp = Dimentions()
myApp._title = "3D Experiment"
myApp._bg = tuple( CT.web24f("#101010") )
myApp._log_col = "#FFFFFF"
myApp._center = True
myApp._wh = ( 500, 500 )

myApp.init()
myApp.prep()
myApp.exe()

"""
































































"""
