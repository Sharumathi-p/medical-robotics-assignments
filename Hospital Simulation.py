import time
import browserbotics as bb
import math

NO_ROT    = bb.getQuaternionFromEuler((0, 0, 0))
FRONT_ROT = bb.getQuaternionFromEuler((1.5708, 0, 0))
SIDE_ROT  = bb.getQuaternionFromEuler((1.5708, 0, 1.5708))

ROOM_W = 8.0; ROOM_H = 8.0; WALL_H = 2.5; WALL_T = 0.08
WALL_COLOR = '#EEE8EE'; FLOOR_COLOR = '#C8D8E8'; CHROME = '#C8C8CC'
CEILING_COLOR = '#F4F4F6'

CORR_START_X =  4.0
CORR_END_X   = 10.0
CORR_Y       =  0.0
CORR_W       =  1.2
CORR_LEN     = (CORR_END_X - CORR_START_X) / 2.0

R2_CX = 14.0

# ── Knife (room 1 trolley) ──────────────────────────────────────────────────
KNIFE_X, KNIFE_Y, KNIFE_Z = 2.2, -1.8, 0.85

# ── Delivery bed (room 2) ───────────────────────────────────────────────────
# Bed centre world position
BED_CX = R2_CX - 0.5   # slightly west of room centre
BED_CY = 0.3
BED_TOP_Z = 0.98        # top surface of bed pad

# Drop: lay knife on bed surface, just barely above
DROP_X  = BED_CX
DROP_Y  = BED_CY
DROP_Z  = BED_TOP_Z + 0.01   # 1 cm above pad — no penetration

# Robot parks 1.3 m WEST of bed centre (arm reaches east to bed)
PARK_X  = BED_CX - 1.3
PARK_Y  = BED_CY

# ── Robot home (room 1) ─────────────────────────────────────────────────────
HOME_X, HOME_Y = 2.2, -1.2

# ── Globals ─────────────────────────────────────────────────────────────────
knife_handle = None
knife_blade  = None
knife_label  = None
is_carrying  = False

# ===========================================================================
# ROOM 1  –  Operating Theatre
# ===========================================================================
def setup_room1():
    hw, hh = ROOM_W/2, ROOM_H/2
    # Floor (light blue-grey tiles)
    bb.createBody('box', halfExtent=[hw,hh,0.02], position=[0,0,0.01],
                  color='#BDD0E0', mass=0)
    # Tile grid lines (visual strips)
    for gx in [-3,-2,-1,0,1,2,3]:
        bb.createBody('box', halfExtent=[0.01,hh,0.005],
                      position=[gx,0,0.022], color='#A8C0D0', mass=0)
    for gy in [-3,-2,-1,0,1,2,3]:
        bb.createBody('box', halfExtent=[hw,0.01,0.005],
                      position=[0,gy,0.022], color='#A8C0D0', mass=0)

    WZ = WALL_H/2
    # Back (north) wall
    bb.createBody('box', halfExtent=[hw+WALL_T,WALL_T,WZ],
                  position=[0,hh+WALL_T,WZ], color=WALL_COLOR, mass=0)
    # Left (west) wall
    bb.createBody('box', halfExtent=[WALL_T,hh+WALL_T,WZ],
                  position=[-(hw+WALL_T),0,WZ], color=WALL_COLOR, mass=0)
    # Right (east) wall — gap for corridor
    WALL_X = hw + WALL_T
    low_half = (hh + (CORR_Y - CORR_W)) / 2.0
    bb.createBody('box', halfExtent=[WALL_T,low_half,WZ],
                  position=[WALL_X,-(hh-low_half),WZ], color=WALL_COLOR, mass=0)
    hi_half  = (hh - (CORR_Y + CORR_W)) / 2.0
    bb.createBody('box', halfExtent=[WALL_T,hi_half,WZ],
                  position=[WALL_X,hh-hi_half,WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[WALL_T+0.02,CORR_W+0.06,0.06],
                  position=[WALL_X,CORR_Y,WALL_H-0.06], color='#2A6F98', mass=0)



    # Front (south) wall with theatre door
    GAP=hw*0.30; DY=-(hh+WALL_T)
    bb.createBody('box', halfExtent=[hw-GAP+WALL_T,WALL_T,WZ],
                  position=[-(GAP+WALL_T),DY,WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[hw-GAP+WALL_T,WALL_T,WZ],
                  position=[GAP+WALL_T,DY,WZ], color=WALL_COLOR, mass=0)
    DH=WZ*2; DW=GAP
    SZB=DH+0.02; SZT=DH+0.48; SZM=(SZT+SZB)/2; SHH=(SZT-SZB)/2
    bb.createBody('box', halfExtent=[DW*0.90,WALL_T+0.02,SHH],
                  position=[0,DY,SZM], color='#FFFFFF', mass=0)
    bb.createBody('box', halfExtent=[DW*0.92,WALL_T+0.01,0.025],
                  position=[0,DY,SZT], color='#0033CC', mass=0)
    bb.createBody('box', halfExtent=[DW*0.92,WALL_T+0.01,0.025],
                  position=[0,DY,SZB], color='#0033CC', mass=0)
    bb.createDebugText('OPERATING',(-0.08,DY-WALL_T-0.02,SZM+SHH*0.42),
                       FRONT_ROT, color='#FF0000', size=0.17)
    bb.createDebugText('THEATRE',  (-0.08,DY-WALL_T-0.02,SZM-SHH*0.42),
                       FRONT_ROT, color='#FF0000', size=0.17)
    WSZ=SZB-0.14
    bb.createBody('box', halfExtent=[DW*0.90,WALL_T+0.02,0.12],
                  position=[0,DY,WSZ], color='#DD0000', mass=0)
    bb.createDebugText('ENTRY RESTRICTED',(0,DY-WALL_T-0.02,WSZ),
                       FRONT_ROT, color='#FFFFFF', size=0.085)
    DPW=DW*0.485; DPH=1.85; DPTH=WALL_T
    bb.createBody('box', halfExtent=[DW+0.09,DPTH+0.01,0.08],
                  position=[0,DY,DPH+0.08], color='#2A6F98', mass=0)
    for LRX in [-DPW*0.52, DPW*0.52]:
        bb.createBody('box', halfExtent=[DPW,DPTH,DPH/2],
                      position=[LRX,DY,DPH/2], color='#4A9FCC', mass=0)
        bb.createBody('box', halfExtent=[DPW+0.01,DPTH+0.015,0.10],
                      position=[LRX,DY,0.10], color='#B8B8B8', mass=0)
    bb.createBody('box', halfExtent=[0.020,DPTH+0.02,DPH/2],
                  position=[0,DY,DPH/2], color='#111111', mass=0)

def setup_room1_furniture():
    hw = ROOM_W/2
    # ── Wall-mounted monitor (north-west corner) ──────────────────────────
    MX=-hw+0.06; MY=3.2; MZ=1.7
    bb.createBody('box', halfExtent=[0.06,0.28,0.20],
                  position=[MX,MY,MZ], color='#1A1A2A', mass=0)       # screen
    bb.createBody('box', halfExtent=[0.03,0.30,0.22],
                  position=[MX-0.03,MY,MZ], color='#2A2A3A', mass=0)  # bezel
    bb.createBody('box', halfExtent=[0.04,0.04,0.28],
                  position=[MX-0.04,MY,MZ-0.40], color=CHROME, mass=0) # arm
    bb.createDebugText('VITALS MONITOR',(MX+0.10,MY,MZ+0.24),
                       SIDE_ROT, color='#00FF88', size=0.07)

    # ── Anaesthesia machine (north wall, left) ────────────────────────────
    AX=-1.8; AY=3.0; AZ=0.0
    bb.createBody('box', halfExtent=[0.22,0.18,0.60],
                  position=[AX,AY,AZ+0.60], color='#D0D8E0', mass=0)
    bb.createBody('box', halfExtent=[0.20,0.16,0.06],
                  position=[AX,AY,AZ+1.22], color='#B0B8C8', mass=0)
    bb.createBody('sphere', radius=0.06,
                  position=[AX-0.10,AY-0.20,AZ+0.80], color='#88AACC', mass=0)
    bb.createBody('sphere', radius=0.06,
                  position=[AX+0.10,AY-0.20,AZ+0.80], color='#AACCAA', mass=0)
    bb.createDebugText('ANAESTHESIA',(AX,AY,AZ+1.36),
                       NO_ROT, color='#AABBCC', size=0.07)

    # ── Instrument cabinet (south-west) ───────────────────────────────────
    CX=-3.2; CY=-3.0
    bb.createBody('box', halfExtent=[0.35,0.20,0.80],
                  position=[CX,CY,0.80], color='#D8DDE8', mass=0)
    bb.createBody('box', halfExtent=[0.36,0.21,0.02],
                  position=[CX,CY,1.61], color=CHROME, mass=0)
    # Cabinet door line
    bb.createBody('box', halfExtent=[0.005,0.20,0.78],
                  position=[CX,CY,0.80], color='#B0B8C8', mass=0)
    bb.createDebugText('INSTRUMENTS',(CX,CY,1.72),
                       NO_ROT, color='#99AACC', size=0.07)

    # ── Sink unit (south-east) ────────────────────────────────────────────
    SX=3.0; SY=-3.2
    bb.createBody('box', halfExtent=[0.40,0.22,0.45],
                  position=[SX,SY,0.45], color='#E0E4EA', mass=0)
    bb.createBody('box', halfExtent=[0.36,0.18,0.04],
                  position=[SX,SY,0.90], color='#C8D0DC', mass=0)  # basin
    bb.createBody('box', halfExtent=[0.02,0.02,0.18],
                  position=[SX,SY-0.08,1.00], color=CHROME, mass=0) # tap
    bb.createBody('box', halfExtent=[0.06,0.005,0.06],
                  position=[SX,SY-0.10,1.14], color=CHROME, mass=0) # spout
    bb.createDebugText('SCRUB SINK',(SX,SY,1.06),
                       NO_ROT, color='#AABBCC', size=0.07)

    # ── IV drip stand (beside operating table) ────────────────────────────
    IVX=0.80; IVY=-0.6
    bb.createBody('box', halfExtent=[0.015,0.015,0.90],
                  position=[IVX,IVY,0.90], color=CHROME, mass=0)    # pole
    bb.createBody('box', halfExtent=[0.22,0.005,0.005],
                  position=[IVX,IVY,1.80], color=CHROME, mass=0)    # crossbar
    bb.createBody('box', halfExtent=[0.06,0.04,0.12],
                  position=[IVX,IVY,1.65], color='#DDEECC', mass=0) # bag
    bb.createBody('box', halfExtent=[0.003,0.003,0.30],
                  position=[IVX,IVY+0.02,1.35], color='#CCDDBB', mass=0) # tube
    # Base tripod
    for ang in [0, 2.094, 4.189]:
        bx=IVX+0.20*math.cos(ang); by=IVY+0.20*math.sin(ang)
        bb.createBody('box', halfExtent=[0.10,0.012,0.012],
                      position=[(IVX+bx)/2,(IVY+by)/2,0.02],
                      color=CHROME, mass=0)

    # ── Overhead surgical light cluster (Room 1) ─────────────────────────
    CZ = WALL_H
    # Ceiling mount plate
    bb.createBody('box', halfExtent=[0.18,0.18,0.04],
                  position=[0,0.2,CZ], color='#AAAAAA', mass=0)
    # Two articulated arms hanging down
    for ax, ay in [(-0.30, 0.2), (0.30, 0.2)]:
        # Vertical drop arm
        bb.createBody('box', halfExtent=[0.025,0.025,0.35],
                      position=[ax,ay,CZ-0.37], color=CHROME, mass=0)
        # Horizontal reach arm
        bb.createBody('box', halfExtent=[0.30,0.025,0.025],
                      position=[ax,ay,CZ-0.72], color=CHROME, mass=0)
        # Elbow joint
        bb.createBody('sphere', radius=0.04,
                      position=[ax,ay,CZ-0.72], color='#888888', mass=0)
        # Light head housing (flat disc)
        bb.createBody('box', halfExtent=[0.30,0.30,0.055],
                      position=[ax,ay,CZ-0.88], color='#E0E0E8', mass=0)
        # Outer reflector ring
        bb.createBody('box', halfExtent=[0.31,0.31,0.01],
                      position=[ax,ay,CZ-0.83], color=CHROME, mass=0)
        # Inner bright lens cluster (7 LEDs in hex pattern)
        led_offsets = [(0,0),(0.10,0),(-0.10,0),(0.05,0.09),(-0.05,0.09),(0.05,-0.09),(-0.05,-0.09)]
        for lox,loy in led_offsets:
            bb.createBody('sphere', radius=0.028,
                          position=[ax+lox, ay+loy, CZ-0.93], color='#FFFFFF', mass=0)
        # Bright centre glow sphere
        bb.createBody('sphere', radius=0.09,
                      position=[ax,ay,CZ-0.92], color='#F8F8FF', mass=0)
        # Handle grip bar across light head
        bb.createBody('box', halfExtent=[0.005,0.22,0.018],
                      position=[ax,ay,CZ-0.84], color='#666666', mass=0)

    # Central ceiling track rail
    bb.createBody('box', halfExtent=[0.80,0.04,0.03],
                  position=[0,0.2,CZ-0.02], color='#909090', mass=0)
    bb.createBody('box', halfExtent=[0.04,0.60,0.03],
                  position=[0,0.2,CZ-0.02], color='#909090', mass=0)

    # ── Wall clock (east wall) ────────────────────────────────────────────
    CLX=hw-0.05; CLY=0.0; CLZ=2.0
    bb.createBody('sphere', radius=0.18,
                  position=[CLX,CLY,CLZ], color='#FFFFFF', mass=0)
    bb.createBody('box', halfExtent=[0.19,0.005,0.005],
                  position=[CLX,CLY,CLZ], color='#333333', mass=0)
    bb.createBody('box', halfExtent=[0.005,0.005,0.14],
                  position=[CLX,CLY,CLZ], color='#333333', mass=0)

# ===========================================================================
# CORRIDOR
# ===========================================================================
def setup_corridor():
    MX=(CORR_START_X+CORR_END_X)/2.0
    WZ=WALL_H/2
    bb.createBody('box', halfExtent=[CORR_LEN,CORR_W,0.02],
                  position=[MX,CORR_Y,0.01], color='#D0D8E0', mass=0)
    bb.createBody('box', halfExtent=[CORR_LEN,WALL_T,WZ],
                  position=[MX,CORR_Y+CORR_W+WALL_T,WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[CORR_LEN,WALL_T,WZ],
                  position=[MX,CORR_Y-CORR_W-WALL_T,WZ], color=WALL_COLOR, mass=0)

    bb.createDebugText('-> RECOVERY ROOM',(MX,CORR_Y+CORR_W-0.05,WALL_H-0.28),
                       NO_ROT, color='#00CC44', size=0.13)

# ===========================================================================
# ROOM 2  –  Recovery / Delivery Room
# ===========================================================================
def setup_room2():
    hw,hh=ROOM_W/2,ROOM_H/2
    cx=R2_CX
    # Floor — warmer green-cream tiles
    bb.createBody('box', halfExtent=[hw,hh,0.02],
                  position=[cx,0,0.01], color='#D4E8D4', mass=0)
    for gx in [cx-3,cx-2,cx-1,cx,cx+1,cx+2,cx+3]:
        bb.createBody('box', halfExtent=[0.01,hh,0.005],
                      position=[gx,0,0.022], color='#B8D0B8', mass=0)
    for gy in [-3,-2,-1,0,1,2,3]:
        bb.createBody('box', halfExtent=[hw,0.01,0.005],
                      position=[cx,gy,0.022], color='#B8D0B8', mass=0)

    WZ=WALL_H/2
    bb.createBody('box', halfExtent=[hw+WALL_T,WALL_T,WZ],
                  position=[cx,hh+WALL_T,WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[hw+WALL_T,WALL_T,WZ],
                  position=[cx,-(hh+WALL_T),WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[WALL_T,hh+WALL_T,WZ],
                  position=[cx+hw+WALL_T,0,WZ], color=WALL_COLOR, mass=0)
    WALL_X=cx-hw-WALL_T
    low_half=(hh+(CORR_Y-CORR_W))/2.0
    bb.createBody('box', halfExtent=[WALL_T,low_half,WZ],
                  position=[WALL_X,-(hh-low_half),WZ], color=WALL_COLOR, mass=0)
    hi_half=(hh-(CORR_Y+CORR_W))/2.0
    bb.createBody('box', halfExtent=[WALL_T,hi_half,WZ],
                  position=[WALL_X,hh-hi_half,WZ], color=WALL_COLOR, mass=0)
    bb.createBody('box', halfExtent=[WALL_T+0.02,CORR_W+0.06,0.06],
                  position=[WALL_X,CORR_Y,WALL_H-0.06], color='#2A6F98', mass=0)

    bb.createDebugText('RECOVERY ROOM',(cx,hh-0.3,WALL_H-0.22),
                       NO_ROT, color='#00AA44', size=0.18)

def setup_room2_furniture():
    cx=R2_CX; hw=ROOM_W/2

    # ── Ceiling pendant lights — Room 2 (Recovery) ───────────────────────
    CZ=WALL_H
    # Ceiling track bar
    bb.createBody('box', halfExtent=[1.40,0.05,0.03],
                  position=[cx,0.2,CZ-0.02], color='#909090', mass=0)

    for lx in [cx-0.80, cx, cx+0.80]:
        # Drop stem
        bb.createBody('box', halfExtent=[0.018,0.018,0.28],
                      position=[lx,0.2,CZ-0.30], color=CHROME, mass=0)
        # Pendant shade (inverted dome shape: wide box + hemisphere suggestion)
        bb.createBody('box', halfExtent=[0.22,0.22,0.06],
                      position=[lx,0.2,CZ-0.64], color='#D8DCE8', mass=0)
        bb.createBody('box', halfExtent=[0.20,0.20,0.02],
                      position=[lx,0.2,CZ-0.58], color=CHROME, mass=0)  # top rim
        bb.createBody('box', halfExtent=[0.21,0.21,0.01],
                      position=[lx,0.2,CZ-0.70], color=CHROME, mass=0)  # bottom rim
        # Bright bulb inside shade
        bb.createBody('sphere', radius=0.07,
                      position=[lx,0.2,CZ-0.65], color='#FFFFF0', mass=0)
        # Warm glow halo
        bb.createBody('sphere', radius=0.12,
                      position=[lx,0.2,CZ-0.68], color='#F4F0E0', mass=0)

    # ── Bed-side examination spotlight (over recovery bed) ───────────────
    SLX=BED_CX; SLY=BED_CY
    # Ceiling arm
    bb.createBody('box', halfExtent=[0.02,0.02,0.40],
                  position=[SLX,SLY,CZ-0.42], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.35,0.02,0.02],
                  position=[SLX,SLY,CZ-0.82], color=CHROME, mass=0)
    bb.createBody('sphere', radius=0.03,
                  position=[SLX,SLY,CZ-0.82], color='#777777', mass=0)  # pivot
    # Light head
    bb.createBody('box', halfExtent=[0.20,0.20,0.045],
                  position=[SLX,SLY,CZ-0.98], color='#DDDDE8', mass=0)
    bb.createBody('box', halfExtent=[0.21,0.21,0.01],
                  position=[SLX,SLY,CZ-0.94], color=CHROME, mass=0)
    # 5-LED array
    for lox,loy in [(0,0),(0.08,0),(-0.08,0),(0,0.08),(0,-0.08)]:
        bb.createBody('sphere', radius=0.025,
                      position=[SLX+lox,SLY+loy,CZ-1.02], color='#FFFFFF', mass=0)
    bb.createBody('sphere', radius=0.08,
                  position=[SLX,SLY,CZ-1.01], color='#F6F6FF', mass=0)
    bb.createBody('box', halfExtent=[0.005,0.16,0.015],
                  position=[SLX,SLY,CZ-0.95], color='#555555', mass=0)  # handle

    # ── Patient monitor on pole (east side of bed) ────────────────────────
    PMX=BED_CX+1.0; PMY=BED_CY; PMZ=0.0
    bb.createBody('box', halfExtent=[0.015,0.015,0.85],
                  position=[PMX,PMY,0.85], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.18,0.06,0.14],
                  position=[PMX,PMY,1.80], color='#1A1A2A', mass=0)  # screen
    bb.createBody('box', halfExtent=[0.19,0.07,0.15],
                  position=[PMX,PMY,1.80], color='#2C2C3C', mass=0)  # bezel
    bb.createDebugText('PATIENT MONITOR',(PMX,PMY,2.02),
                       NO_ROT, color='#00FF88', size=0.07)

    # ── IV drip stand (west side of bed) ─────────────────────────────────
    IVX=BED_CX-1.05; IVY=BED_CY-0.3
    bb.createBody('box', halfExtent=[0.015,0.015,0.90],
                  position=[IVX,IVY,0.90], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.20,0.005,0.005],
                  position=[IVX,IVY,1.82], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.055,0.038,0.11],
                  position=[IVX,IVY,1.67], color='#DDEEBB', mass=0)
    bb.createBody('box', halfExtent=[0.003,0.003,0.28],
                  position=[IVX,IVY+0.02,1.38], color='#CCDDAA', mass=0)
    for ang in [0,2.094,4.189]:
        bx=IVX+0.18*math.cos(ang); by=IVY+0.18*math.sin(ang)
        bb.createBody('box', halfExtent=[0.09,0.012,0.012],
                      position=[(IVX+bx)/2,(IVY+by)/2,0.02], color=CHROME, mass=0)

    # ── Side table / instrument tray (south of bed) ───────────────────────
    STX=BED_CX; STY=BED_CY+1.6
    bb.createBody('box', halfExtent=[0.30,0.22,0.02],
                  position=[STX,STY,0.88], color='#E0E8E0', mass=0)
    for lx,ly in [(-0.27,-0.18),(0.27,-0.18),(-0.27,0.18),(0.27,0.18)]:
        bb.createBody('box', halfExtent=[0.015,0.015,0.44],
                      position=[STX+lx,STY+ly,0.44], color=CHROME, mass=0)
    bb.createDebugText('TRAY',(STX,STY,0.98), NO_ROT, color='#88AA88', size=0.07)

    # ── Window (east wall) ────────────────────────────────────────────────
    WX=cx+hw+WALL_T-0.01; WY=-1.5; WZ2=1.4
    bb.createBody('box', halfExtent=[0.02,0.55,0.50],
                  position=[WX,WY,WZ2], color='#A8D8F0', mass=0)   # glass
    bb.createBody('box', halfExtent=[0.03,0.58,0.03],
                  position=[WX,WY,WZ2+0.50], color='#C0C8D0', mass=0) # top frame
    bb.createBody('box', halfExtent=[0.03,0.58,0.03],
                  position=[WX,WY,WZ2-0.50], color='#C0C8D0', mass=0) # bot frame
    bb.createBody('box', halfExtent=[0.03,0.03,0.52],
                  position=[WX,WY-0.56,WZ2], color='#C0C8D0', mass=0) # left
    bb.createBody('box', halfExtent=[0.03,0.03,0.52],
                  position=[WX,WY+0.56,WZ2], color='#C0C8D0', mass=0) # right
    bb.createDebugText('WINDOW',(WX-0.10,WY,WZ2+0.62), SIDE_ROT,
                       color='#88AABB', size=0.06)

    # ── Handwash sink (south wall) ────────────────────────────────────────
    SX=cx+2.0; SY=-(ROOM_H/2)+0.25
    bb.createBody('box', halfExtent=[0.35,0.20,0.43],
                  position=[SX,SY,0.43], color='#E4E8EE', mass=0)
    bb.createBody('box', halfExtent=[0.30,0.16,0.03],
                  position=[SX,SY,0.87], color='#C8D0DC', mass=0)
    bb.createBody('box', halfExtent=[0.018,0.018,0.15],
                  position=[SX,SY-0.08,0.97], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.055,0.005,0.04],
                  position=[SX,SY-0.10,1.11], color=CHROME, mass=0)
    bb.createDebugText('WASH STATION',(SX,SY+0.28,0.98),
                       FRONT_ROT, color='#99AABB', size=0.07)

    # ── Storage cabinet (north wall) ─────────────────────────────────────
    CBX=cx+2.5; CBY=ROOM_H/2-0.22
    bb.createBody('box', halfExtent=[0.45,0.20,0.85],
                  position=[CBX,CBY,0.85], color='#E0E4EA', mass=0)
    bb.createBody('box', halfExtent=[0.46,0.21,0.02],
                  position=[CBX,CBY,1.71], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.005,0.20,0.83],
                  position=[CBX,CBY,0.84], color='#C8CCD8', mass=0)
    bb.createDebugText('SUPPLIES',(CBX,CBY-0.26,1.76),
                       FRONT_ROT, color='#99AABB', size=0.07)

def setup_recovery_bed():
    """Detailed patient bed with headboard, rails, and patient silhouette."""
    cx=BED_CX; cy=BED_CY
    BASE='#C0C8C0'; FRAME=CHROME; PAD='#E8EEE8'; RAIL='#B0B8B8'

    # Base / frame
    bb.createBody('box', halfExtent=[0.50,1.10,0.06],
                  position=[cx,cy,0.82], color=BASE, mass=0)
    bb.createBody('box', halfExtent=[0.46,1.06,0.04],
                  position=[cx,cy,0.94], color=PAD, mass=0)   # mattress pad

    # Legs (four corners)
    for lx,ly in [(-0.44,-0.95),(0.44,-0.95),(-0.44,0.95),(0.44,0.95)]:
        bb.createBody('box', halfExtent=[0.04,0.04,0.41],
                      position=[cx+lx,cy+ly,0.41], color=FRAME, mass=0)

    # Headboard (north end)
    bb.createBody('box', halfExtent=[0.50,0.06,0.38],
                  position=[cx,cy+1.10,1.20], color='#9AACAA', mass=0)
    bb.createBody('box', halfExtent=[0.48,0.04,0.02],
                  position=[cx,cy+1.12,1.56], color=FRAME, mass=0)

    # Footboard (south end)
    bb.createBody('box', halfExtent=[0.50,0.06,0.22],
                  position=[cx,cy-1.10,1.05], color='#9AACAA', mass=0)

    # Side rails
    for rx in [-0.50, 0.50]:
        bb.createBody('box', halfExtent=[0.02,0.90,0.06],
                      position=[cx+rx,cy,1.14], color=RAIL, mass=0)

    # Pillow
    bb.createBody('box', halfExtent=[0.20,0.22,0.04],
                  position=[cx,cy+0.75,0.99], color='#FFFFFF', mass=0)

    # Patient silhouette (body + head)
    bb.createBody('box', halfExtent=[0.16,0.55,0.06],
                  position=[cx,cy-0.10,1.00], color='#D4B8A0', mass=0) # torso
    bb.createBody('sphere', radius=0.12,
                  position=[cx,cy+0.70,1.04], color='#D4B8A0', mass=0) # head
    # Sheet / blanket over lower body
    bb.createBody('box', halfExtent=[0.22,0.60,0.04],
                  position=[cx,cy-0.45,1.02], color='#DDEEDD', mass=0)

    bb.createDebugText('RECOVERY BED',(cx,cy,1.28),
                       NO_ROT, color='#88BB88', size=0.10)
    # Drop zone marker — on pad surface, clearly visible
    bb.createBody('box', halfExtent=[0.06,0.06,0.002],
                  position=[DROP_X,DROP_Y-0.10,BED_TOP_Z+0.001],
                  color='#FF4400', mass=0)
    bb.createDebugText('DROP HERE',(DROP_X,DROP_Y-0.10,BED_TOP_Z+0.10),
                       NO_ROT, color='#FF6600', size=0.08)

def setup_operating_table():
    BASE='#B0B8C0'; PAD='#2A3038'
    bb.createBody('box', halfExtent=[0.12,0.12,0.40],
                  position=[0,0.3,0.40], color=BASE, mass=0)
    bb.createBody('box', halfExtent=[0.48,1.10,0.06],
                  position=[0,0.3,0.86], color=BASE, mass=0)
    bb.createBody('box', halfExtent=[0.44,1.05,0.04],
                  position=[0,0.3,0.94], color=PAD, mass=0)
    bb.createBody('box', halfExtent=[0.55,0.04,0.02],
                  position=[ 0.50,0.3,0.92], color=CHROME, mass=0)
    bb.createBody('box', halfExtent=[0.55,0.04,0.02],
                  position=[-0.50,0.3,0.92], color=CHROME, mass=0)
    bb.createDebugText('OPERATING TABLE',(0,0.3,1.10),
                       NO_ROT, color='#88AACC', size=0.11)

def build_trolley(tx, ty):
    W='#EBEBF0'; C='#C8C8CC'; K='#222228'
    for wx,wy in [(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]:
        bb.createBody('sphere', radius=0.035,
                      position=[tx+wx,ty+wy,0.035], color=K, mass=0)
    for lx,ly in [(-0.17,-0.17),(0.17,-0.17),(-0.17,0.17),(0.17,0.17)]:
        bb.createBody('box', halfExtent=[0.018,0.018,0.40],
                      position=[tx+lx,ty+ly,0.47], color=C, mass=0)
    for sz in [0.22,0.50,0.78]:
        bb.createBody('box', halfExtent=[0.20,0.20,0.014],
                      position=[tx,ty,sz], color=W, mass=0)
    bb.createDebugText('TROLLEY',(tx,ty,1.06), NO_ROT, color='#888888', size=0.09)

# ===========================================================================
# KNIFE
# ===========================================================================
def create_knife():
    global knife_handle, knife_blade, knife_label
    knife_handle = bb.createBody('box', halfExtent=[0.008,0.065,0.006],
        position=[KNIFE_X,KNIFE_Y,KNIFE_Z], color='#1A1A1A', mass=0)
    knife_blade  = bb.createBody('box', halfExtent=[0.004,0.080,0.003],
        position=[KNIFE_X,KNIFE_Y+0.14,KNIFE_Z], color='#C8D8E0', mass=0)
    knife_label  = bb.createDebugText('KNIFE',
        (KNIFE_X,KNIFE_Y,KNIFE_Z+0.12), NO_ROT, color='#FF4400', size=0.09)

def rotate_by_quat(quat, local_offset):
    qx,qy,qz,qw = quat
    ox,oy,oz = local_offset
    tx=2.0*(qy*oz-qz*oy); ty=2.0*(qz*ox-qx*oz); tz=2.0*(qx*oy-qy*ox)
    return [ox+qw*tx+qy*tz-qz*ty,
            oy+qw*ty+qz*tx-qx*tz,
            oz+qw*tz+qx*ty-qy*tx]

def snap_knife_to_gripper(robot):
    p = bb.getLinkPose(robot, 10)
    if p is None: return
    pos,rot = p[0],p[1]
    bb.resetBasePose(knife_handle, pos, rot)
    bw = rotate_by_quat(rot, [0,0.14,0])
    bb.resetBasePose(knife_blade,
        [pos[0]+bw[0],pos[1]+bw[1],pos[2]+bw[2]], rot)
    bb.resetDebugObjectPose(knife_label, [pos[0],pos[1],pos[2]+0.10])

def place_knife_at(x, y, z):
    bb.resetBasePose(knife_handle, [x,y,z], NO_ROT)
    bb.resetBasePose(knife_blade,  [x,y+0.14,z], NO_ROT)
    bb.resetDebugObjectPose(knife_label, [x,y,z+0.12])

# ===========================================================================
# ARM HELPERS
# ===========================================================================
joint_pos = {}

def smooth_joints(robot, joints, target, steps=60):
    if target is None:
        print('[WARN] IK no solution, skipping'); return
    start_vals = [joint_pos.get(jn,0.0) for (_,jn) in joints]
    for s in range(steps+1):
        t=s/steps; t2=t*t*(3-2*t)
        for idx,(i,jn) in enumerate(joints):
            if idx < len(target):
                v = start_vals[idx]+(target[idx]-start_vals[idx])*t2
                bb.setJointMotorControl(robot, i, targetPosition=v)
        if is_carrying: snap_knife_to_gripper(robot)
        time.sleep(0.02)
    for idx,(_,jn) in enumerate(joints):
        if idx < len(target): joint_pos[jn]=target[idx]

def open_gripper(robot, joints):
    for i,jn in joints:
        if 'finger' in jn.lower() or 'gripper' in jn.lower():
            bb.setJointMotorControl(robot, i, targetPosition=0.04)
    time.sleep(0.5)

def close_gripper(robot, joints):
    for i,jn in joints:
        if 'finger' in jn.lower() or 'gripper' in jn.lower():
            bb.setJointMotorControl(robot, i, targetPosition=0.001)
    time.sleep(0.5)

def get_ik(robot, x, y, z):
    q = bb.getQuaternionFromEuler([math.pi, 0, 0])
    try:
        r = bb.calculateInverseKinematics(robot, 10, [x,y,z], q)
        if r is None or len(r)<7:
            print(f'[WARN] IK failed ({x:.2f},{y:.2f},{z:.2f})'); return None
        return list(r[:7])
    except Exception as e:
        print(f'[ERROR] IK: {e}'); return None

# ===========================================================================
# ROVER DRIVE
# ===========================================================================
cur_rx = HOME_X
cur_ry = HOME_Y

def rover_drive(robot, joints, tx, ty):
    global cur_rx, cur_ry
    fx,fy = cur_rx,cur_ry
    dist = math.hypot(tx-fx, ty-fy)
    steps = max(60, int(dist*30))
    for s in range(steps+1):
        t=s/steps; t2=t*t*(3-2*t)
        nx=fx+(tx-fx)*t2; ny=fy+(ty-fy)*t2
        bb.resetBasePose(robot, [nx,ny,0.0], NO_ROT)
        for i,jn in joints:
            bb.setJointMotorControl(robot, i, targetPosition=joint_pos.get(jn,0.0))
        if is_carrying: snap_knife_to_gripper(robot)
        time.sleep(0.03)
    cur_rx=tx; cur_ry=ty

# ===========================================================================
# PICK & DELIVER
# Robot parks at PARK_X,PARK_Y  =  BED_CX-1.3, BED_CY
# Arm reaches EAST (+X) to BED_CX — never enters the bed footprint
# ===========================================================================
def pick_and_deliver(robot, joints):
    global is_carrying
    is_carrying = False

    rover_drive(robot, joints, HOME_X, HOME_Y)

    print('[1] Open gripper')
    open_gripper(robot, joints)
    print('[2] Reach above knife on trolley')
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 1.10), steps=80)
    print('[3] Lower to knife')
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 0.87), steps=60)
    print('[4] Close gripper & lift')
    close_gripper(robot, joints)
    is_carrying = True
    snap_knife_to_gripper(robot)
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 1.45), steps=50)

    print('[5] Drive through corridor')
    rover_drive(robot, joints, CORR_START_X-0.6, CORR_Y)
    rover_drive(robot, joints, (CORR_START_X+CORR_END_X)/2, CORR_Y)
    rover_drive(robot, joints, CORR_END_X+0.6, CORR_Y)

    print('[6] Park WEST of bed (arm reaches east — never enters bed)')
    rover_drive(robot, joints, PARK_X, PARK_Y)

    print('[7] Extend arm over bed surface')
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y, 1.30), steps=60)

    # Lower to just 1 cm above pad — stops at bed surface, never penetrates
    print('[8] Lower knife to bed surface')
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y, DROP_Z+0.03), steps=55)

    print('[9] Release knife')
    is_carrying = False
    open_gripper(robot, joints)
    place_knife_at(DROP_X, DROP_Y-0.10, DROP_Z)   # land on pad

    print('[10] Retract arm clear of bed')
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y, 1.40), steps=40)

    print('[11] Return home via corridor')
    rover_drive(robot, joints, CORR_END_X+0.6, CORR_Y)
    rover_drive(robot, joints, (CORR_START_X+CORR_END_X)/2, CORR_Y)
    rover_drive(robot, joints, CORR_START_X-0.6, CORR_Y)
    rover_drive(robot, joints, HOME_X, HOME_Y)
    print('[DONE] Knife delivered to recovery bed!')

# ===========================================================================
# RETURN KNIFE
# ===========================================================================
def return_knife(robot, joints):
    global is_carrying
    is_carrying = False

    print('[R1] Drive to Room 2')
    rover_drive(robot, joints, CORR_START_X-0.6, CORR_Y)
    rover_drive(robot, joints, (CORR_START_X+CORR_END_X)/2, CORR_Y)
    rover_drive(robot, joints, CORR_END_X+0.6, CORR_Y)
    rover_drive(robot, joints, PARK_X, PARK_Y)

    print('[R2] Reach to knife on bed')
    open_gripper(robot, joints)
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y-0.10, 1.30), steps=60)
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y-0.10, DROP_Z+0.04), steps=55)

    print('[R3] Grip & lift')
    close_gripper(robot, joints)
    is_carrying = True
    snap_knife_to_gripper(robot)
    smooth_joints(robot, joints, get_ik(robot, DROP_X, DROP_Y-0.10, 1.45), steps=50)

    print('[R4] Return via corridor')
    rover_drive(robot, joints, CORR_END_X+0.6, CORR_Y)
    rover_drive(robot, joints, (CORR_START_X+CORR_END_X)/2, CORR_Y)
    rover_drive(robot, joints, CORR_START_X-0.6, CORR_Y)
    rover_drive(robot, joints, HOME_X, HOME_Y)

    print('[R5] Return knife to trolley')
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 1.10), steps=60)
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 0.87), steps=55)
    is_carrying = False
    open_gripper(robot, joints)
    place_knife_at(KNIFE_X, KNIFE_Y, KNIFE_Z)
    smooth_joints(robot, joints, get_ik(robot, KNIFE_X, KNIFE_Y, 1.10), steps=40)
    print('[DONE] Knife returned to trolley!')

# ===========================================================================
# SCENE INIT
# ===========================================================================
bb.setGravity(0, 0, -9.8)
bb.createBody('box', halfExtent=[50,50,0.01], position=[0,0,-0.01],
              color='#A8B8C8', mass=0)

setup_room1()
setup_room1_furniture()
setup_corridor()
setup_room2()
setup_room2_furniture()
setup_operating_table()
setup_recovery_bed()

# Room 1 trolleys
build_trolley(-2.2, -1.8)
build_trolley( 2.2, -1.8)   # ← knife lives here
build_trolley( 2.8,  1.2)
build_trolley(-2.8, -1.2)
# Room 2 trolleys
build_trolley(R2_CX+2.2, -1.6)
build_trolley(R2_CX-2.0,  1.8)

create_knife()

robot = bb.loadURDF('panda.urdf', position=[HOME_X,HOME_Y,0.0], fixedBase=True)
bb.createDebugText('ARM+ROVER',(HOME_X,HOME_Y,1.40), NO_ROT, color='cyan', size=0.10)

joints=[]
for i in range(bb.getNumJoints(robot)):
    joint_name, joint_type, joint_limits = bb.getJointInfo(robot, i)
    if joint_type != 'fixed':
        joints.append((i, joint_name))
        joint_pos[joint_name] = sum(joint_limits)/2
        bb.addDebugSlider(joint_name, sum(joint_limits)/2, *joint_limits)

bb.addDebugButton('PICK & DELIVER TO RECOVERY BED')
bb.addDebugButton('RETURN KNIFE TO TROLLEY')
prev_pick=0; prev_ret=0

print('=== READY: Press PICK & DELIVER TO RECOVERY BED ===')

while True:
    vp=bb.readDebugParameter('PICK & DELIVER TO RECOVERY BED')
    vr=bb.readDebugParameter('RETURN KNIFE TO TROLLEY')
    if vp > prev_pick:
        pick_and_deliver(robot, joints); prev_pick=vp
    elif vr > prev_ret:
        return_knife(robot, joints);   prev_ret=vr
    else:
        for i,jn in joints:
            jp=bb.readDebugParameter(jn)
            bb.setJointMotorControl(robot, i, targetPosition=jp)
            joint_pos[jn]=jp
    time.sleep(0.05)
