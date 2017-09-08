"""
Vector and matrix maths for manipulating 3D stuffs, OpenGL Drawing, The usual.


"""
import numpy as np

# types, incase I want to test f64 or different width ints
FLOAT = np.float32
INT   = np.int32


def composeRot( yaw, pitch, roll ):
    ''' expects degrees, R-order YXZ
        Right Handed coord system
        Y = Yaw != y-axis
        cf. Parent 'Computer Animation Complete' pp48
        
        OK dust off your matrix maths...
        Z.X.Y -> Z.X  (Z.X).Y
        
        |cz, -sz,  0|   |1,  0,   0|   |cz, -sz.cx,  sz.sx|
        |sz,  cz,  0| . |0, cz, -sx| = |sz,  cz.cx, -cz.sx| 
        | 0,   0,  1|   |0, sx,  cx|   | 0,     sx,     cx|
         
        |cz, -sz.cx,  sz.sx|     | cy, 0, sy|
        |sz,  cz.cx, -cz.sx|  .  |  0, 1,  0|
        | 0,     sx,     cx|     |-sy, 0, cy|
         
         
        | cz.cy - sz.sx.sy,   -sz.cx,   cz.sy + sz.sx.cy|
        | sz.cy + cz.sx.sy,    cz.cx,   sz.sy - cz.sx.cy|
        |-cx.sy,                  sx,   cx.cy           |
        
        now they are just numbers, they are communicative, so we can rearrange & simplify
        | cz.cy - sz.sxsy,   -sz.cx,   cz.sy + sz.sxcy|
        | sz.cy + cz.sxsy,    cz.cx,   sz.sy - cz.sxcy|
        |-cx.sy,                 sx,   cx.cy          | 
        
        not a lot, no
        
    '''
    rads = np.radians( (yaw, pitch, roll) )
    ( sy, sx, sz ) = np.sin( rads )
    ( cy, cx, cz ) = np.cos( rads )
    
    sxsy = sx * sy
    sxcy = sx * cy
    
    ret = [
        [ cz*cy - sz*sxsy,   -sz*cx,   cz*sy + sz*sxcy],
        [ sz*cy + cz*sxsy,    cz*cx,   sz*sy - cz*sxcy],
        [-cx*sy,                 sx,   cx*cy          ]
    ]
    
    return np.array( ret, dtype=FLOAT )
    
    
if __name__ == "__main__":
    print "Test compose Rot Mat"
    print composeRot( 44., 0., 0. )
    print composeRot( 45., 0., 0. )
    print composeRot( 90., 90., 0. ) # here be gimbels
    print composeRot( 89., 89., 0. )
    