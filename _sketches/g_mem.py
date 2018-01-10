# SGI memory mapper
from random import randint
from copy   import deepcopy

# memory activity simulation
class SysSim( object ):
    # consts
    X_PROCNAMES = [ "Apple", "Orange", "Grape", "Mellon", "Eggs", "Bacon", "Spam" ]
    X_PROCSIZES = [     300,     5000,     800,     1000,    400,    2000,    200 ]
    X_LEN       = len( X_PROCSIZES )
    # SYSTEN CONSTANTS
    S_MAXMEM    = sum( X_PROCSIZES ) * 6
    S_AGECLAMP  = 23

    
    @staticmethod
    def tenPCspread( val ):
        haf = val/20
        ret = randint( 0-haf, haf )
        return ret

        
    def __init__( self ):
        self.proc_table = {}
        self.used_mem = 0
        self.PID = -1
        self.state = []
        self.counts = [ 0 for x in range( self.X_LEN ) ]
        
        
    def makeProc( self ):
        # pick proc
        idx = randint( 0, SysSim.X_LEN-1 )
        # make new pid
        new_pid = self.PID + randint(1, 23)
        sz = SysSim.X_PROCSIZES[ idx ]
        sz += SysSim.tenPCspread( sz )
        # add if space
        if (self.used_mem + sz) < SysSim.S_MAXMEM:
            # Add new proc
            self.PID = new_pid
            proc_name = self.X_PROCNAMES[ idx ] + str( self.counts[ idx ] )
            self.proc_table[ self.PID ] = [ proc_name, sz, 0 ]
            self.used_mem += sz
            self.counts[ idx ] += 1
            

    def kill( self, pid ):
        _, sz, _ = self.proc_table[ pid ]
        self.used_mem -= sz
        del self.proc_table[ pid ]


    def initProcs( self ):
        for i in range( randint( 5, 9 ) ):
            self.makeProc()

        
    def updateProcs( self, cmd=None ):
        # simulate aging of procs and mem size changes
        pid_list = deepcopy( self.proc_table.keys() )
        for pid in pid_list:
            data = self.proc_table[ pid ]
            v = randint( 0, 100 )
            if v<12:
                # rare event
                self.kill( pid )
            elif v<72:
                # proc ages
                data[2] += 1
            elif v<88:
                # new proc
                self.makeProc()
            else:
                # memusage changes
                sz = data[1]
                delta = SysSim.tenPCspread( sz )
                if (self.used_mem + delta) < SysSim.S_MAXMEM:
                    data[1] += delta
                    self.used_mem += delta
                    
            if data[2] > SysSim.S_AGECLAMP:
                self.kill( pid )

                
    # some task specific constants...
    ORDER = { "pid":None, "name":0, "size":1, "age":2 }
    TABLE_FORMAT = "{: >3} {: >9} {: >5} {:0>2}"
    def ps( self, sort="pid", order="asc", printing=True ):
        # determine sort order & direction
        keys   = []
        sort   = sort.lower()
        order  = order.lower()
        if not sort in SysSim.ORDER.keys():
            sort = "pid"
        action = SysSim.ORDER[ sort ]
        if action == None:
            keys = self.proc_table.keys()
            keys.sort()
        else:
            keys = sorted( self.proc_table, key=lambda x: self.proc_table[x][action] )
            
        if order == "des":
            keys.reverse()
            
        # emit
        free = SysSim.S_MAXMEM - self.used_mem
        ret = []
        if printing:
            print "Mem {}/{}".format( self.used_mem, SysSim.S_MAXMEM )
            print self.TABLE_FORMAT.format( "PID", "Name", "size", "age" )
            print self.TABLE_FORMAT.format(   "-", "FREE",   free,    "" )
        
        ret.append( (-2, "Total", SysSim.S_MAXMEM, -1) )
        ret.append( (-1,  "Free", free,            -1) )
        for k in keys:
            n, s, a = self.proc_table[ k ]
            if printing:
                print self.TABLE_FORMAT.format( k, n, s, a )
            ret.append( (k, n, s, a) )
        self.state = ret

        
class Compute( object ):
    
    COLOURS = tuple( [ x for x in range( 600, 620 ) ] )
    NUM_COL = len( COLOURS )
    
    def __init__( self, mem_size ):
        self.colour_map = { -1:self.COLOURS[0], 0:self.COLOURS[1] }
        self.usage      = []
        self.mem_size   = mem_size
        self.mem_sizef  = float( mem_size )
        self.colour_cyc = 2

        
    def push( self, data, clamp=900 ):
        
        seen_pids = set( [0, -1] ) # small and free 'seen'
        #        PID,               NAME, SIZE, %
        small = [  0, "Small Processess",    0, 0. ]
        free  = [ -1, "Free", 0, 0 ]
        ret   = [ free, small ]
        
        for pid, name, sz, _ in data:
            if pid < 0:
                if pid == -1:
                    free[2] = sz
                    free[3] = float( sz ) / self.mem_sizef
                continue
            if sz < clamp:
                small[2] += sz
            else:
                seen_pids.add( pid )
                prop = float( sz ) / self.mem_sizef
                ret.append( ( pid, name, sz, prop ) )
                if not pid in self.colour_map:
                    idx = self.colour_cyc % self.NUM_COL
                    self.colour_map[ pid ] = self.COLOURS[ idx ]
                    self.colour_cyc += 1
        prop = float( small[2] ) / self.mem_sizef
        small[3] = prop
        # clean up lost pids from colour map
        lost_pids = set( self.colour_map.keys() ).difference( seen_pids )
        for pid in lost_pids:
            del self.colour_map[ pid ]
        # swap
        self.usage = ret
        
def test():
    my_sys = SysSim()
    my_dat = Compute( SysSim.S_MAXMEM )
    my_sys.initProcs()
    print my_sys.PID, my_sys.used_mem, SysSim.S_MAXMEM
    my_sys.ps()
    my_dat.push( my_sys.state )

    for i in range( 66 ):
        my_sys.updateProcs()
        my_sys.ps( printing = False )
        my_dat.push( my_sys.state )
    my_sys.ps()
    print my_dat.usage, my_dat.colour_map


test()
