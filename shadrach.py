"""  
    SHADeR ArCHitecture system.  Also cf. https://www.youtube.com/watch?v=j_QKKkWJjqk
    load and link shaders (Vert, Frag, Geo)
    register Shaders
    register and track published uniforms
    
    NOTE:  Shaders *must* define in, out, varying, uniforms on single lines.
           (due to nieve name extraction)
    attributes are internal to the shader, so invisible to the outside world.
"""
from OpenGL.GL import *

class Shadrach( object ):
    # Class consts
    SHAD_LUT = {
        GL_VERTEX_SHADER  : "vert",
        GL_FRAGMENT_SHADER: "frag",
        GL_GEOMETRY_SHADER: "geom"
    }
    SHAD_REV_LUT = { v:k for k,v in SHAD_LUT.iteritems() }
    SHAD_UNI, SHAD_ATR = "uni", "atr"
    
    @staticmethod
    def parseForVariables( glsl ):
        """
        read a glsl string, extract:
          declaration [uniform, attribute], type, variable name
          
        assumes each relevent var is on it's own line.  As per specification.
        should be line-ending agnostic
        
        returns dict { "uni":["name",...], "atr":["name",...] }
        future implementation may extract type - might not be needed
        """
        ret = { Shadrach.SHAD_UNI:[], Shadrach.SHAD_ATR:[] }
        pass
        
        
    def __init__( self ):
        self.shader_reg = {} # system shaders
        self.method_reg = {} # system methods - some may be shared
        self.shared     = {} # register of shared params
        self.system     = {} # register of shared params
        self.shared[Shadrach.SHAD_ATR] = {} # shared atters... maybe a LUT?
        self.shared[Shadrach.SHAD_UNI] = {} # shared uniforms
        self.system[Shadrach.SHAD_ATR] = {} # all atters - I give a SN. to
        self.system[Shadrach.SHAD_UNI] = {} # all uniforms (I am given a SN)
        
    def prepareShader( self, shader_name ):
        assert( not shader_name in self.shader_reg )
        self.shader_reg[ shader_name ] = {
            "shader" : None,
            "atrs_n" : {},
            "unis_n" : {}
        }
        
    def registerSharedParam( self, param_flavour, param_name ):
        assert( param_flavour in (Shadrach.SHAD_UNI, Shadrach.SHAD_ATR) )
        
        if( param_name in self.shared[ param_flavour ] ):
            # param already registered
            return
     
        new_sn = registerPrivateParam( param_flavour, param_name )
        self.shared[ param_flavour ][ param_name ] = new_sn
            
    def registerPrivateParam(self, param_flavour, param_name ):
        if( param_name in self.system[ param_flavour ] ):
            # param already registered
            return
        new_sn = None
        if param_flavour == Shadrach.SHAD_UNI:
            # uniform, I will be issued an SN
            self.system[ param_flavour ][ new_name ] = new_sn
        else:
            # Attribute, assign my own accounting to it
            new_sn = len( self.system[ param_flavour ] )
            self.system[ param_flavour ][ new_name ] = new_sn
        
    def compileShaderMethod( self,  shader_flavour, method_name, shader_source,
                                    uni_override=None, attr_override=None     ):
        # compile a shader method
        shader_method = method_name + "." + shader_flavour
        
        # parse for attributes & uniforms
        vars = self.parseForVariables( shader_source )
        
        # register paramiters, use overrides if sharing
        for test_uni in vars[ Shadrach.SHAD_UNI ]:
            param = ""
            if test_uni in uni_override:
                param = uni_override[ test_uni ]
            else:
                param = test_uni #method_name + "." + test_uni ???
            registerPrivateParam( Shadrach.SHAD_UNI, param )
        for test_atr in vars[ Shadrach.SHAD_ATR ]:
            param = test_atr
            if test_atr in uni_override:
                param = uni_override[ test_atr ]
            registerPrivateParam( Shadrach.SHAD_ATR, param )

        tmp_shader  = glCreateShader( Shadrach.SHAD_REV_LUT[ shader_flavour ] )
        
        # Build
        glShaderSource(  tmp_shader, shader_source )
        glCompileShader( tmp_shader )
        assert( glGetShaderiv( tmp_shader, GL_COMPILE_STATUS ) == GL_TRUE )
        
        # register
        self.method_reg[ shader_method ] = tmp_shader
        return shader_method
        
    def compileShaderProgram( self, shader_name, shader_methods=None )
        assert( shader_methods != None )
        # prep
        tmp_shader = gl.CreateProgram()
        for method in shader_methods:
            glAttachShader( tmp_shader, self.method_reg[ method ] )
            
        # register variables
        # TODO: make work with shared variables
        for attrib in self.shader_reg[ shader_name ][ "atrs_n" ]:
            glBindAttribLocation( tmp_shader, self.system_atr[ attrib ], attrib )
        for uniform in self.shader_reg[ shader_name ][ "atrs_n" ]:
            self.system_uni[ uniform ] = glGetUniformLocation( tmp_shader, uniform )
            
        # compile
        glLinkProgram( tmp_shader )
        assert( glGetProgramiv( tmp_shader, GL_LINK_STATUS ) == GL_TRUE )
        glUseProgram( tmp_shader )
        
        # register
        self.shader_reg[ shader_name ][ "shader" ] = tmp_shader