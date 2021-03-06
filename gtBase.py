from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *

import numpy as np
import time
import random
import sys
import logging

from collections import deque

import chromaTool as CT

class TimeMan( object ):
    class Clock( object ):
        def __init__( self ):
            self.acum_d = 0.
            self.last_t = 0.
            self.last_d = 0.
            self.ticks = 0
            self.push = self._first
            
        def _first( self, time ):
            self.last_t = now
            self.ticks = 1
            self.push = self._second
            
        def _second( self, time ):
            self.last_d = time - self.last_t
            self.last_t = now
            self.ticks += 1
            self.acum_d = self.last_d
            self.push = self._push
            
        def _push( self, time ):
            self.last_d = time - self.last_t
            self.last_t = now
            self.ticks += 1
            self.acum_d += self.last_d
            self.acum_d /= 2.
        
        def getFPS( self ):
            if self.ticks > 3:
                return 1. / self.accum_d
            else:
                return 1.
            
            
    def __init__( self ):
        self._clocks = {}
        
        
    def addClock( self, clock ):
        self._clocks[ clock ] = Clock()
        
        
    def push( self, clock_list ):
        now = time.time()
        for clock in clock_list:
            if clock in self._clocks:
                self._clocks[ clock ].push(now)
        
        
    def checkFPS( self, clock ):
        if clock in self._clocks:
            return self._clocks[ clock ].getFPS()
   
   
    def checkDur( self, clock ):
        if clock in self._clocks:
            return self._clocks[ clock ].acum_d
            
   
            
class KeyMan( object ):
    # press states
    DOWN        = 0
    UP          = 1
    
    # key ids
    SPECIAL_OS  = 128
    C_RIGHT     = 100 + SPECIAL_OS
    C_UP        = 101 + SPECIAL_OS
    C_LEFT      = 102 + SPECIAL_OS
    C_DOWN      = 103 + SPECIAL_OS
    PGUP        = 104 + SPECIAL_OS
    PGDN        = 105 + SPECIAL_OS
    HOME        = 106 + SPECIAL_OS
    END         = 107 + SPECIAL_OS
    LEFT_SHIFT  = 112 + SPECIAL_OS
    RIGHT_SHIFT = 113 + SPECIAL_OS
    LEFT_CTRL   = 114 + SPECIAL_OS
    RIGHT_CTRL  = 115 + SPECIAL_OS
    LEFT_ALT    = 116 + SPECIAL_OS
    
    MAX_SLOTS   = 255 # Arbitrary, I'll fix it if there's a crash
    
    def __init__( self ):
        self.history     = np.zeros( (KeyMan.MAX_SLOTS, 2), dtype=np.float64 )
        self.taps        = np.zeros( KeyMan.MAX_SLOTS, dtype=np.uint8 )
        self.active      = np.zeros( KeyMan.MAX_SLOTS, dtype=np.uint8 )
        self._boot       = time.time()
        self.tap_window  = 0.255 # ms
        self.acumulate   = True
        self.last_time   = 0.
        self.last_action = 0
        # registry
        self._rises      = {}
        self._falls      = {}
        self._taps       = {}
        
        # Logging
        self.log = logging.getLogger( __name__ )
        
    def push( self, key_idx, action ):
        ''' deal with keypressess, keyholds, and keytaps.
        '''
        now = time.time()
        last_action = int( not action )
        self.active[ key_idx ] = last_action
        self.last_time = now
        
        # SoA data
        self.history[ key_idx ][ action ] = now
        delta = now - self.history[ key_idx ][ last_action ]
                
        # detect multi-taps
        if (delta < self.tap_window):
            # tapped
            if action==KeyMan.DOWN:
                self.taps[ key_idx ] += 1
                
        else:
            # out of tap window - tap count only cleared on subsequent press!
            if self.acumulate and action==KeyMan.DOWN:
                self.taps[ key_idx ] = 0

        # check registered key events for 'key_idx' and emit CB
        if action : # up==1==True
            if key_idx in self._rises:
                self._rises[key_idx]()
        else:
            if key_idx in self._falls:
                self._falls[key_idx]()
            self.last_action = key_idx
                
        # I might not do it this way. I think a CB expecting to be tapped
        # should check taps[idx] when called (it knows the regidtered idx)
        if self.taps[ key_idx ]>1:
            if key_idx in self._taps:
                self._taps[key_idx]()
        # done
        
    def registerFallingCB( self, key_idx, fcall ):
        self._falls[key_idx] = fcall
        
    def registerRisingCB( self, key_idx, fcall ):
        self._rises[key_idx] = fcall
        
    def registerTapsCB( self, key_idx, fcall ):
        self._taps[key_idx] = fcall
        
        
class HudMan( object ):
    DEFAULT_LIFE = 50

    
    def __init__( self ):
        self.HUD_elements = {}
        self.HUD_display_list = []
        # Logging
        self.log = logging.getLogger( __name__ )
        
    def addElement( self, name, x, y, col=None, life=DEFAULT_LIFE, font="H12" ):
        if name in self.HUD_elements:
            # update x,y ?
            self.HUD_elements[ name ]["POS"] = (x,y)
        else:
            self.HUD_elements[ name ] = {
                "POS"  : (x,y),
                "QUE"  : deque(),
                "TTL"  : 0,
                "COL"  : CT._flexCol( col ),
                "LIFE" : life,
                "TASK" : 0,
                "FONT" : font
            }
            self.HUD_display_list.append( name )
            
            
    def addMsg( self, name, text, overide_col=None, overide_life=None, overide_font=None ):
        if name in self.HUD_elements:
            # overides
            col  = self.HUD_elements[name]["COL"]  if overide_col==None  else overide_col
            ttl  = self.HUD_elements[name]["LIFE"] if overide_life==None else overide_life
            font = self.HUD_elements[name]["FONT"] if overide_font==None else overide_font
            
            # new task, or joining the queue ?
            if self.HUD_elements[name]["TASK"] == 0:
                # new message, set ttl
                self.HUD_elements[name]["TTL"] = ttl
            elif self.HUD_elements[name]["TTL"] < 0:
                # if there is an eternal task, this new one succeeds it
                self.HUD_elements[name]["TTL"] = 0
                
            # add new task
            self.HUD_elements[name]["TASK"] += 1
            self.HUD_elements[name]["QUE"].append( [text, col, ttl, font] )
            
        else:
            print "no HUD group '{}'".format( name )
            
            
    def getNextMsg( self, name ):
        # Get data
        x, y = self.HUD_elements[name]["POS"]
        text, col, _, font = self.HUD_elements[name]["QUE"][0]
        # update ttl
        if self.HUD_elements[name]["TTL"] >= 1:
            self.HUD_elements[name]["TTL"] -= 1
        if self.HUD_elements[name]["TTL"] == 0:
            # TODO: Test Eternal HUD using TTL = -1 
            _ = self.HUD_elements[name]["QUE"].popleft()
            self.HUD_elements[name]["TASK"] -= 1
            # advance to next task, if available & EoL
            if self.HUD_elements[name]["TASK"] > 0:
                ttl = self.HUD_elements[name]["QUE"][0][2]
                self.HUD_elements[name]["TTL"] = ttl
                
        return x, y, text, col, font
        
        
class GLtoast( object ):


    FONTS = {
        "H10": OpenGL.GLUT.GLUT_BITMAP_HELVETICA_10,
        "H12": OpenGL.GLUT.GLUT_BITMAP_HELVETICA_12,
        "H18": OpenGL.GLUT.GLUT_BITMAP_HELVETICA_18,
        "T10": OpenGL.GLUT.GLUT_BITMAP_TIMES_ROMAN_10,
        "T24": OpenGL.GLUT.GLUT_BITMAP_TIMES_ROMAN_24,
        "BM8": OpenGL.GLUT.GLUT_BITMAP_8_BY_13,
        "BM9": OpenGL.GLUT.GLUT_BITMAP_9_BY_15        
    }
    STYLES = {
        "QUADS": GL_QUADS,
        "LINES": GL_LINES,
        "LOOPS": GL_LINE_LOOP,
        "POLYS": GL_POLYGON
    }
    # View Filters
    VIEW_AXIS    = 1
    VIEW_GRID    = 2
    VIEW_CAMERAS = 4
    VIEW_LABELS  = 8
    
    VIEW_FILTERS = {
        "AXIS"    : VIEW_AXIS,
        "GRID"    : VIEW_GRID,
        "CAMERAS" : VIEW_CAMERAS,
        "LABELS"  : VIEW_LABELS,
    }
    
    UP = (0.,1.,0.) # Y-Up!
    
    def __init__( self ):
        self.g_wind = None
        self._glut_opts = GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH
        self._title = None
        self._wh = (640,480)
        self._native_wh = (1920,1280)
        self._min_extents = (300, 50)
        self._bg = (0.0, 0.0, 0.0, 1.0) # default clear colour
        self._native_pos = (0,0)
        self._center = False # force center of panel
        self._ratio_lock = True # lock inital aspect ratio
        self._ext_lock = True # Lock to display min extents
        self._ratio = float(self._wh[0]) / float(self._wh[1])
        self._fov = 45.0
        self._z_clip = ( 0.1, 100.0 )
        self._cam_pos = [ 10., 5., 10. ]
        self._interest = [ 0., 0., 0., ]
        self._key_man = KeyMan()
        self._hud_man = HudMan()
        self._reverseDrawOrder = True
        self.nav_mode = "MAYA" # TODO: "QUAKE" mode (wasd + orbit mouse)
        self._draw_mode = "3D" #????
        self._log_pos = (10,4)
        self.log = logging.getLogger( "GT-Core" )
        self.log.debug( "Goat Toaster STarted" )
        self.rec_list = []
        self.line_list = []
        self.text_list = []
        self._draw_order = ["LINES","RECTS"]
        self._log_pos =(10,18)
        self._log_life = 45
        self._log_col = "#ffffff"
        
        
    def _reSize( self, width, height ):
        # Returns True if resize took place
        old_w, old_h = self._wh
        if width==old_w and height==old_h:
            return False
        lock_w, lock_h = 2, 2
        if self._ext_lock:
            lock_w, lock_h = self._min_extents
        new_h = lock_h if(height<lock_h) else height
        new_w = lock_w if(width<lock_w)  else width
        if new_w==old_w and new_h==old_h:
            return False
        # TODO: fix fixed ratio window
        '''
        not quite right yet
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
        self._ratio = float(self._wh[0]) / float(self._wh[1])
        # TODO: Auto for all HUDs
        self._hud_man.addElement( "LOG", self._log_pos[0], self._log_pos[1] )
        glutReshapeWindow( self._wh[0], self._wh[1] )
        glutPostRedisplay()
        return True
        
        
    def _idle( self ):
        # if [Alt] pressed, mouse clicks are navigation taasks
        self._navigating = (self.nav_mode=="MAYA") and \
                            self._key_man.active[KeyMan.LEFT_ALT]
        
        glutPostRedisplay()
        
        
    def _draw( self ):
        glutSwapBuffers()
        

    def _clear( self )    :
        glClearColor( *self._bg )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
    def paintLists( self, rec_slice=None, line_slice=None ):
        # Draw to back buffer items in the lists
        self.paintText()
        if self._reverseDrawOrder:
            self.rec_list.reverse() # darwin wants front to back drawing order
            self.line_list.reverse()
        else:
            self.doHUD()
            self.paintText()
            
        # Determine slice of lists to use - Experimental
        _r_slice, _l_slice = None, None
        if rec_slice==None:
            _r_slice = slice( 0, len(self.rec_list), None )
        else:
            _r_slice = slice( rec_slice[0], rec_slice[1], None )
        
        if line_slice==None:
            _l_slice = slice( 0, len(self.line_list), None )
        else:
            _l_slice = slice( line_slice[0], line_slice[1], None )
        
        for task in self._draw_order:
            if task == "RECTS":
                for (x, y, w, h, col, mode) in self.rec_list[_r_slice]:
                    self.drawRect2D( x, y, w, h, CT.web23f( col ), mode )
            elif task == "LINES":
                for (x, y, m, n, col) in self.line_list[_l_slice]:
                    self.drawLine2D( x, y, m, n, CT.web23f( col ) )
                    
        if self._reverseDrawOrder:
            self.doHUD()
        self.paintText()


    def paintText( self ):
        for (x, y, text, align, col, font) in self.text_list:
            off = 0
            if align=="LEFT":
                    off = 0
            elif align=="CENTER":
                    _w, _h = self.textExtents( text, font )
                    off = -(_w/2)
            elif align=="RIGHT":
                    _w, _h = self.textExtents( text, font )
                    off = -_w
                    
            self.printTxt( x+off, y, text, CT.web23f(col), font)
            
            
    def _keyDn( self, key, x, y ):
        self._action_native_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.DOWN )
    
    
    def _keyUp( self, key, x, y ):
        self._action_native_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.UP )
        
        
    def _keyDnS( self, val, x, y ):
        self._action_native_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.DOWN )
        
        
    def _keyUpS( self, val, x, y ):
        self._action_native_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.UP )
        
                
    def drawRect2D( self, x, y, w, h, col=None, mode=GL_QUADS ):
        # for HUD and 2D drawing in context piuxel space
        # God Damn Winding order!!!
        gl_col = CT._flexCol( col )
        glColor4f( *gl_col )
        glBegin( mode )

        m, n = x+w, y+h

        glVertex2f(x-1, y)
        glVertex2f(m, y)
        glVertex2f(m, n)
        glVertex2f(x, n)

        if mode==GL_LINES:
            glVertex2f(x, y)
            glVertex2f(x, n)
            glVertex2f(m, y)
            glVertex2f(m, n)
        glEnd()
        
        
    def drawLine2D( self, x, y, m, n, col=None ):
        gl_col = CT._flexCol( col )
        glColor4f( *gl_col )
        glBegin( GL_LINES )
        glVertex2f( x+1, y )
        glVertex2f( m+1, n )
        glEnd()
        
        
    def set2D( self ):
        glViewport( 0, 0, self._wh[0], self._wh[1] )
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0.0, self._wh[0], 0.0, self._wh[1], 0.0, 1.0 )
        
        
    def set3D( self ):
        glViewport( 0, 0, self._wh[0], self._wh[1] )
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        gluPerspective( self._fov, self._ratio, self._z_clip[0], self._z_clip[1] )
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        gluLookAt( *( self._cam_pos + self._interest + self.UP ) )
        
        
    def printTxt( self, x, y, text, col=None, font="H10"):
        gl_col = CT._flexCol( col )
        glColor4f( *gl_col )
        glWindowPos2i( x, y )
        glutBitmapString( self.FONTS[ font ], text )
    
    
    def textExtents( self, text, font="H10" ):
        w = 0
        # glutBitmapLength takes exception to str
        for c in text:
            w += glutBitmapWidth( self.FONTS[ font ], ord(c) )
        h = glutBitmapHeight( self.FONTS[ font ] )
        return (w,h)
        
        
    def doHUD(self):
        # HUD Messages
        for task in self._hud_man.HUD_display_list:
            
            if self._hud_man.HUD_elements[ task ]["TASK"]>0:
                x, y, text, col, font = self._hud_man.getNextMsg( task )
                self.printTxt( x, y, text, col, font )
            
            
    def init( self ):
        # do glut init
        # TODO: refactor to freeglut
        glutInit()
        glutInitDisplayMode( self._glut_opts )
        
        # Get Natove res
        self._native_wh = (glutGet( GLUT_SCREEN_WIDTH  ),
                           glutGet( GLUT_SCREEN_HEIGHT ))
        
        # Guard against requested window size > native
        new_wh = list( self._wh )
        new_wh[0] = min( self._wh[0], self._native_wh[0] )
        new_wh[1] = min( self._wh[1], self._native_wh[1] )
        self._wh = tuple( new_wh )
        
        # auto center
        if self._center:
            pos_x = (self._native_wh[0]-self._wh[0]) / 2
            pos_y = (self._native_wh[1]-self._wh[1]) / 2
            self._native_pos = (pos_x, pos_y)
            
        glutInitWindowSize( self._wh[0], self._wh[1] )
        glutInitWindowPosition( self._native_pos[0], self._native_pos[1] )  
        self.g_wind = glutCreateWindow( self._title )
        
        # Enable GL Options
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        glDepthFunc(GL_LESS) 
    
        # bind std CBs
        # This only works because we're interpreted, and this function is called
        # after the object is constructed, and the derived method has superceeded
        # it's prototype.
        glutDisplayFunc( self._draw   )
        glutIdleFunc(    self._idle   )
        glutReshapeFunc( self._reSize )
        
        # keys
        glutIgnoreKeyRepeat( 1 )
        glutKeyboardFunc(   self._keyDn  )
        glutKeyboardUpFunc( self._keyUp  )
        glutSpecialFunc(    self._keyDnS )
        glutSpecialUpFunc(  self._keyUpS )
        
        # deal with platform differences
        if sys.platform=="darwin":
            self._reverseDrawOrder = True
            self._draw_order.reverse()
            
        self._hud_man.addElement( "LOG", self._log_pos[0], self._wh[1]-self._log_pos[1],
                                         CT.web23f(self._log_col), self._log_life )
        
        
    def prep( self ):
        pass
        
        
    def exe( self ):
        glutMainLoop()

        
    def end( self ):
        # graceful exit cb, if only it worked
        pass

        
