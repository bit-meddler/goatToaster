
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class TimeLine( gtBase.GLtoast ):
    ''' A nice looking timeline:
        # BG with graticules
            + Sensible granularity
        # sub region display [log, active, cached]
        # marks in log region
        # moving play head
        # IN/OUT indicators
        # Magnifying Glass
            + BG and graticules rescale
        # Moving Magnifying glass
            + trys to keep glass center in sync with playhead's position in file
            + locks left and right till playhead reaches or exceedes center
        # Rate stretch (Multiplier) Control
        
        Respecting AVID shortcuts:
        # [Space] = toggle Play Pause
        # [I], [O] = Mark main In/Out
        # [Shift] + [I], [O] = append In/Out region to regions list
        # [J], [K], [L] ->
            K tapped: toggle Play Pause 1x
            K Held: Play at 1x, enable Multipliers
            K released: Pause, reset to 1x
            J/L tapped: step 1 frame < or >
            J/L held: Play 1x in < or >
            K Held, and and J/L Tapped: temporary inc or dec Multiplier
                                        multi taps = doubling of inc/dec
        # [<], [>] = multiplier dec/inc 
        # [[], []] = Magnify dec/inc
        # [T] = promote select region to active sub-region
        # [Shift]+[T] = extract select region from active sub0region
        
        Click Handlers ?
        # We could do this, invisible rect on top of 'hit' regions?
        # or not bother, this is just an experiment
        
        
    '''
    
    COLOURS = {
        "BACK"    : "#bfcfe1",
        "TEXT"    : "#000000",
        "IN_TICK" : "#009240",
        "OUT_TICK": "#da251d",
        "PLAY"    : "#29166f",
        "LENS"    : "#007cc3",
        "IN_BG"   : "#70c564",
        "TC_BG"   : "#dcdcdc",
        "OUT_BG"  : "#ff9696",
        "TIME_BG" : "#96b5ed",
        "LINES"   : "#000000",
        "GRATICS" : "#000000",
        "CONTRA"  : "#c3c3c2"
    }
    
    
    def __init__(self):
        super( TimeLine, self ).__init__()
        
         
    def init( self ):
        # super
        super( TimeLine, self ).init()
        # set up HUD LOG
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF"), -1 )
        
        # my Vars
        # #######
        
        # draw control
        self._border_pad = 5
        
        # playback
        self.start_frame = 1
        self.end_frame   = 3600 # factors to 24, 25, 30 fps
        self.play_in     = 1
        self.play_out    = 3600
        self.cur_frame   = 1    # anims count from 1
        self.play_multi  = 1.   # multiplier
        self.skip_multi  = 1.   # after skipping revert to play_multi
        
        # Markings
        self.mark_in     =    1 # Single Marked Range (in/out)
        self.mark_out    = 3600 #
        self.mark_active =   [] # List of [in,out] pairs, in order
        self.mark_cached =   [] #             ditto
        
        # View
        # Magnifying glass dosen't rescale like premiere
        # these are as a % of mag_bg width, which is scaled to fit canvas size
        self.mag_in      =    0.
        self.mag_out     =  100.
        self.mag_mark_in =    1
        self.mag_mark_out= 3600
        self.mag_first   =    0. # start of mag region, 
        
        # timing
        self.native_frame_dur = 0.04 # 25fps
        
        
        # Register keys / Callback into the key_man

        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        self._hud_man.addMsg( "LOG", "Ready!", overide_life=33 )        
        
        # Compute Fixed UI, update min Extents
        self._computeUIFixed()
        self._ext_lock = True
        # TODO: cache fixed UI from display list
        #       In a real application this would be an image, and blitted into place
        self._fixed_ui_cache = None
        
        
    def end( self ):
        exit(0)      
        
    def _computeUIFixed( self ):
        # locals
        nw, nh = self._wh
        x, y, n, m = 0, 0, 0, 0
        
        edge_pad  = 12
        small_pad = 5
        
        # UI Regions
        frames_display = (40, 15)
        play_control = (141, 21)
        tc_box = (101, 14)
        speed_bar_h = 9
        label_box_h = 31
        label_area_h = 10
        mag_pad_w = 40
        region_tick = (8, 19)
        timeline_height   = play_control[1] + small_pad + tc_box[1]
        min_h = edge_pad  + timeline_height + small_pad + speed_bar_h + \
                small_pad + label_box_h + edge_pad
        min_w = edge_pad  + frames_display[0] + edge_pad + play_control[0] + \
                edge_pad  + 200 + edge_pad
        self._min_extents = ( min_w, min_h )
        
        del self.rec_list[:], self.line_list[:]
        
        # Start drawing Rects
        # ###################
        temp = 0
        y = nh - edge_pad
        x = edge_pad
        # ### Frames ###
        # Current Frame
        y -= frames_display[1]
        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["TIME_BG"], self.STYLES["QUADS"]) )

        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        
        # Region In Frame
        y -= frames_display[1] + small_pad
        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["IN_BG"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # Region Out Frame
        y -= frames_display[1] + small_pad
        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["OUT_BG"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, frames_display[0], frames_display[1],
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        
        
        
        # ### play controls ###
        x += frames_display[0] + small_pad
        y = nh - (edge_pad + play_control[1])
        # Transport
        self.rec_list.append( (x, y, play_control[0], play_control[1],
                               self.COLOURS["CONTRA"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, play_control[0], play_control[1],
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # TC readout
        y -= (small_pad + tc_box[1])
        self.rec_list.append( (x, y, tc_box[0], tc_box[1],
                               self.COLOURS["TC_BG"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, tc_box[0], tc_box[1],
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # Speed bar
        y -= (speed_bar_h + small_pad)
        self.rec_list.append( (x, y, play_control[0], speed_bar_h,
                               self.COLOURS["BACK"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, play_control[0], speed_bar_h,
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # Labels
        y -= label_box_h + small_pad
        self.rec_list.append( (x, y, play_control[0], label_box_h,
                               self.COLOURS["BACK"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, play_control[0], label_box_h,
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )

        y += label_box_h
        y -= label_area_h
        temp = x + play_control[0] - 2
        self.line_list.append( (x-1, y, temp, y, self.COLOURS["LENS"]) )
        y -= label_area_h
        self.line_list.append( (x-1, y, temp, y, self.COLOURS["LENS"]) )
        

        # ### Timeline ###
        x += play_control[0] + small_pad
        y = nh - (edge_pad + timeline_height)
        # Timeline
        timeline_width = nw - edge_pad - x
        self.rec_list.append( (x, y, timeline_width, timeline_height,
                               self.COLOURS["BACK"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, timeline_width, timeline_height,
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # Mag
        y -= (0 + small_pad)
        self.rec_list.append( (x+mag_pad_w, y, timeline_width-mag_pad_w, -speed_bar_h,
                               self.COLOURS["BACK"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x+mag_pad_w, y, timeline_width-mag_pad_w, -speed_bar_h,
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        # Labels
        # Labels
        y -= speed_bar_h + small_pad
        self.rec_list.append( (x, y, timeline_width, -label_box_h,
                               self.COLOURS["BACK"], self.STYLES["QUADS"]) )
        self.rec_list.append( (x, y, timeline_width, -label_box_h,
                               self.COLOURS["LINES"], self.STYLES["LINES"]) )
        y -= label_area_h
        temp = x + timeline_width - 2
        self.line_list.append( (x-1, y, temp, y,self.COLOURS["LENS"]) )
        y -= label_area_h
        self.line_list.append( (x-1, y, temp, y,self.COLOURS["LENS"]) )

        
    def _reSize( self, width, height ):
        super( TimeLine, self )._reSize( width, height )
        print self._wh
        self._computeUIFixed()
        
        
    def _draw( self ):
        # Reset canvas
        self._clear()
    
        # Draw Stuff
        self.set2D()
        
        # do lists
        self.paintLists()
        
        # swap buffers & clean up
        super( TimeLine, self )._draw()
        
        
myApp = TimeLine()
myApp._title = "Optimal Timeline Experiment"
myApp._bg = tuple( CT.web24f("#D4D0C8") )
myApp._log_col = "#000000"
myApp._center = True
myApp._wh = ( 500, 114 )

myApp.init()

myApp.prep()
myApp.exe()

"""




Timeline Logic

Draw First and Last Frame exactly

divide space available to draw by padded width of highest number = number of gradiations
find 'round' step size 

























































"""
