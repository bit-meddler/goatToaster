""" Graph experiments
    Based on 'DSA for Game Devs' p360~390
"""
class Graph(object):
    def __init__( self, max_verts ):
        self._max_verts = max_verts
        self._verts = []
        self._visit = []
        self._resetVisits()
        self._ajmx  = [ [ 0 for i in xrange( self._max_verts ) ] \
                            for j in xrange( self._max_verts ) ]

    def _resetVisits( self ):
        self._visit = [ 0 for i in xrange( self._max_verts ) ]
        
    def push( self, node ):
        num_verts = len( self._verts )
        assert( num_verts <= self._max_verts )

        self._verts.append( node )
        return num_verts + 1

    def attach( self, directed, lhs, rhs ):
            self._ajmx[lhs][rhs] = 1
            if not directed:
                self._ajmx[rhs][lhs] = 1

    def getNextUnvisited( self, node_index ):
        for i in xrange( len( self._verts ) ):
            if (self._ajmx[node_index][i] > 0) and (self._visit[i] < 1):
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
