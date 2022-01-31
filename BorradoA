# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Variable con la referencia del pallete a borrar
pallete_ref = RDK.Item('PalletK', ITEM_TYPE_FRAME)

#Eliminar las cajas del PalleteA
for obj in pallete_ref.Childs():
    if obj.Name().startswith("Part"):
        obj.Delete()

# Actualizar el estado de palleteA en el parametro EPALLETE
estado_pallete = RDK.getParam('EPALLETE')
l = list(estado_pallete) #El parametro es un string
l[0] = '0'
estado_pallete = "".join(l)
RDK.setParam('EPALLETE', estado_pallete)
