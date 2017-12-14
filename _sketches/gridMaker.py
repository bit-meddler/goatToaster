import numpy as np

def makeGrid( x, z, scale, shuffle=lambda f1,f2: (f1,0.,f2) ):
    """
        Make a grid
        if you are not in Y-Up, or are using the grid for something else
        (line-up of a camera??), or want a specific y plain to arrange the
        grid on, just make a new lambda
        eg lambda f1, f2: (f1,f2,0.)
           lambda f1, f2: (f1,0.02,f2)

        I assume we're counting lo to high, so assert on a -ve scale
        
    """
    assert( scale > 0 )
    # work out Mjr line stride
    x_cadence = range( -x, 0 )
    x_cadence.extend( range( 0, x+1 ) )
    z_cadence = range( -z, 0 )
    z_cadence.extend( range(0, z+1) )
    num_x = (x*2) + 1
    num_z = (z*2) + 1
    num = ( num_x * num_z )
    t_vts = []
    for x_ in x_cadence:
        for z_ in z_cadence:
            t_vts.append( shuffle(x_,z_) )
    # indexs of the verts
    idx_str = np.arange( num, dtype=np.int ).reshape( (num_z, num_x) )
    # form up a list of pairs of vert indexs to draw a line between
    drawpairs = []
    # do lines in x
    for i in range( num_z ):
        for j in range( num_x-1 ):
            drawpairs.append( idx_str[i][j] )
            drawpairs.append( idx_str[i][j+1] )
    # flip & do lines in z
    idx_str = idx_str.T
    for i in range( num_x ): # filp loop ends!
        for j in range( num_z-1 ):
            drawpairs.append( idx_str[i][j] )
            drawpairs.append( idx_str[i][j+1] )
    # make np
    idxs = np.array( drawpairs, dtype=int )            
    vts = np.array( t_vts, dtype=np.float )
    vts *= scale
    # some other useful info (perimiter of floor, the cardinal axis)
    corners = (0,(num_x*(num_z-1)), num-1, num_x-1)
    center = num_x*z + x
    axis = ( (center, num-z-1), (center, center+z) )
    return vts, idxs, corners, axis

def showLine( verts, i, j ):
    print "{}->{}".format( verts[i], verts[j] )

v,i,c,a = makeGrid( 5, 4, 200. )
print len( v )
print i
print c
print a
for A,B in a:
    showLine( v, A, B )
    
v,i,c,a = makeGrid( 3, 3, 50. )
print len(v)
print i
print c
print a
for A,B in a:
    showLine( v, A, B )
