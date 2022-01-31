# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Use RoboDK API as RDK
RDK = Robolink()

# Parametros de la estacion
PARAM_PARTS_X_MINUTE = 'parts/min'
PARAM_NUMERO_BOX_PALLETE = 'NBOXP'
PARAM_ESTADO_PALLETE = 'EPALLETE'

# Establecer en 0 el estado de los pallete A y B
RDK.setParam(PARAM_ESTADO_PALLETE, '0,0')

# Establecer el numero indicador de cajas por Pallete
SIZE_PALLET = RDK.getParam('SizePallet')
SIZE_PALLET_XYZ = [float(x.replace(' ','')) for x in SIZE_PALLET.split(',')]
numero_box_pallete = SIZE_PALLET_XYZ[0]*SIZE_PALLET_XYZ[1]*SIZE_PALLET_XYZ[2]
RDK.setParam(PARAM_NUMERO_BOX_PALLETE, numero_box_pallete)

# turn off rendering (much faster when setting up the station)
#RDK.Render(False)

# Eliminar todas las cajas previamente simuladas
all_objects     = RDK.ItemList(ITEM_TYPE_OBJECT, False)
for item in all_objects:
    if item.Name().startswith("Part"):
        item.Delete()

# Turn on rendering
#RDK.Render(True)

# Valor de la cantidad de cajas por minuto
parts_x_minute = RDK.getParam(PARAM_PARTS_X_MINUTE)

# Seleccion del codigo de AddPart
add_part = RDK.Item('AddPart', ITEM_TYPE_PROGRAM_PYTHON)

# Movimiento de la banda transportadora
conv = RDK.Item('Conveyor Belt', ITEM_TYPE_ROBOT)
conv.setJoints([0]) # Establecer en cero
conv.MoveJ([99999], False) # Mover hasta el maximo valor permitido.

# Temporizador para creacion de cajas
SECONDS_X_PART = 60.0 / parts_x_minute #Tiempo por cada caja
tic() # Marcar inicio de cconteo
timer_last = toc() # Tiempo transcurrido desde el inicio del conteo
simulation_time = SECONDS_X_PART
while True:

    # Numero indicador de disponibilidad de pallete
    ESTADOS_PALLET      = RDK.getParam(PARAM_ESTADO_PALLETE)
    ESTADOS_PALLET_AB   = [int(x.replace(' ','')) for x in ESTADOS_PALLET.split(',')]
    numero_disponible   = ESTADOS_PALLET_AB[0] + ESTADOS_PALLET_AB[1]

    # Creacion de la nueva caja
    timer = toc()
    simulation_time = simulation_time + (timer - timer_last) * RDK.SimulationSpeed()
    timer_last = timer
    if simulation_time >= SECONDS_X_PART and numero_disponible != 2: # Se crea mas cajas siempre que haya disponibles un pallete
        simulation_time = simulation_time - SECONDS_X_PART
        add_part.RunProgram()
    if numero_disponible == 2: # No hay disponible pallete
        conv.Stop()
        while numero_disponible == 2: #Espera hasta este disponible el palleteA
            ESTADOS_PALLET      = RDK.getParam(PARAM_ESTADO_PALLETE)
            ESTADOS_PALLET_AB   = [int(x.replace(' ','')) for x in ESTADOS_PALLET.split(',')]
            numero_disponible   = ESTADOS_PALLET_AB[0] + ESTADOS_PALLET_AB[1]
        conv.MoveJ([99999], False) 
        tic() # Se reinicia la cuenta para las cajas
        timer_last = toc()
        simulation_time = 0

    pause(0.01)
    
