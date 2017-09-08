__author__ = 'RichH'

import os

def fragmentFilePath( file_path ) :
    """ returns path, name, and extension of an FQ path """
    path_name, ext = os.path.splitext( file_path )
    path_part = os.path.dirname( path_name )
    name_part = os.path.basename( path_name )
    return path_part, name_part, ext

def openMkdir( file_name, mode='r' ):
    """ Open a file, making the path to the file if it doesn't exist already """
    directory = os.path.dirname( file_name )
    if not os.path.exists( directory ):
        os.makedirs( directory )
    return open( file_name, mode )

def strider( task, strides ):
    """ Step through a 1D slicable, returning 'width' long chunks, then skipping
        'skip' long steps of the task.  if more than one imperative is passed
        (in a tuple) we cycle through their instructions until we reach the end
        of the task.
    """
    off = 0 # offset
    sz = len( task ) # size of task
    my_strides = strides if( type( strides[0] ) == tuple ) else (strides,)
    while( True ):
            for stride in my_strides:
                    width, skip = stride
                    yield task[ off : off+width ]
                    off += (width+skip)
                    if( off >= sz ): return

def getFileTimeDigest( file ):
    """ return timestamps of a file. Created, Modified, Accessed """
    c_time = os.path.getctime( file )
    m_time = os.path.getmtime( file )
    a_time = os.path.getatime( file )
    return c_time, m_time, a_time
    
    
if __name__ == "__main__":
    print( "strider test" )
    l = ["Alfa", "Bravo", "Charlie", "Delta", "Echo",
         "Foxtrot", "Golf", "Hotel", "India", "Juliett",
         "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",
         "Quebec", "Romeo", "Sierra", "Tango", "Uniform",
         "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"
    ]
    tests = ( (2,2), ((1,2),(2,1)), ((1,2),(1,1),(2,1) )  )
    for test in tests:
        print( "test {}".format( test ) )
        for r in strider( l, test ):
            print(r)
