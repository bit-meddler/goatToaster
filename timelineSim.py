
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class HenchSim( gtBase.GLtoast ):
    ''' Been meening to write a 'capture henchman' tool for years. Oh well, now's
        my chance
    '''
    
    COLOURS = {
        "TL_BG"   : "#bfcfe1",
        "TEXT"    : "#000000",
        "IN_TICK" : "#009240",
        "OUT_TICK": "#da251d",
        "PLAY"    : "#29166f",
        "LENS"    : "#007cc3",
        "IN_BG"   : "#70c564",
        "OUT_BG"  : "#ff9696",
        "TIME_BG" : "#96b5ed"
    }
    
    
    def __init__(self):
        super( HenchSim, self ).__init__()
        
        
        
        
    def init( self ):
        # super
        super( HenchSim, self ).init()
        # set up HUD LOG
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF") )
        
        # my Vars

        
        # timing

        
        # Register keys / Callback into the key_man

        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        self._hud_man.addMsg( "LOG", "Ready!" )        
        
    def end( self ):
        exit(0)      
        
        
    def _draw( self ):
        # Reset canvas
        self._clear()
    
        # Draw Stuff
        self.set2D()
        
        # do lists
        self.paintLists()
        
        # swap buffers & clean up
        super( HenchSim, self )._draw()
        
        
myApp = HenchSim()
myApp._title = "Optimal Timeline Experiment"
myApp._bg = tuple( CT.web24f("#d4d0c8") )
myApp._log_col = "#000000"
myApp._center = True
myApp._wh = ( 500, 95 )

myApp.init()
myApp.prep()
myApp.exe()

"""
What's supposed to happen in here...

Take can have multiple sub-takes:

|--------------Take "blarBlar_AA_AA_001"--------------------|
   [---Sub 1---] [---Sub 2---]    [---Sub 3---] [---Sub 4---]
     a    b        a                 a     b      a  b   c 
                                     ^
so the indicated point in the take will be called: 'blarBlar_AA_AA_001.3.a'

When tying togeather multipule resources (Cams, Data, Audio, HMC), there will
be many possibly differing in/out points for a peice of media encompassing 
these ranges.  also deal with battery changes, slow starts, or loss of data.

future improvements allow advancing the 'alphas' and auto-incrementing the take no.
possibly bind Addvance/retreat to F1,F2 for Ax_xx, F3,F4 for xA_xx and so on.



DIGICONT_LOG = {
    "SESSION_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing Main, Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,
        "SUBJECTS_ENCOUNTERED": (NAME1,NAME2),
                                # Every subject activated ever this day
        "CAPTURE_PATH": TEXT,   # Path to where this data was captured
        "CAPTURE_HOST": TEXT,   # Hostname / IP / MAC of original capture host
        "UNIT": TEXT            # Name of Unit recording
    },
    "SCRIPT_DATA":{
        "SCENE_ID":{
            "SCENE_UUID": UUID  # UUID
            "SLATE": NAME       # slate name from production
            "SCENE": NAME       # Scene Name from production
            "SCENE_DESC": TEXT  # textual description of the scene
        }
    }
    "SESSION_TAKE_LOGS":{
        "TAKE_DISPLAY_NAME":{
            "UUID": UUID,
            "SCENE_ID"
            "TAKE_NAME_DETAIL": (BASENAME,SETUP,ACTION,TAKE) # Blar_AA_AA_0001
            "CREATION_TOD": (YYYY,MM,DD,HH,MM,SS,ZZZ), # 2017,09,12,13,50,45,GMT
            "SUBJECTS":(NAME1,NAME2),   # List of Subjects (actors)
            "IN": TIMECODE,             # Recording start timecode (NOT Action)
            "OUT": TIMECODE,            # End of recording timecode, might be 'cut' time
            "DURATION_FRAMES": NUMBER,  # Imply from end-start
            "SUBTAKES":{
                "ACTION": TIMECODE,     # action tc
                "CUT": TIMECODE,        # cut tc
                "MARKERS":{             # any markers logged, labelled [a-z]
                    "TIME": TIMECODE,   # TC
                    "NOTE": TEXT,       # Logging Notes
                    "D_NOTE": TEXT      # Director's notes
                },
                "PREFERENCE": TEXT,     # Director's Preference
                "NOTE": TEXT,           # Logging Note
                "D_NOTE": TEXT          # Director's notes
            },
            "COSTUME":( (SUBJECT1, TARGET1, TIMECODE),
                        (SUBJECT1, TARGET2, TIMECODE)
                        # Map of Subjects to 'costumes' and time they atarted wearing it
            )
        }
    },
    "SESSION_TAKE_DATA":{ # Technical date about MoCap
        "TAKE_DISPLAY_NAME":{ 
            "UUID": UUID,               # Inherited from Lag Log
            "CALIBRATION": FILENAME,    # MoCap Calibration in use
            "MASKS": FILENAME,          # Masks
            "CAMERA_SETTINGS": FILENAME,# camera data
            "DISPATCHERS_REGISTERED": (CAPTURE_SLAVE_NAME1, CAPTURE_SLAVE_NAME2)
            "DISPATCHER_LOGS":{
                CAPTURE_SLAVE_NAME:(
                    (TIMECODE,EVENT,TEXT),
                )
            }
        }
    }
}


# more like VFX set survey / Data acquisition than MoCap / Digi-Cont logging, but for extensibility, think about it...

CAM_REPORTS = {
    "KNOWN_CAMERAS": (CAMERA_NAME1, CAMERA_NAME2),
    "SESSION_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,   # Project base frame-rate (can be overridden by cameras)
        "UNIT": TEXT            # Name of Unit recording
    },
    "TAKE_DATA":{
        "TAKE_DISPLAY_NAME":{
            "SETUP_ID"": ID,    # ID of the setup
            "CAMERA_LOGS":{
                "CAMERA_NAME":{
                    "ROLL": NAME,
                    "SHUTTER" NUMBER,
                    "F-STOP": NUMBER,
                    "FPS": NUMBER
                    "LENS_SN": NAME,
                    "FOCAL_LENGTH": NUMBER
                    "SYNCRONIZED": TRUE
                    "IN": TIMECODE
                    "OUT": TIMECODE
                }
            }
        }
    },
    "SETUP_DATA":{
        "SETUP_ID":{
            "ELEMENT_TYPE": TEXT,
            "ELEMENTS": (Set Extension, Chromakey ),
            "RECORDED": (IBC, Macbeth, Balls, Clean-pass, )
        },
    }
    "CAMERA_DATA":{
        "CAMERA_NAME":{
            "BODY_SN":NUMBER,
            "TYPE": NAME,
            "HIRE": NAME
        }
    }
    
}

VFX_SURVEY = {
    "SHOOTING_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,   # Project base framerate (can be overridden by cameras)
        "UNIT": TEXT            # Name of Unit recording
        "LOCATION": GPS         # GPS location of shoot
    },
    "SETUPS":{
        "SETUP_ID":{
            "HDR":
            "SPHERICAL"
            "TRIG_SURVEY"
            "LIDAR_SCAN"
            "PHOTO_REF"
            "PHOTO_SCAN"
            "CONSTRUCTION_PLANS"
            "LIGHTING_PLOT"
        }
    }

}




































































"""
