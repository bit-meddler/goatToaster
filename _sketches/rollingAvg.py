import math

class rollingAvg( object ):
    
    def __init__( self ):
        self.num  = 0
        self.mean = 0.0
        self._sqr = 0.0

    def push( self, val ):
        self.num  += 1
        vmm        = val - self.mean # value minus mean
        new_mean   = self.mean + (vmm / self.num)
        self._sqr += ( vmm**2 )
        self.mean  = new_mean
        
        
    def forget( self, val ):
        if(  self.num == 0 ):
            # nothing to do
            return
        # only 1 value, so clear
        if( self.num == 1 ):
            self.num  = 0
            self.mean = 0.0
            self._sqr = 0.0
            return
        # safe to do computation
        old_mean   = (self.num * (self.mean - val)) / (self.num - 1)
        self._sqr -= (val - self.mean) * (val - old_mean)
        self.mean  = old_mean
        self.num  -= 1
        

    def variance( self ):
        if( self.num>1 ):
            return ( self._sqr / self.num )
        else:
            return 0.0
            

    def varianceUnbiased( self ):
        if( self.num>1 ):
            return ( self._sqr / (self.num-1) )
        else:
            return 0.0
            

    def standardDeviation( self ):
        return math.sqrt( self.variance() )


    def standardDeviationUnbiased( self ):
        return math.sqrt( self.varianceUnbiased() )


    def __repr__( self ):
        return "Rolling Mean {} with SD {} from {} samples".format(
                self.mean, self.standardDeviation(), self.num )
                
                
if __name__ == "__main__":
    roll = rollingAvg()
    import random
    
    for i in xrange( 100 ):
        roll.push( i )
        print i, repr( roll )