from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import numpy as np
import time
import random


import chromaTool as CT


class KeyMan( object ):
    DOWN = 0
    UP   = 1
    
    SPECIAL_OS = 128
    LEFT_SHIFT = 112 + SPECIAL_OS
    RIGHT_SHIFT= 113 + SPECIAL_OS
    LEFT_CTRL  = 114 + SPECIAL_OS
    RIGHT_CTRL = 115 + SPECIAL_OS
    LEFT_ALT   = 116 + SPECIAL_OS
    
    
    def __init__( self ):
        self.history    = {}
        self.taps       = {}
        self.active     = set()
        self._boot      = time.time()
        self.tap_window = 0.255 # ms
        self.acumulate  = True
        self.last_time  = 0
        # registry
        self._rises    = {}
        self._falls    = {}
        self._taps     = {}
        
    def push( self, key_idx, action ):
        ''' deal with keypressess, keyholds, and keytaps.
            TODO:   work out packing sceme so all keys & modifiers fit
                    in flat contigious arrays (SoA)
        '''
        self.last_time = time.time()
        last_action = None
        if action==KeyMan.DOWN:
            self.active.add( key_idx )
            last_action = KeyMan.UP
        else:
            self.active.remove( key_idx )
            last_action = KeyMan.DOWN
            
        if key_idx not in self.history:
            self.history[ key_idx ] = [ 0, 0 ]
            self.taps[ key_idx ] = 0
        
        key_stats = self.history[ key_idx ]
        key_taps  = self.taps[ key_idx ]
        
        # log some data
        key_stats[ action ] = self.last_time
        delta = self.last_time - key_stats[last_action]
        
        # detect multi-taps
        if (delta < self.tap_window):
            # tapped
            if action==KeyMan.DOWN:
                key_taps += 1
        else:
            # out of tap window - tap count only cleared on subsequent press!
            if self.acumulate and action==KeyMan.DOWN:
                key_taps = 0

        # scan registered key events for 'key_idx' and emit CB
        if action==KeyMan.DOWN:
            if key_idx in self._falls:
                self._falls[key_idx]()
        else:
            if key_idx in self._rises:
                self._rises[key_idx]()
                
        if key_taps>1:
            if key_idx in self._taps:
                self._taps[key_idx]()
        # done
        
    def registerFallingCB( self, key_idx, fcall ):
        self._falls[key_idx] = fcall
        
    def registerRisingCB( self, key_idx, fcall ):
        self._rises[key_idx] = fcall
        
    def registerTapsCB( self, key_idx, fcall ):
        self._taps[key_idx] = fcall
        
        
class GLtoast( object ):

    def __init__( self ):
        self.g_wind = None
        self._glut_opts = None
        self._title = None
        self._wh = (640,480)
        self._native_wh = (1920,1280)
        self._pos = (0,0)
        self._center = False
        self._ratio_lock = True
        self._ratio = float(self._wh[0]) / float(self._wh[1])
        self._fov = 45.0
        self._z_clip = ( 0.1, 100.0 )
        self._key_man = KeyMan()
        self.reverseDrawOrder = False
     
       
    def _reSize( self, width, height ):
        new_h = 2 if(height<2) else height
        new_w = 2 if(width<2)  else width
        ''' not quite right yet
        if self._ratio_lock:
            fw, fh = float( new_w ), float( new_h )
            ratio = fw/fh
            print ratio
            if( ratio > self._ratio ):
                # width wrong
                fw = fh / self._ratio
            elif( ratio < self._ratio ):
                # wrong height
                fh = fw * self._ratio
            new_w, new_h = int( fw ), int( fh )
            print new_w, new_h, (fw/fh)
        '''
        self._wh = ( new_w, new_h )
        
        
    def _idle( self ):
        glutPostRedisplay()
        #self._draw()
        
    def _draw( self ):
        pass

    def _keyDn( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.DOWN )
    
    def _keyUp( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.UP )
        
    def _keyDnS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.DOWN )
        
    def _keyUpS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.UP )
        
    def init( self ):
        # do glut init
        glutInit()
        glutInitDisplayMode( self._glut_opts )
        
        # Get Natove res
        self._native_wh = (glutGet( GLUT_SCREEN_WIDTH ), glutGet( GLUT_SCREEN_HEIGHT ))
        # TODO: guard against requested window size > native
        
        # auto center
        if self._center:
            pos_x = (self._native_wh[0]-self._wh[0]) / 2
            pos_y = (self._native_wh[1]-self._wh[1]) / 2
            self._pos = (pos_x, pos_y)
            
        glutInitWindowSize( self._wh[0], self._wh[1] )
        glutInitWindowPosition( self._pos[0], self._pos[1] )  
        self.g_wind = glutCreateWindow( self._title )
        
        # Enable GL Options
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        glDepthFunc(GL_LESS) 
    
        # bind std CBs
        glutDisplayFunc( self._draw   )
        glutIdleFunc(    self._idle   )
        glutReshapeFunc( self._reSize )
        
        # keys
        glutIgnoreKeyRepeat( 1 )
        glutKeyboardFunc(   self._keyDn  )
        glutKeyboardUpFunc( self._keyUp  )
        glutSpecialFunc(    self._keyDnS )
        glutSpecialUpFunc(  self._keyUpS )
        
        
    def prep( self ):
        pass
        
        
    def exe( self ):
        glutMainLoop()

        
    def end( self ):
        # graceful exit cb
        pass

        
