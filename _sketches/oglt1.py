from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import numpy as np
import time

def web23f( val, cache={} ):
    if val in cache:
        return cache[val]
    
    v = ""
    if( len( val ) > 6 ):
        if( val[0] == "#" ):
            v = val[1:7]
        else:
            v = val[:6]
    elif( len( val ) < 6 ):
        # append 0 and hope for the best
        v = val + "0"
    else:
        v = val
    r = float( int( v[0:2], 16 ) ) / 255.
    g = float( int( v[2:4], 16 ) ) / 255.
    b = float( int( v[4:6], 16 ) ) / 255.
    ret = (r, g, b)
    cache[val] = ret
    return ret

        
class KeyMan( object ):
    DOWN = 0
    UP   = 1
    
    LEFT_SHIFT = 1112
    LEFT_CTRL  = 1114
    LEFT_ALT   = 1116
    
    def __init__( self ):
        self.activity = {}
        self.history = {}
        self.active = set()
        self._boot = time.time()
        
    def push( self, key, action ):
        now = time.time()
        if action==KeyMan.DOWN:
            self.active.add( key )
        else:
            self.active.remove( key )
            
        delta = 0
        if key not in self.history: self.history[ key ]=[]
        if key in self.activity:
            delta = now - self.activity[ key ]
            hl = self.history[ key ]
            hl.append( (now, delta) )
            del( self.activity[ key ] )
            if( len( hl ) > 1 ):
                print hl
                pass
        else:
            self.activity[ key ] = now
        print delta, key, action

        
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
        
    def drawRect2D( self, x, y, w, h, col=(.5,.0,.0) ):
        glColor3f( col[0], col[1], col[2] )
        glBegin( GL_QUADS )
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        
    def drawPoly2Dtest(self):
        r, g, b = web23f( "#32CD32" )
        glColor3f( r, g, b )
        glBegin(GL_POLYGON)
        glVertex2i( 100, 10 )
        glVertex2i( 100, 50 )
        glVertex2i(  99, 51 )
        glVertex2i(  98, 54 )
        glVertex2i(  97, 51 )
        glVertex2i(  96, 47 )
        glVertex2i(  95, 50 )
        glVertex2i(  94, 51 )
        glVertex2i(  93, 53 )
        glVertex2i(  92, 45 )
        glVertex2i(  91, 58 )
        glVertex2i(  90, 56 )
        glVertex2i(  50, 51 )
        glVertex2i(  50, 10 )
        glEnd()
        
    def test3D( self ):
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK,  GL_FILL)
            
        r, g, b = web23f( "#123456" )
        glColor3f( r, g, b )
        glPushMatrix()
        glTranslatef(-1.5, 2.0, -6.0)
        
        glBegin(GL_POLYGON)
        glVertex3f(0.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, 0.0)
        glVertex3f(-1.0, -1.0, 0.0)
        glEnd()

        r, g, b = web23f( "#778899" )
        glColor3f( r, g, b )
        glTranslatef(3.0, 2.0, 0.0)

        glBegin(GL_QUADS)
        glVertex3f(-1.0, 1.0, 0.0)
        glVertex3f(1.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, 0.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glEnd()
        glPopMatrix()
        
    def drawPeg( self, x, y, z ):
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK,  GL_FILL)
        
        glPushMatrix()
        glTranslatef( x, y, z )
        glRotate( self.y, 0, 1, 0)
        r, g, b = web23f( "#FFD700" )
        glColor3f( r, g, b )
        glBegin(GL_POLYGON)
        
        # WSU
        glVertex3f(  0.0,  0.0,  0.7 )
        glVertex3f(  0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  1.7,  0.0 )
        # NWU
        glVertex3f( -0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  0.0,  0.7 )
        glVertex3f(  0.0,  1.7,  0.0 )
        # NUE
        glVertex3f( -0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  1.7,  0.0 )
        glVertex3f(  0.0,  0.0, -0.7 )
        # ESU
        glVertex3f(  0.0,  0.0, -0.7 )
        glVertex3f(  0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  1.7,  0.0 )
        # SWD
        glVertex3f(  0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  0.0,  0.7 )
        glVertex3f(  0.0, -1.7,  0.0 )
        # WND
        glVertex3f(  0.0,  0.0,  0.7 )
        glVertex3f( -0.7,  0.0,  0.0 )
        glVertex3f(  0.0, -1.7,  0.0 )
        # DNE
        glVertex3f(  0.0, -1.7,  0.0 )
        glVertex3f( -0.7,  0.0,  0.0 )
        glVertex3f(  0.0,  0.0, -0.7 )
        # DES
        glVertex3f(  0.0, -1.7,  0.0 )
        glVertex3f(  0.0,  0.0, -0.7 )
        glVertex3f(  0.7,  0.0,  0.0 )

        glEnd() 
        glPopMatrix()
        
    def test3DD( self ):
        glPolygonMode(GL_FRONT, GL_LINE)
        glPolygonMode(GL_BACK,  GL_LINE)
        
        glPushMatrix()
        glTranslatef( 5.0, 0.0, -5.0 )
        
        glRotate(self.x, 1, 0, 0)
        glRotate(self.y, 0, 1, 0)
        glRotate(self.z, 0, 0, 1)

        glBegin(GL_QUADS)
        glColor3f(0.0,1.0,0.0)
        glVertex3f( 1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f( 1.0, 1.0, 1.0)
        glColor3f(1.0,0.5,0.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f( 1.0,-1.0,-1.0)
        glColor3f(1.0,0.0,0.0)
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0) 
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glColor3f(1.0,1.0,0.0)
        glVertex3f( 1.0,-1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f( 1.0, 1.0,-1.0)
        glColor3f(0.0,0.0,1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glColor3f(1.0,1.0,1.0)
        glVertex3f( 1.0, 1.0,-1.0)
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0,-1.0)
        glEnd()
        glPopMatrix()
    
    def testBall( self ):
        glPushMatrix()
        glTranslatef( -10.0, 0.0, -6.0)
        glMaterialfv( GL_FRONT, GL_DIFFUSE, web23f( "#778899" ) )
        glutSolidSphere( 3, 20, 20 )
        glPopMatrix()
    
    def set2D( self ):
        glViewport( 0, 0, self._wh[0], self._wh[1] )
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0.0, self._wh[0], 0.0, self._wh[1], 0.0, 1.0 )
        glMatrixMode( GL_MODELVIEW )
     

    def set3D( self ):
        glViewport( 0, 0, self._wh[0], self._wh[1] )
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        ratio = float(self._wh[0]) / float(self._wh[1])
        gluPerspective( self._fov, ratio, self._z_clip[0], self._z_clip[1] )
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        gluLookAt( 0., 3., 20.,  0.,0.,0.,  0.,1.,0. )
        
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
        self.x += 0.1
        self.y += 0.01
        self.z += 0.001
        glutPostRedisplay()
        #self._draw()
        
    def _draw( self ):
        # gl Reset
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
        # Draw Stuff
        #self.set2D()
        #self.drawRect2D( 10, self._wh[1] - 15, 50, 30 )
        
        self.set3D()
        self.test3D()
        self.testBall()
        self.test3DD()
        self.drawPeg( 0., 0., 0, )
        
        self.set2D()
        self.drawRect2D( 10, 10, 100, 100, web23f("556B2F") )
        self.drawPoly2Dtest()
        # swap
        glutSwapBuffers()   

    def _keyDn( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.DOWN )
    
    def _keyUp( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.UP )
        
    def _keyDnS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + 1000, KeyMan.DOWN )
        
    def _keyUpS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + 1000, KeyMan.UP )
        
    def init( self ):
        # do glut init
        glutInit()
        glutInitDisplayMode( self._glut_opts )
        
        self._native_wh = (glutGet( GLUT_SCREEN_WIDTH ), glutGet( GLUT_SCREEN_HEIGHT ))
        
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
        self.x = 0.
        self.y = 0.
        self.z = 0.
        
    def exe( self ):
        glutMainLoop()

    def end( self ):
        # graceful exit cb
        pass
    
myApp = GLtoast()
myApp._glut_opts = GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH
myApp._title = "Hello OpenGL"
myApp._center = True

myApp.init()
myApp.prep()
myApp.exe()
