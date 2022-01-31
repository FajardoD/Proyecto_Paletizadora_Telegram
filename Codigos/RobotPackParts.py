# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Use RoboDK API as RL
RDK = Robolink()

# define default approach distance
APPROACH = 100

# Parametros de la estacion
SENSOR_VARIABLE = 'SENSOR' 
PARAM_ESTADO_PALLETE = 'EPALLETE'
RDK.setParam(PARAM_ESTADO_PALLETE, '0,0')
ESTADOS_PALLET      = RDK.getParam(PARAM_ESTADO_PALLETE)

# gather robot, tool and reference frames from the station
robot               = RDK.Item('KR', ITEM_TYPE_ROBOT)
tool                = RDK.Item('GripperK', ITEM_TYPE_TOOL)
tool_tcp            = RDK.Item('TCPK', ITEM_TYPE_TOOL)

frame_palletA        = RDK.Item('PalletK', ITEM_TYPE_FRAME)
frame_palletB       = RDK.Item('PalletK2', ITEM_TYPE_FRAME)
frame_conv          = RDK.Item('ConveyorReference', ITEM_TYPE_FRAME)
frame_conv_moving   = RDK.Item('MovingRef', ITEM_TYPE_FRAME)

# gather targets
target_pallet_safeA  = RDK.Item('PalletApproachk', ITEM_TYPE_TARGET)
target_pallet_safeB = RDK.Item('PalletApproachk2', ITEM_TYPE_TARGET)
target_conv_safe    = RDK.Item('ConvApproachk', ITEM_TYPE_TARGET)
target_conv         = RDK.Item('Get Conveyor', ITEM_TYPE_TARGET)

# Reinicio de la cuenta de las cajas totales paletizadas
COUNT_BOX = 0

# get variable parameters
SIZE_BOX = RDK.getParam('SizeBox')
SIZE_PALLET = RDK.getParam('SizePallet')
SIZE_BOX_XYZ = [float(x.replace(' ','')) for x in SIZE_BOX.split(',')]
SIZE_PALLET_XYZ = [float(x.replace(' ','')) for x in SIZE_PALLET.split(',')]
SIZE_BOX_Z = SIZE_BOX_XYZ[2] # the height of the boxes is important to take into account when approaching the positions

def box_calc(size_xyz, pallet_xyz):
    """Calculates a list of points to store parts in a pallet"""
    [size_x, size_y, size_z] = size_xyz
    [pallet_x, pallet_y, pallet_z] = pallet_xyz    
    xyz_list = []
    for h in range(int(pallet_z)):
        for j in range(int(pallet_y)):
            for i in range(int(pallet_x)):
                xyz_list = xyz_list + [[(i+0.5)*size_x, (j+0.5)*size_y, (h+0.5)*size_z]]
    return xyz_list

def TCP_On(toolitem):
    """Attaches the closest object to the toolitem Htool pose,
    It will also output appropriate function calls on the generated robot program (call to TCP_On)"""
    toolitem.AttachClosest()
    toolitem.RDK().RunMessage('Set air valve on')
    toolitem.RDK().RunProgram('TCP_On()')
        
def TCP_Off(toolitem, itemleave=0):
    """Detaches the closest object attached to the toolitem Htool pose,
    It will also output appropriate function calls on the generated robot program (call to TCP_Off)"""
    #toolitem.DetachClosest(itemleave)
    toolitem.DetachAll(itemleave)
    toolitem.RDK().RunMessage('Set air valve off')
    toolitem.RDK().RunProgram('TCP_Off()')

# calculate an array of positions to get/store the parts
parts_positions = box_calc(SIZE_BOX_XYZ, SIZE_PALLET_XYZ)

# Calculate a new TCP that takes into account the size of the part (targets are set to the center of the box)
tool_xyzrpw = tool.PoseTool()*transl(0,0,SIZE_BOX_Z/2)
tool_tcp.setPoseTool(tool_xyzrpw)
#tool_tcp = robot.AddTool(tool_xyzrpw, 'TCP')

# ---------------------------------------------------------------------------------
# -------------------------- PROGRAM START ----------------------------------------

def WaitSensor():
    if RDK.RunMode() == RUNMODE_SIMULATE:
        # Simulate the sensor by waiting for the SENSOR status to turn to 1 (object present)
        while RDK.getParam(SENSOR_VARIABLE) == 0:
            pause(0.001)
    else:
        RDK.RunProgram('WaitSensor')
    print("Part detected")

P = -1 # Variable indicadora del pallete a llenar
robot.setTool(tool_tcp)
nparts = len(parts_positions)
while True:
    # Numero indicador de disponibilidad de palletes
    ESTADOS_PALLET_AB   = [int(x.replace(' ','')) for x in ESTADOS_PALLET.split(',')]
    numero_disponible   = ESTADOS_PALLET_AB[0] + ESTADOS_PALLET_AB[1]

    if numero_disponible == 2:
        # Se detiene el brazo robotico hasta que haya palletes disponibles
        while numero_disponible == 2:
            ESTADOS_PALLET      = RDK.getParam(PARAM_ESTADO_PALLETE)
            ESTADOS_PALLET_AB   = [int(x.replace(' ','')) for x in ESTADOS_PALLET.split(',')]
            numero_disponible   = ESTADOS_PALLET_AB[0] + ESTADOS_PALLET_AB[1]  
    #Establecer la referencia y el target del pallete
    if ESTADOS_PALLET_AB[0] == 0:
        P = 1
        frame_pallet = frame_palletA
        target_pallet_safe = target_pallet_safeA
    elif ESTADOS_PALLET_AB[1] == 0:
        P = 2
        frame_pallet = frame_palletB
        target_pallet_safe = target_pallet_safeB

    i = 0
    while i < nparts:
        # ----------- place the box i on the convegor ------
        # approach to the conveyor
        robot.setFrame(frame_conv)
        target_conv_pose = target_conv.Pose()*transl(0,0,-SIZE_BOX_Z/2)
        target_conv_app = target_conv_pose*transl(0,0,-APPROACH)
        robot.MoveJ(target_conv_safe)
        robot.MoveJ(target_conv_app)
        WaitSensor()
        robot.MoveL(target_conv_pose)
        TCP_On(tool) # detach an place the object in the moving reference frame of the conveyor
        robot.MoveL(target_conv_app)
        robot.MoveJ(target_conv_safe)

        # ----------- take a part from the conveyor ------
        # get the xyz position of part i
        robot.setFrame(frame_pallet)
        part_position_i = parts_positions[i]
        target_i = transl(part_position_i)*rotx(pi)
        target_i_app = target_i * transl(0,0,-(APPROACH+SIZE_BOX_Z))    
        # approach to the pallet
        robot.MoveJ(target_pallet_safe)
        # get the box i
        robot.MoveJ(target_i_app)
        robot.MoveL(target_i)
        TCP_Off(tool, frame_pallet) # attach the closest part
        robot.MoveL(target_i_app)
        robot.MoveJ(target_pallet_safe)
        COUNT_BOX +=1 # Aumenta la cuenta cuando deja una caja
        RDK.setParam('BOX', COUNT_BOX)
        i = i + 1

    # Cambio del estado de los pallete
    ESTADOS_PALLET      = RDK.getParam(PARAM_ESTADO_PALLETE)
    if P == 1:
        l = list(ESTADOS_PALLET)
        l[0] = '1'
        ESTADOS_PALLET = "".join(l)
    else:
        l = list(ESTADOS_PALLET)
        l[2] = '1'
        ESTADOS_PALLET = "".join(l)
    RDK.setParam('EPALLETE', ESTADOS_PALLET)
    
    
