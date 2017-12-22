"""
    Kicking around some node graph Ideas...
    
"""
class Node( object ):

    DIR_IN  =  1
    DIR_BI  =  0
    DIR_OUT = -1
    DIR_LUT = {
        DIR_IN  : ">-",
        DIR_BI  : "<>",
        DIR_OUT : "->",
    }
    
    GRP_INT = 1
    GRP_UI  = 2
    GRP_LUT = {
        GRP_INT : "Internal",
        GRP_UI  : "Interface"
    }
    
    def __init__( self, name, title ):
        self.inner_name = name
        self.display_name = title
        self.slots = {}
        self.slotOrder = []
        self.children = []
        self.parents = []
        self.dirty = False
        
        
    def addSlot( self, name, type, group, direction ):
        if not name in self.slots:
            self.slots[ name ] = None
            self.slotOrder.append( name )
        self.slots[ name ] = [ type, group, direction ]
        
        
    def invalidate( self ):
        self.dirty = True
        for child in self.children:
            child.invalidate()
            
            
    def process( self ):
        self.dirty = False
    
    
    def show( self ):
        print "'{}' ({}) [{}Dirty]".format( self.display_name, self.inner_name,
                                          "" if self.dirty else "Not " )
        slots_ui  = ""
        slots_int = ""
        for slot in self.slotOrder:
            t, g, d = self.slots[slot]
            if( g == self.GRP_UI ):
                slots_ui += "\t{: >16}:{: >9} {}\n".format( slot, t, self.DIR_LUT[d] )
            else:
                slots_int+= "\t{: >16}:{: >9} {}\n".format( slot, t, self.DIR_LUT[d] )
        print "Internal"
        print slots_int
        print "Interface"
        print slots_ui
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
        self.visited = set()

        
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
        
        if self.nodes[ source_name ].slots[ source_slot ][2] > Node.DIR_BI:
            return
        if self.nodes[ target_name ].slots[ target_slot ][2] < Node.DIR_BI:
            return
        
        # finally, connect them
        self.nodes[ source_name ].children.append( self.nodes[ target_name ] )
        self.nodes[ target_name ].parents.append( self.nodes[ source_name ] )
        self.links[ "{}.{}".format( source_name, source_slot ) ] = "{}.{}".format( target_name, target_slot )
        self.nodes[ target_name ].invalidate()
        
        
    def show( self ):
        print "Nodes"
        for _,n in self.nodes.iteritems():
            n.show()
            print "-"*37
        print "Edges"
        for source, target in self.links.iteritems():
            print "{} -> {}".format( source, target )
            
            
    def _findNoParent( self ):
        for _,n in self.nodes.iteritems():
            if len( n.parents ) == 0:
                if not n in self.visited:
                    self.visited.add( n )
                    return n
        return None
        
        
    def walk( self ):
        """ Walk the Graph.
        """
        visited = set()
        walk_order = []
        orphens = []
        examine_list = []
        task = self._findNoParent()
        if task != None:
            examine_list.append( task )
        while( len(examine_list)>0 ):
            test = examine_list.pop()
            if test in visited:
                continue
            if len(test.children)<1 and len(test.parents)<1 :
                orphens.append( test )
                visited.add( c )
            else:
                walk_order.insert( 0, test )
                for c in test.children:
                    if c in visited:
                        pass
                    elif len(c.children)>0 :
                        examine_list.insert( 0, c )

            task = self._findNoParent()
            if task != None:
                examine_list.append( task )

        print walk_order
        for t in walk_order:
            t.process()
        
        
if __name__ == "__main__":

    # Node Graph
    
    sg = Scene()
    
    blur = sg.addNode( "blur", "Blur Node" )
    blur.addSlot( "frame_in", "IMAGE", Node.GRP_INT, Node.DIR_IN )
    blur.addSlot( "frame_out", "IMAGE", Node.GRP_INT, Node.DIR_OUT )
    blur.addSlot( "radius", "FLOAT", Node.GRP_UI, Node.DIR_BI )
    blur.addSlot( "amount", "FLOAT", Node.GRP_UI, Node.DIR_BI )
    
    read = sg.addNode( "read", "Read File" )
    read.addSlot( "frame_out", "IMAGE", Node.GRP_INT, Node.DIR_OUT )
    
    edge = sg.addNode( "edge", "Edge Enhance Node" )
    edge.addSlot( "frame_in", "IMAGE", Node.GRP_INT, Node.DIR_IN )
    edge.addSlot( "frame_out", "IMAGE", Node.GRP_INT, Node.DIR_OUT )
    edge.addSlot( "k_size", "DESCRETE", Node.GRP_UI, Node.DIR_BI )
    edge.addSlot( "amount", "FLOAT", Node.GRP_UI, Node.DIR_BI )
    
    sg.connect( read.inner_name, "frame_out", blur.inner_name, "frame_in" )
    sg.connect( blur.inner_name, "frame_out", edge.inner_name, "frame_in" )
    
    sg.show()
    sg.walk()
    sg.show()
    
    # ----------------- Try a skeleton hyrachy
    
    sg = Scene()
    g_origin = sg.addNode( "g_origin", "Root" )
    g_origin.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    root = sg.addNode( "root", "Root" )
    root.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    root.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    hips = sg.addNode( "hips", "Root" )
    hips.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    hips.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    l_leg_upper = sg.addNode( "l_leg_upper", "Root" )
    l_leg_upper.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    l_leg_upper.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    r_leg_upper = sg.addNode( "r_leg_upper", "Root" )
    r_leg_upper.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    r_leg_upper.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    l_leg_lower = sg.addNode( "l_leg_lower", "Root" )
    l_leg_lower.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    l_leg_lower.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    r_leg_lower = sg.addNode( "r_leg_lower", "Root" )
    r_leg_lower.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    r_leg_lower.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    l_foot = sg.addNode( "l_foot", "Root" )
    l_foot.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    l_foot.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    r_foot = sg.addNode( "r_foot", "Root" )
    r_foot.addSlot( "L", "M44", Node.GRP_UI, Node.DIR_BI )
    r_foot.addSlot( "G", "M44", Node.GRP_INT, Node.DIR_BI )
    
    sg.connect( g_origin.inner_name, "G", root.inner_name, "L" )
    sg.connect( root.inner_name, "G", hips.inner_name, "L" )
    sg.connect( hips.inner_name, "G", l_leg_upper.inner_name, "L" )
    sg.connect( hips.inner_name, "G", r_leg_upper.inner_name, "L" )
    sg.connect( l_leg_upper.inner_name, "G", l_leg_lower.inner_name, "L" )
    sg.connect( r_leg_upper.inner_name, "G", r_leg_lower.inner_name, "L" )
    sg.connect( l_leg_lower.inner_name, "G", l_foot.inner_name, "L" )
    sg.connect( r_leg_lower.inner_name, "G", r_foot.inner_name, "L" )
    sg.show()