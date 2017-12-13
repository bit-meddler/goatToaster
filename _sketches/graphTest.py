""" Graph experiments
    Based on 'DSA for Game Devs' p360~390
"""
import copy

class Graph( object ):
    
    def __init__( self, max_verts ):
        self._max_verts = max_verts
        self.clear()

    def _resetVisits( self ):
        self._visit = [ 0 for i in xrange( self._max_verts ) ]

    def clear( self ):
        self._verts = []
        self._visit = []
        self._revLut = {}
        self._resetVisits()
        self._ajmx  = [ [ 0 for i in xrange( self._max_verts ) ] \
                            for j in xrange( self._max_verts ) ]

    def copy( self, other ):
        self._verts  = copy.deepcopy( other._verts  )
        self._visit  = copy.deepcopy( other._visit  )
        self._revLut = copy.deepcopy( other._revLut )
        self._ajmx   = copy.deepcopy( other._ajmx   )
        
    def push( self, node ):
        num_verts = len( self._verts )
        assert( num_verts <= self._max_verts )
        self._verts.append( node )
        idx = num_verts + 1
        self._revLut[ node ] = idx
        return idx

    def attach( self, directed, from_vert, to_vert ):
        self._ajmx[from_vert][to_vert] = 1
        if not directed:
            self._ajmx[from_vert][to_vert] = 1

    def remove( self, node ):
        if not node in self._revLut:
            return False
        
        idx = self._revLut[ node ]
        numVerts = len( self._verts )
        # remove other links
        for i in xrange( numVerts ):
            if i==idx:
                continue
            self._ajmx[i].pop( idx )
        # remove vert
        self._ajmx.pop( idx )
        self._verts.pop( idx )
        # renumber Lut
        self._revLut = {}
        for i, n in enumerate( self._verts ):
            self._revLut[n] = i
        return True

    def getNextUnvisited( self, node_index ):
        for i in xrange( len( self._verts ) ):
            if (self._ajmx[node_index][i] > 0) and (self._visit[i] < 1):
                return i
        return -1

    def getNoParent( self, offset=0 ):
        numVerts = len( self._ajmx )
        found = False
        for i in xrange( offset, numVerts ):
            found = False
            for j in xrange( numVerts ):
                if( self._ajmx[i][j] > 0 ):
                    found = True
                    break
            if found:
                return i
        return -1

    def dfs( self, start, end ):
        print "starting DFS at {} looking for {}".format( self._verts[start], self._verts[end] )
        visitStack = []
        visitStack.append( start )
        self._visit[ start ] = 1
        
        while( len( visitStack ) > 0 ):
            test_idx = self.getNextUnvisited( visitStack[-1] )
            print "Looking at {}".format( self._verts[ test_idx ] )
            if test_idx < 0:
                visitStack.pop()
            else:
                self._visit[test_idx] = 1
                visitStack.append( test_idx )

            if( test_idx == end ):
                self._resetVisits()
                return True

        self._resetVisits()
        return False

    def bfs( self, start, end ):
        print "Starting BFS at {} looking for {}".format( self._verts[start], self._verts[end] )
        self._visit[ start ] = 1
        visitQueue = []
        visitQueue.insert( 0, start )

        while( len( visitQueue ) > 0 ):
            test_idx = visitQueue.pop()
            print "Looking at {}".format( self._verts[test_idx] )
            if( test_idx==end ):
                self._resetVisits()
                return True
            new_idx = self.getNextUnvisited( test_idx )
            while( new_idx>=0 ):
                self._visit[ new_idx ] = 1
                visitQueue.insert( 0, new_idx )
                new_idx = self.getNextUnvisited( test_idx )
                
        self._resetVisits()
        return False

    def mst(self, start=0):
        ret = ""
        self._visit[ start ] = 1

        visitStack = []
        current, next = -1, -1

        visitStack.append( start )

        while( len(visitStack) > 0 ):
            current = visitStack[-1]
            next = self.getNextUnvisited( current )

            if( next < 0 ):
                visitStack.pop()
            else:
                self._visit[next] = 1
                visitStack.append( next )
                ret += "{}-{} ".format(
                    self._verts[ current ],
                    self._verts[ next ] )

        self._resetVisits()
        return ret

    def topoSort( self ):
        cyclic = False
        ret = []
        # copy to temp Graph
        temp = Graph( len( self._verts ) )
        temp.copy( self )

        # do sort
        while( len( temp._verts ) > 0 ):
            vert = temp.getNoParent()
            print vert
            if( vert < 0 ):
                cyclic = True
                break
            node = temp._verts[vert]
            ret.insert(0, node)
            temp.remove( node )
        return ret
    
# test
demoGraph = Graph(6)
demoGraph.push('A')
demoGraph.push('B')
demoGraph.push('C')
demoGraph.push('D')
demoGraph.push('E')
demoGraph.push('F')

demoGraph.attach(False, 0, 2) # A-C
demoGraph.attach(False, 0, 3) # A-D
demoGraph.attach(False, 1, 4) # B-E
demoGraph.attach(False, 2, 5) # C-F

print demoGraph.dfs(0,5)
print demoGraph.dfs(0,4)
print demoGraph.dfs(5,3)

print demoGraph.bfs(0,5)
print demoGraph.bfs(0,4)
print demoGraph.bfs(5,3)

print demoGraph.mst()

# Tests with a DAG

demoGraph.clear()

demoGraph.push('A')
demoGraph.push('B')
demoGraph.push('C')
demoGraph.push('D')
demoGraph.push('E')
demoGraph.push('F')

demoGraph.attach(True, 0, 1) # A-B
demoGraph.attach(True, 0, 2) # A-C
demoGraph.attach(True, 1, 3) # B-D
demoGraph.attach(True, 2, 4) # C-E
demoGraph.attach(True, 3, 4) # D-E
demoGraph.attach(True, 4, 5) # E-F

print demoGraph.bfs(0,3)
print demoGraph.mst()
print demoGraph.topoSort()
