# REQUISITOS DEL SISTEMA 
# Intentaré ser breve, pero hay unas cuantas cosas que hacer antes de poder utilizar el módulo.
# Instalar: 
# - NI-VISA (se instala todo: NI package management, NI MAX ...)
# - Paquete de NI-VISA: ni-488.2_21.0
# - Anaconda para manejar los paquetes de Python o similares. Realmente podríamos crear entornos virtuales con nvenv y usar pip
# - Uso Python 3.8.12
# - Paquete PyVISA 1.11.3 (No está en el repositorio de Anaconda. Hay que instalarlo con 'pip install')
# - Paquetes típicos de python: Pandas, matplotlib, math ...
# Poco más, antes de tirar el código hay que ver en NI MAX que el pc reconoce el dispositvo GPIB sin problemas. Si hay problemas,
# revisar que esté el paquete de NI-VISA e intentar ver la páginas web de PyVISA que tiene bastante bibliografía.



import pyvisa # Paquete que manejará la interfaz entre Python y la GPIB.
import time # Necesario para usar delays.
import tkinter as tk


rm = pyvisa.ResourceManager() # Creamos el objeto Resource Manager
print(rm.list_resources()) # Imprimimos la lista de recursos: se entiende recursos por instrumentos conectados al pc.

inst = rm.open_resource('GPIB0::20::INSTR') # Abrimos el recurso deseado. En este caso es el Multimetro de Agilent8163A 
# (por defecto GPIB::20)
print(inst.query("*IDN?")) # Función básica que pregunta al instrumento quién es. Protocolaria
print(inst.query("*OPT?")) # Devuelve los módulos instalados y su localización.


# Configuración necesaria para la comunicación. En el caso del multimetro que queremos controlar, 
# todos los mensajes han de acabar en un retorno de carro (saltar línea).
inst.read_termination = '\n'
inst.write_termination = '\n'
# INFO ADICIONAL: En general vamos a enviar las órdenes una a una. Si quisieramos encadenar órdenes seguidas, deberían ser 
# separadas por ;

def err(instrumento): # Función que comprueba la cola de errores
    m=instrumento.query('SYST:ERR?')
    #if m !=0:
    #    return  print(m)
    return  print(m)
     
# Apunte: query manda un write y un read consecutivos


############################################### EJEMPLO 101 #################################################
# Objetivo: Seleccionar cierta longitud de onda y potencia, encender el láser y medir la salida.
# Apuntes necesarios: El láser se encuentra en el slot 1. El módulo de sensado en el slot 2. Ambos son monocanal
# La verdad es que la nomenclatura es bastante autoexplicativa.

print(inst.query('SOURCE1:CHAN1:WAV?')) # Preguntar a qué longitud de onda se encuentra el multimetro
print(err(inst))
#inst.write('SOURCE1:CHAN1:POW:ATT 7.0') # Ponemos el Láser a 7 dBm
inst.write('SENS2:CHAN1:POW:UNIT 0')  # Seleccionar dBm como unidad
print(err(inst))
inst.write('SOURCE1:CHAN1:POW:STATE 1') # Encender el Láser 

time.sleep(2)                         # Esperar 5 segundos para que se estabilice el láser
#print(inst.query('READ2:CHAN1:POW?')) # Lectura de la potencia 



#inst.write('SENS2:CHAN1:POW:RANGE:AUTO 1')
#print(err(inst))
#inst.write('SENS2:CHAN1:POW:RANGE:AUTO 1')
#print(err(inst))


inst.write('SOURCE1:CHAN1:WAV:SWE:MODE CONTINUOUS')
print(err(inst))
inst.write('SOURCE1:CHAN1:WAV:SWE:START 1550NM')
print(err(inst))
inst.write('SOURCE1:CHAN1:WAV:SWE:STOP 1600NM')
print(err(inst))
inst.write('SOURCE1:CHAN1:WAV:SWE:SPEED 10nm/s')
print(err(inst))
inst.write('SOURCE1:CHAN1:WAV:SWE START')


'SENS2:CHAN1:FUNC:RES?'
'SENS2:CHAN1:FUNC:PAR:LOGG'
'TRIG2:CHAN:INP SME'

#FOTO1
'SOUR1:CHAN1:WAV'
'SOUR1:CHAN1:WAV:SWE:STAR'
'SOUR1:CHAN1:WAV:SWE:STOP'
'SOUR1:CHAN1:WAV:SWE:SPE'
'SENS2:CHAN1:POW:ATIM 1ms'
'SOUR1:CHAN1:WAV:SWE:CYCL'
'TRIG1:CHAN1:OUTP STF'











time.sleep(10)                         # Esperar 5 segundos por amor al arte
#print(inst.write('SOURCE1:CHAN1:POW:STATE 0')) # Apagar el Láser

print(err(inst))


inst.close()                          # Cerrar el objeto, acabar medidas.

#Todo bien, funciona correctamente. 05/11/2021