"""
    Kicking around some node graph Ideas...
    
"""
class Node( object ):

    DIR_IN  =  1
    DIR_BI  =  0
    DIR_OUT = -1
    DIR_LUT = {
        DIR_IN  :">-",
        DIR_BI  :"<>",
        DIR_OUT :"->",
    }
    
    
    def __init__( self, name, title ):
        self.inner_name = name
        self.display_name = title
        self.slots = {}
        self.slotOrder = []
        self.children = []
        self.parents = []
        self.dirty = False
        
        
    def addSlot( self, name, type, direction ):
        if not name in self.slots:
            self.slots[ name ] = None
            self.slotOrder.append( name )
        self.slots[ name ] = [ type, direction ]
        
        
    def invalidate( self ):
        self.dirty = True
        for child in self.children:
            child.invalidate()
    
    
    def show( self ):
        print "'{}' ({})".format( self.display_name, self.inner_name )
        for slot in self.slotOrder:
            t, d = self.slots[slot]
            print "\t{: >16}:{: >9} {}".format( slot, t, self.DIR_LUT[d] )
        print "\nDownstream:"
        for c in self.children:
            print "\t{}".format( c.display_name )
        print "\nUpstream:"
        for p in self.parents:
            print "\t{}".format( p.display_name )
                
                
class Scene( object ):

    def __init__( self ):        
        self.nodes = {}
        self.ids = 1000
        self.links = {}

        
    def addNode( self, name, title ):
        inner_name = "{}_{}".format( name.lower(), self.ids )
        self.ids += 1
        node = Node( inner_name, title )
        self.nodes[ inner_name ] = node
        return node
        
        
    def connect( self, source_name, source_slot, target_name, target_slot ):
    
        if not source_name in self.nodes:
            return
        if not target_name in self.nodes:
            return
            
        if not source_slot in self.nodes[ source_name ].slots:
            return
        if not target_slot in self.nodes[ target_name ].slots:
            return
        
        if self.nodes[ source_name ].slots[ source_slot ][1] > 0:
            return
        if self.nodes[ target_name ].slots[ target_slot ][1] < 0:
            return
        
        # finally, connect them
        self.nodes[ source_name ].children.append( self.nodes[ target_name ] )
        self.nodes[ target_name ].parents.append( self.nodes[ source_name ] )
        self.links[ "{}.{}".format( source_name, source_slot ) ] = "{}.{}".format( target_name, target_slot )
        self.nodes[ target_name ].invalidate()
        
        
    def show( self ):
        for _,n in self.nodes.iteritems():
            n.show()
            print "--------------------------------------------"
            
            
if __name__ == "__main__":
    sg = Scene()
    blur = sg.addNode( "blur", "Blur Node" )
    blur.addSlot( "frame_in", "IMAGE", Node.DIR_IN )
    blur.addSlot( "frame_out", "IMAGE", Node.DIR_OUT )
    blur.addSlot( "radius", "FLOAT", Node.DIR_BI )
    read = sg.addNode( "read", "Read File" )
    read.addSlot( "frame_out", "IMAGE", Node.DIR_OUT )
    sg.connect( read.inner_name, "frame_out", blur.inner_name, "frame_in" )
    sg.show()