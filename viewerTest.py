
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class ViewTest( gtBase.GLtoast ):
    ''' Test viewing in a 3D enviroment
    '''
    
    COLOURS = {  # Fill,   Highlight
        "BACK"  : ["080808","161616"], # 
        "GRID"  : ["808080","A0A0A0"], # 
        "FLOOR" : ["484848","FFFFFF"], # 
    }
    
    def __init__(self):
        super( ViewTest, self ).__init__()

        
    def init( self ):
        # super
        super( ViewTest, self ).init()
        
        # set coloura
        self._bg = CT.web24f( self.COLOURS["BACK"][0] )
        
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF") )
        
        # my Vars

        
        # timing
        now         = time.time()
        tmp_time    = DT.datetime.fromtimestamp( now )
        log_time    = DT.datetime( tmp_time.year, tmp_time.month, tmp_time.day, 0, 0, 0, 0 )
        self._epoch = CR.timegm( log_time.timetuple() )
        del( tmp_time, log_time, now )
        self.now = time.time() - self._epoch
        
        # Register keys / Callback into the key_man

        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        
        # set up Messages
        self._hud_man.addElement( "MSG", self._wh[0]-200, self._wh[1]-10, CT.web23f("#FFFFFF"), -1 )
        self._hud_man.addMsg( "LOG", "Ready!" )
        
        
    def end( self ):
        exit(0)      
        
            
    def _draw( self ):
        # Reset canvas
        self._clear()
        
        #set to Camera
    
        # Draw Stuff
        self.set2D()
        self.now = time.time() - self._epoch # I'd prefer not to do this every frame, but it's needed for drawing
        
        # do lists
        self.paintLists()
        
        # swap buffers & clean up
        super( ViewTest, self )._draw()
        
        
myApp = ViewTest()
myApp._title = "MoCap viewer"
myApp._center = True
myApp._wh = ( 640, 480 )

myApp.init()
myApp.prep()
myApp.exe()

"""
What's supposed to happen in here...

    A camera model, having an Xform, (pos, gaze vector)
        + An aspect Ratio
        + A Fov expressed in Deg
        + Near & far Clip distances
        For computation
            + An interest and a roll axis
            + A Film Gate size & lens focal length
        For Display
            + Image planr on Near or Far plane of frustrum
                + dialable opacity
                + Static Image, Image Sequence, Video
                + Un-warpable with k1, k2 radial peramiters
    

















































"""
