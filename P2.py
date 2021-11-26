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
import numpy as np

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
inst.write('SOURCE1:CHAN1:POW 6DBM')
print(err(inst))
inst.write('SOURCE1:CHAN1:POW:STATE 1') # Encender el Láser 
print(err(inst))

time.sleep(2)                         # Esperar 5 segundos para que se estabilice el láser
print(inst.query('READ2:CHAN1:POW?'))
print(err(inst))
#FOTO1
inst.write('SOUR1:CHAN1:WAV 1550NM') #Seleccionar lambda
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:STAR 1550NM') #Lambda inicial barrido
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:STOP 1600NM') #Lambda final barrido
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:SPE 10nm/s') #Velocidad de barrido
print(err(inst))
inst.write('SENS2:CHAN1:POW:ATIM 1ms') #Es el tiempo para que el módulo realice la medición y la media durante ese intervalo
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:CYCL 1') #El número de ciclos a realizar
print(err(inst))
inst.write('TRIG1:CHAN1:OUTP STF') #El output del trigger se hace que sale cuando una Sweep Step termine
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:MODE CONT') # Modo continuo de sweep para el láser
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:AM:STAT OFF') #Modulación en amplitud apagada
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:LLOG ON') #Lambda loggin enabled
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE:STEP 100pm') #Resolución en Lambda en picometros
print(err(inst))
#Con lambda inicial, final y sweeping speed hay que sacar parámetros para el logging

inst.write('SENS2:CHAN1:FUNC:PAR:LOGG 500,1ms')#Número de puntos y el tiempo de medida
print(err(inst))
inst.write('TRIG2:CHAN1:INP SME')
print(err(inst))
inst.write('SENS2:CHAN1:FUNC:STAT LOGG,START')
print(err(inst))
inst.write('SOUR1:CHAN1:WAV:SWE 1') #Empezar sweep
time.sleep(2)  

inst.write('SENS2:CHAN1:FUNC:RES?')
values=np.array(inst.read_binary_values('SENS2:CHAN1:FUNC:RES?',datatype='d'))#Esto lleva WRITE Y DESPUÉS READ O UN QUERY
np.savetxt('testascii.out', values, delimiter=',') 
print(err(inst))

print(values)
inst.write('SOUR1:CHAN1:WAV:SWE 0') #logging off



#La cosa es: (Lambdafinal-lambdainicial)/speed=tiempo de barrido; tiempo de barrido/numero de pasos=tiempo de cada paso(en segundos)
#Multiplicamos por 1000 para ponerlo en ms(Aquí quien hizo el anterior programa puso x100, supongo que para espaciar las medidas)
# OJO el tiempo de cada paso no puede ser menor que un ms
# (Lambdafinal-lambdainicial)*1000/lambdaresolution=número de puntos (estaba la resolucion en picómetros por eso el factor 1000)

#The following settings are the prerequisites for Lambda Logging:
#Set “[:SOURce[n]][:CHANnel[m]]:WAVelength:SWEep:MODE” on page 141 to CONTinuous.
#Set “:TRIGger[n][:CHANnel[m]]:OUTPut” on page 176 to STFinished (step finished).
#Set “[:SOURce[n]][:CHANnel[m]]:WAVelength:SWEep:CYCLes” on page 137 to 1.
#Set “[:SOURce[n]][:CHANnel[m]]:AM:STATe[l]” on page 117 to OFF.
#If any of the above prerequisites are not met, then when the sweep is started
#the status
#"Sweep parameters inconsistent" will be returned and Lambda Logging will automatically
#be turned off.

#time.sleep(3)                         # Esperar 5 segundos por amor al arte
#print(inst.write('SOURCE1:CHAN1:POW:STATE 0')) # Apagar el Láser

#inst.write('SOURCE1:CHAN1:POW:STATE 0')
inst.close()                          # Cerrar el objeto, acabar medidas.

#Todo bien, funciona correctamente. 24/11/2021