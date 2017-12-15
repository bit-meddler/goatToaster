""" primative.py

Class of Geometric and logical Primatives.

primative -> Class prototype & Xform
Displayable -> Something that can be displayed
GeoGrid(Displayable) -> Floor grid
GeoCube(Displayable) -> Basic cubeube

Logical -> an invisible scene element, ut one which may provide a scene service
Camera -> scene camera
"""
from OpenGL.GL import *
import OpenGL.GLUT

import numpy as np

import gtMath as GM
import chromaTool as CT
import gtHelpers

class Primative( object ):
    """
        Note on X-Form.
        This is a transformation matrix like:
        Rxx Ryx Rzx Tx
        Rxy Ryy Rzy Ty
        Rxz Ryz Rzz Tz
        0   0   0   1
        
        but OpenGL likes: 
        Rxx Rxy Rxz 0
        Ryx Ryy Ryz 0
        Rzx Rzy Rzz 0
        Tx  Ty  Tz  1
        
        so X.T will do it.  see extensive descussion
        https://www.opengl.org/discussion_boards/showthread.php/123437-glMultMatrixf%28GLfloat-%2Am-%29/page5
        
    """
    def __init__( self, name, gt_parent )
        self.X = np.eye( 4, dtype=GM.FLOAT )
        self.dirty = False
        self.name = name
        self._p = gt_parent
        # overidable
        self.id = 0
        
        
class Displayable( Primative ):
    AX_VTS = np.array( ( (0., 0., 0.),
                         (1., 0., 0.),
                         (0., 1., 0.),
                         (0., 0., 1.) ), dtype=GM.FLOAT )
    AX_IDX = ( (0,1), (0,2), (0,3) )
    AX_COL = ( (1., 0., 0.), (0., 1., 0.), (0., 0., 1.) )
    
    LABEL_FONT = "H10"
    
    def __init__( self, name, gt_parent ):
        super( Displayable, self ).__init__( name, parent )
        self.setName( name )
        # gl VBO stuff
        self._VBO = None
        # Overidable
        self._label_os   = (2.5, 2.5, 0.) # Label Offset
        self._draw_scale = 1.0 # draw scale
        self._view_yes   = 0 # forse show view filter
        self._view_no    = 0 # force hide View Filter
        self._my_filter  = 0 # cache overriden view filter

    def setName( self, name ):
        self.name = name
        self._name_extents = self._p.textExtents( name, LABEL_FONT )
        
        
    def draw( self, filters ):
        # apply overrides
        self._my_filter = filters | self._view_yes
        self._my_filter = self._my_filter & ~self._view_no
        # draw axis
        if self._my_filter & self._p.VIEW_AXIS:
            # Transform to position
            glPushMatrix()
            glMultMatrixf( self.X.T )
            # draw
            tmp = AX_VTS * self._draw_scale
            for (i,j), col in zip( self.AX_IDX, AX_COL ):
                glColour3f( col )
                glBegin( GL_LINES )
                glVertex2f( tmp[i] )
                glVertex2f( tmp[j] )
                glEnd()
            # done
            glPopMatrix()
        # draw Label
        if self._my_filter & self._p.VIEW_LABELS:
            t = self.X[3:,3]
            t += self._label_os
            glRasterPos3f(*t)
			GLUT.glutBitmapString(self.font, name)
        
        
    def vboInit( self ):
        self._VBO = GLuint( 0 )
        glGenBuffers( 1, self._VBO )
        self._VBO = self._VBO.value
        glBindBuffer( GL_ARRAY_BUFFER_ARB, self._VBO )
        
        
    def vboPopulate( self, buff_data, vbo_mode=GL_STATIC_DRAW ):
        # https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBufferData.xhtml#description
        # GL_STATIC_DRAW will be most popular
        glBufferData( GL_ARRAY_BUFFER, buff_data.nbytes, buff_data, vbo_mode )
        glBindBuffer( GL_ARRAY_BUFFER_ARB, self._VBO )
        glVertexPointer( 3, GL_FLOAT, 0, None )
        
        
    def vboDestroy( self ):
        glDeleteBuffers(1, GLuint( self._VBO ) )
        
        
class FloorGrid( Displayable ):

    def __init__( self, mjr_dims=(3,3) mjr_spacing=50., mnr_spacing=25., gt_parent ):
        super( FloorGrid, self).__init__( "", gt_parent )
        # Don't draw axis or label
        self._view_no = self._p.VIEW_AXIS | self._p.VIEW_LABELS
        # stash settings
        self.mjr_dims = mjr_dims
        self.mjr_spacing = mjr_spacing
        self.mnr_spacing = mnr_spacing
        # calculate junctions of Major lines
        v,i,c,a = gtHelpers.makeGrid( self.mjr_dims[0], self.mjr_dims[1],
                                      self.mjr_spacing, lambda f1,f2:(f1, 0.01, f2) )
        self._verts = v
        self._grid_idx = i
        self._floor_idx = c
        self._axis_x = a[0]
        self._axis_z = a[1]
        # do vbbo
        self.vboInit()
        self.vboPopulate( self._verts )
        
        #Minor lines, TODO
        # set colour
        self._col_mjr   = CT.web24f( self._p.COLOURS["GRID"][0], 1.0  )
        self._col_floor = CT.web24f( self._p.COLOURS["FLOOR"][0], 1.0 )
        
        
    def draw( self ):
        # Omiting super call - no axis or name for floor
        # setup for drawing
        glEnable( GL_BLEND )
		# Bind verts into VBO
        # Draw floor
        pos = self.X[:3,3]
        glColor4f( self._col_floor )
        glTranslate( *pos )
		# draw a quad
        glEnableClientState( GL_VERTEX_ARRAY )
        glDrawElementsui( GL_QUADS, self._floor_idx )
        # Draw Gridlines MJR
		glColor3f( self._col_mjr )
		glLineWidth( 1 )
		# draw lines
        glDrawElementsui( GL_LINES, self._grid_idx )
        # Reset GL OPTS
        glDisableClientState( GL_VERTEX_ARRAY )