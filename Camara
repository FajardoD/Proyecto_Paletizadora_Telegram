# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

#Parametro que indica cuando tomar una foto
FOTO_ESTACION = 'FOTO'

#Direccion y nombre de la foto
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = '/estacion.jpg'

while(1):
    ref_cam = RDK.Item('Camera Reference',ITEM_TYPE_FRAME)
    ref_cam.setVisible(False)
    
    tomar_foto = int(RDK.getParam(FOTO_ESTACION)) # Indicador para tomar la foto 
    while tomar_foto == 0: # No tomara la foto mientras se indique 0
        tomar_foto = int(RDK.getParam(FOTO_ESTACION))
        pause(0.001)
    #Parametros, toma y guardado de la foto.
    cam_id = RDK.Cam2D_Add(ref_cam, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=10000 SIZE=1024x768 BG_COLOR=black LIGHT_AMBIENT=white LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')
    RDK.Cam2D_Snapshot((path_rdk+file_name), cam_id)
    RDK.Cam2D_Close(cam_id)
    cam_id.Delete()

    while tomar_foto == 1: #No tomara otra foto hasta que se resetee el indicador.
        tomar_foto = int(RDK.getParam(FOTO_ESTACION))
        pause(0.001)
    
