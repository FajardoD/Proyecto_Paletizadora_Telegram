#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import ChatAction

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox

RDK = Robolink()
FOTO_ESTACION = 'FOTO' # Parametro que indica si se debe tomar una foto
path_rdk = RDK.getParam('PATH_OPENSTATION')# Parametro con la direccion de la foto
file_name = '/estacion.jpg'# Parametro con el nombre de la foto

# Definiendo los comandos de telegram
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2( #Funcion para enviar un mensaje con el nombre del usuario.
        fr'Hola {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text('En esta aplicacion podras consultar el estado de la estacion de paletizado, usa el comando /help para conocer las funciones')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Las funciones que se pueden usar son:') # Funcion para enviar un mensaje de texto al usuario
    update.message.reply_text('/help -> Te ayuda a conocer la funciones existentes')
    update.message.reply_text('/box -> Te indica la cantidas de cajas paletizadas')
    update.message.reply_text('/pallete -> Te indica la cantidad de palletes llenos')
    update.message.reply_text('/Epallete -> Te indica el estado de los palletes de la estacion')
    update.message.reply_text('/foto -> Te envia una foto de la estacion')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Por favor, ingrese un comando conocido, o de clic en -> /help')

def box(update: Update, context: CallbackContext) -> None:
    cantidad_cajas = RDK.getParam('BOX') # Parametro con el valor de cajas totales paletizadas
    update.message.reply_text('La cantidad de cajas paletizadas es de ' + str(cantidad_cajas))

def pallete(update: Update, context: CallbackContext) -> None:
    cantidad_cajas = int(RDK.getParam('BOX')) # Parametro con el valor de cajas totales paletizadas
    numero_box_pallete = int(RDK.getParam('NBOXP')) #Parametro con la cantidad de cajas por palleto
    cantidad_pallete = cantidad_cajas//numero_box_pallete # Numero de palletes enteros realizados
    update.message.reply_text('La cantidad de palletes terminados es de ' + str(cantidad_pallete))

def Epallete(update: Update, context: CallbackContext) -> None:
    estado_pallete      = RDK.getParam('EPALLETE') #Parametro con el estado de los palletes
    estados_pallete_AB   = [int(x.replace(' ','')) for x in estado_pallete.split(',')]
    # Asignacion de vacio o lleno al mensaje sobre el estado de cada pallete
    if estados_pallete_AB[0] == 0 :
        palleteA = 'vacio o llenando'
    else:
        palleteA = 'lleno'
    if estados_pallete_AB[1] == 0:
        palleteB = 'vacio o llenando'
    else:
        palleteB = 'lleno'
    
    # Determinar estructura del mensaje segun el estado de los palletes
    if estados_pallete_AB == [1,1]:
        update.message.reply_text('Los dos palletes se encuentran llenos, el proceso esta detenido' )
    else:
        update.message.reply_text('El palleteA esta ' + str(palleteA))
        update.message.reply_text('El palleteB esta ' + str(palleteB))

def foto(chat):
    chat.send_action(action=ChatAction.UPLOAD_PHOTO,timeout=None) #Accion de que se esta enviando una foto
    pause(0.1)
    chat.send_photo(photo = open(path_rdk+file_name,'rb')) # Se envia la foto que sera buscada en la direccion establecida
    RDK.setParam(FOTO_ESTACION,'0') # Actualizacion de parametro que indica cuando tomar una foto

def chat(update: Update, context: CallbackContext) -> None:
    RDK.setParam(FOTO_ESTACION,'1') # Actualizacion de parametro que indica cuando tomar una foto
    chat = update.message.chat #Datos de chat de la persona que escribe
    foto(chat) # Funcion para enviar la foto

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5062967228:AAGSuI74jk8Jqe0g8b1kAKCBIIlwF6qlM4A")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("box", box))
    dispatcher.add_handler(CommandHandler("pallete", pallete))
    dispatcher.add_handler(CommandHandler("Epallete", Epallete))
    dispatcher.add_handler(CommandHandler("foto", chat))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()