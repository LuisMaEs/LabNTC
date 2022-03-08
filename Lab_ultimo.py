from multiprocessing import Event
import tkinter as tk
import time
from tkinter.constants import ON
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import threading
from scipy.optimize import curve_fit
import pyvisa 

rm = pyvisa.ResourceManager() # Creamos el objeto Resource Manager
print(rm.list_resources()) # Imprimimos la lista de recursos: se entiende recursos por instrumentos conectados al pc.

global Fecha
global Contador
contador_sesion=0
######################################## Recuperamos el Log ##################################################
# Aquí se recupera el contador diario
local = time.localtime()
Log= pd.read_csv('Log.txt', sep=',')
Fecha= '%02d/%02d/%02d' % ( local.tm_mday,local.tm_mon,local.tm_year)

print(str(Log.loc[Log['Fecha']=='d']['contador'])) 
if str(Log.loc[Log['Fecha']==Fecha]['contador']) == 'Series([], Name: contador, dtype: int64)':
    Contador=0
else: 
    Contador=int(Log.loc[Log['Fecha']==Fecha]['contador'])

print(Contador)
###############################################################################################################

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
    
class Page1(Page):
    global Power
    Power=0
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)                
        btn_on_off= tk.Button(self, text='State : Off', command=lambda widget="btn_on_off" : Page1.SwitchOnOff(btn_on_off) ,bg='red') 
        btn_on_off.pack(side="top", fill="both", expand=True)

        ELambda=tk.Entry(self,textvariable=entry_var)
        ELambda.pack(side="top", fill="both", expand=True)

        btn_set_lambda=tk.Button(self, text='Go to Lambda', command=Page1.GoToLambda )
        btn_set_lambda.pack(side="top", fill="both", expand=True)

    def SwitchOnOff(button):
        global Power
        inst = rm.open_resource('GPIB0::20::INSTR') 
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        Power=int(inst.query('sour1:chan1:pow:stat?'))
        if Power==0:
        
            mensaje='SOURCE1:CHAN1:POW:STATE 1'
            inst.write(mensaje)
            button.config(bg='green')
            button.config(text='State : On')
            Power=1
        
        else:
        
            mensaje='SOURCE1:CHAN1:POW:STATE 0'
            inst.write(mensaje)
            button.config(bg='red')
            button.config(text='State : Off')
            Power=0
        inst.close()
         
    
    def GoToLambda():
        if bool(entry_var.get())==1:
            if  1520<float(entry_var.get())<1630:
                mensaje='SOURCE1:CHAN1:WAVE ' + entry_var.get() + 'NM'
                print(mensaje)

            else:
                print('Longitud de onda fuera de rango. Rango válido de 1521 nm a 1629 nm. \n')


class Page2(Page):
    
    global OnOff
    global contador
    
    global lim1,lim2
    lim1=' '
    lim2= ' '
    global x,y
    global lambda_central
    global canvas
    global ax1,fig, cid

    def Hilos():
        t1=threading.Thread(target=Page2.BarridoContinuo).start()
        t1.join()
    
    def Hilos2():
        t2=threading.Thread(target=Page2.Ajustar).start()
        t2.join()

    def __init__(self, *args, **kwargs):
       global canvas
       global ax1,fig, cid
       Page.__init__(self, *args, **kwargs)
       fig,ax1= plt.subplots()
       canvas = FigureCanvasTkAgg(fig, master=self)  # Generate canvas instance, Embedding fig in root
       canvas.draw()
       canvas.get_tk_widget().place(relx = 0.7, rely = 0.4, anchor = 'center')
       toolbar = NavigationToolbar2Tk(canvas, self)
       toolbar.place(relx = 0.7, rely = 0.8, anchor = 'center')
       toolbar.update()
       canvas.get_tk_widget().place(relx = 0.7, rely = 0.4, anchor = 'center')
       
       cid=fig.canvas.callbacks.connect('button_press_event', callback) # Clicks en el plot

       global lim1,lim2
       global label1, entry_ajust
       

       label_lambda_min=tk.Label(self,text='Longitud de onda inicial (nm)')
       label_lambda_min.grid(row=0,column=0,ipadx=5,ipady=15)
       entry_lambda_min=tk.Entry(self,textvariable=entry_var1)
       entry_lambda_min.grid(row=0,column=1,ipadx=5,ipady=15)
       entry_lambda_min.insert(0, "1530")
       
       label_lambda_max=tk.Label(self,text='Longitud de onda final (nm)')
       label_lambda_max.grid(row=1,column=0,ipadx=5,ipady=15)
       entry_lambda_max=tk.Entry(self,textvariable=entry_var2)
       entry_lambda_max.grid(row=1,column=1,ipadx=5,ipady=15)
       entry_lambda_max.insert(0, "1620")
       
       label_lambda_speed=tk.Label(self,text='Velocidad del barrido (nm/s)')
       label_lambda_speed.grid(row=2,column=0,ipadx=5,ipady=15)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var3)
       entry_lambda_speed.grid(row=2,column=1,ipadx=5,ipady=15)
       entry_lambda_speed.insert(0, "10")

       label_lambda_res=tk.Label(self,text='Resolución (pm)')
       label_lambda_res.grid(row=3,column=0,ipadx=5,ipady=15)
       entry_lambda_res=tk.Entry(self,textvariable=entry_var4)
       entry_lambda_res.grid(row=3,column=1,ipadx=5,ipady=15)
       entry_lambda_res.insert(0, "25")

       label_lambda_num=tk.Label(self,text='Número de barridos')
       label_lambda_num.grid(row=4,column=0,ipadx=5,ipady=15)
       entry_lambda_num=tk.Entry(self,textvariable=entry_var5)
       entry_lambda_num.grid(row=4,column=1,ipadx=5,ipady=15)
       entry_lambda_num.insert(0, "1")
       
       btn_barrido_cont=tk.Button(self, text='Hacer barrido', command= Page2.Hilos)
       btn_barrido_cont.grid(row=5,column=0,columnspan=5,ipadx=5,ipady=15)

       btn_barrido_cont=tk.Button(self, text='Stop Barrido', command=Page2.Stop)
       btn_barrido_cont.grid(row=5,column=2,columnspan=5,ipadx=5,ipady=15)

       btn_barrido_cont=tk.Button(self, text='Ajustar', command=Page2.Hilos2)
       btn_barrido_cont.grid(row=9,column=1,columnspan=5,ipadx=5,ipady=15)

       btn_barrido_cont=tk.Button(self, text='Resetear', command=reset)
       btn_barrido_cont.grid(row=9,column=2,columnspan=5,ipadx=5,ipady=15)

       label1 = tk.Label(self, text='Puntos del ajuste', fg="black")
       label1.grid(row=8,column=0,columnspan=5,ipadx=5,ipady=15)

       entry_ajust = tk.Entry(self, textvariable=entry_var10 )
       entry_ajust.grid(row=8,column=3,columnspan=5,ipadx=5,ipady=15)

       #entry_lambda_min=tk.Entry(self,textvariable=entry_var1)

       choices=['dBm','W','mW']
       Seleccion=ttk.Combobox(self, values=choices, state="readonly",textvariable=entry_var6 )
       Seleccion.insert(0, "dBm")
       Seleccion.grid(row=6,column=0,columnspan=5,ipadx=5,ipady=15)
       Seleccion.current(0)

       choices1=['Barrido Único','Múltiples Barridos','Barrido Continuo. Stop manual']
       Seleccion1=ttk.Combobox(self, values=choices1, state="readonly",textvariable=entry_var7 )
       Seleccion1.grid(row=6,column=2,columnspan=5,ipadx=5,ipady=15)
       Seleccion1.current(0)

       choices2=['Gaussian', 'Lorentzian','Linear','Cuadrático']
       Seleccion2=ttk.Combobox(self, values=choices2, state="readonly",textvariable=entry_var8 )
       Seleccion2.grid(row=9,column=0,columnspan=4,ipadx=5,ipady=12)
       Seleccion2.current(0)

       choices3=['Seguir: No','Seguir: Sí' ]
       Seleccion3=ttk.Combobox(self, values=choices3, state="readonly",textvariable=entry_var9 )
       Seleccion3.grid(row=10,column=0,columnspan=5,ipadx=5,ipady=12)
       Seleccion3.current(0)
       



    def find_nearest(array,value):
        idx = (np.abs(array-value)).argmin()
        #print(type(idx))
        return idx

    def BarridoContinuo():
        global contador_sesion
        global contador_int
        global OnOff
        global Contador
        global Archivo
        orden=[]
        OnOff=1  
        
        inst = rm.open_resource('GPIB0::20::INSTR')
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.write('*cls')

        wavelength_start=float(entry_var1.get())
        wavelength_finish= float(entry_var2.get())
        wavelength_step= float(entry_var4.get())*math.pow(10,-3)
        scan_speed= float(entry_var3.get())
        num_barrido=int(entry_var5.get())
        Unidades=entry_var6.get()

        avg_time = 0.1 # photodiode average time
        rangeMAX = 10 #dBm
        sensorAVG = 1 #miliseconds
        laserPOWER = 6 #dBm
        wavelength = np.arange(wavelength_start,wavelength_finish,wavelength_step) # nm
        ###########
        calcpoints = (float(wavelength_finish)-float(wavelength_start))/float(wavelength_step)
        exppoints = str(int(calcpoints))
        points = int(len(wavelength))
        estSweepTime =  int((float(wavelength_finish) - float(wavelength_start))/float(scan_speed))

        if points>4000:
            print('Excede el número máximo de puntos. Bajar resolución.')
            return
        if 1520>wavelength_start or wavelength_finish>1630 or wavelength_finish<wavelength_start:
            print('Intervalo inválido. Ha de estar estrictamente contenido en 1520-1630 nm')
            return

        ############################################### Lista de órdenes ################################################### 
        
        orden.append('SENS2:CHAN1:POW:UNIT 1')
        orden.append('SOURCE1:CHAN1:POW 6DBM')
        orden.append('SOURCE1:CHAN1:POW:STATE 1')
        orden.append('SOUR1:CHAN1:WAV '+str(wavelength_start)+'NM')
        orden.append('sour1:AM:stat OFF')       
        orden.append('SOUR1:CHAN1:WAV:SWE:STAR '+str(wavelength_start)+'NM')
        orden.append('SOUR1:CHAN1:WAV:SWE:STOP '+ str(wavelength_finish)+'NM')
        orden.append('SOUR1:CHAN1:WAV:SWE:SPE '+str(scan_speed)+'nm/s')
        orden.append('SENS2:CHAN1:POW:ATIM 1ms')
        orden.append('SOUR1:CHAN1:WAV:SWE:CYCL 1')
        orden.append('TRIG1:CHAN1:OUTP STF')
        orden.append('SOUR1:CHAN1:WAV:SWE:MODE CONT')
        orden.append('init2:cont 1')
        orden.append('sour1:wav:swe:llog 1')
        orden.append('SOUR1:CHAN1:WAV:SWE:STEP '+str(wavelength_step)+'nm')
        orden.append('SENS2:CHAN1:FUNC:PAR:LOGG '+str(points)+','+str(avg_time)+'ms')
        orden.append('TRIG2:CHAN1:INP SME')
        orden.append('SENS2:CHAN1:FUNC:STAT STAB,START')
        orden.append('SOUR1:CHAN1:WAV:SWE 1')

        #####################################################################################################################

        contador_int=1 #Contador interno de la funcion pero que se usa en el plot
        # Lista de instrucciones que se le van a mandar al láser sobre el barrido
        while OnOff==1:
        
            for i in orden: 
                print(i)
                inst.write(i)
            
            time.sleep(estSweepTime+3)
            #root.after(estSweepTime*1000+3000)
            loggingStatus = "PROGRESS"
            while loggingStatus.endswith("PROGRESS"):
                loggingStatus = inst.query("SENS2:FUNC:STAT?").strip()
                print(loggingStatus)
                time.sleep(0.5)
                #root.after(500)

            values=inst.query_binary_values('SENS2:CHAN1:FUNC:RES?')
            time.sleep(0.2)
            wavelengthreal=inst.query_binary_values('SOUR1:CHAN1:READ:DATA? LLOG',datatype='d') 

            inst.write('SENS2:CHAN1:FUNC:STAT STAB,STOP')
            inst.write('TRIG2:CHAN1:INP IGN')



            wavelengthreal=wavelengthreal[1:int(len(wavelength)+2)]
            wavelengthreal=np.array(wavelengthreal) #Hay que sumarle 2 por las dimensiones, funciona

            dfexperimento = pd.DataFrame({"Longitud de onda(nm)" : wavelengthreal, "Potencia(W)" : values})
            #10*np.log10(values)+30

            if entry_var7.get()=='Múltiples Barridos':
                if num_barrido==contador_int:
                    OnOff=0

            if entry_var7.get()=='Barrido Único':
                OnOff=0

            contador_int=contador_int+1 #contador interno

            ####################################### Guardamos los datos ################################################

            Archivo = 'Resultados_' + Fecha + '_' + str(Contador) + '.csv'
            dfexperimento.to_csv(Archivo, index=False)

            if Contador == 0:
                new_row = {'Fecha':Fecha, 'contador':Contador}
                Log = Log.append(new_row, ignore_index=True)

            Log.loc[Log.Fecha==Fecha, 'contador']= Contador
            Log.to_csv('Log.txt', index=False)

            
            ############################################################################################################
            Page2.plotear() # Llamamos al plot dentro de la string en la que estamos

            Contador=Contador+1 #Contador global sube una unidad
            contador_sesion=contador_sesion+1
            contador_int=contador_int+1

        inst.close #Cerrar el instrumento



    def plotear():

        global contador_int
        global Archivo

        Seguimiento= entry_var9.get()
        Unidades=entry_var6.get()

        #Seguimiento= entry_var9.get()
        #Archivo= 'Resultados_'+str(contador)+'.csv'

        df = pd.read_csv(Archivo, sep=",")
        potencia = df.to_numpy()[:,1]
        wavelength = df.to_numpy()[:,0]

        if contador_int % 3==0:
            ax1.cla()
            for x in range(0,3):

                Archivo_aux = 'Resultados_'+ Fecha+'_'+ str(Contador-x)+'.csv'
                #Archivo_aux= 'Resultados_'+str(contador-x)+'.csv'

                df = pd.read_csv(Archivo_aux, sep=",")
                potencia_aux = df.to_numpy()[:,1]
                wavelength_aux = df.to_numpy()[:,0]
                ax1.plot(wavelength_aux,10*np.log10(potencia_aux)+30)

        elif (contador_int>3):
            ax1.cla()

            for x in range(0,3):
                Archivo_aux= 'Resultados_'+ Fecha+'_'+ str(Contador-x)+'.csv'
                df = pd.read_csv(Archivo_aux, sep=",")
                potencia_aux = df.to_numpy()[:,1]
                wavelength_aux = df.to_numpy()[:,0]
                ax1.plot(wavelength_aux,10*np.log10(potencia_aux)+30)

        elif Unidades=='dBm': 
            print('llega?') 
            ax1.plot(wavelength, 10*np.log10(potencia)+30)
            ax1.set_ylabel('Power(dBm)')

        ax1.set_xlabel('Wavelength(nm)')
        ax1.set_navigate(True)
        #plt.xlim(wavelength[0], wavelength[-1])
        plt.xlim(wavelength[0],wavelength[-1])
        canvas.draw()

        if Seguimiento=='Seguir: Sí':
            Page2.Ajustar()
    
                 
    def Stop():
        global OnOff
        OnOff=0
    
    def fun_Gauss( x, H, A, x0, sigma):
        return H + A * np.exp(-(x - x0)**2 / (2 * sigma ** 2))
    
    def fun_Lorentz(x, H, A, x0,gamma):
        return H + A*(gamma**2)/((x-x0)**2+gamma**2)

    def fun_linear(x,a,b):
        return x*a+b
    
    def fun_square(x,a,b,c):
        return a*x**2 + b*x + c

    def Ajustar():

        global coords
        global Ajustes
        global contador
        global lim1,lim2
        global x,y
        global ax1
        global lambda_central
        global Amplitud
        global contador_sesion

        #Archivo= 'Resultados_'+str(contador)+'.csv'
        Seguimiento= entry_var9.get()
        df = pd.read_csv(Archivo, sep=",")

        wavelength = df.to_numpy()[:,0]
        potencia=np.log10(df.to_numpy()[:,1])*10+30
        #Amplitud=Page2.find_nearest(potencia,coords[2])
        Tipo_ajust=entry_var8.get()
        
        p1=Page2.find_nearest(wavelength,coords[0])
        p2=Page2.find_nearest(wavelength,coords[1])
        #entry_var_lim1.set(wavelength[p1])
        #entry_var_lim2.set(wavelength[p2])
        print(wavelength[p1],wavelength[p2])
        print(contador)

        lim1=wavelength[p1]
        lim2=wavelength[p2]

        label1.config(text='lim1=%5.3f, lim2=%5.3f, Amplitud=%5.3f' % (lim1,lim2,Amplitud))
        x=wavelength[p1:p2]
        y=potencia[p1:p2]
        print(Tipo_ajust)
        print(str(Tipo_ajust))
        x1=np.linspace(lim1,lim2,1000)
        
        lambda_central=(lim1+lim2)/2

        if Seguimiento=='Seguir: Sí':
            lambda_central=Ajustes[contador_sesion-1]
            lim1 = lim1 + (Ajustes[contador_sesion]-Ajustes[contador_sesion-1])
            lim2 = lim2 + (Ajustes[contador_sesion]-Ajustes[contador_sesion-1])
            p1=Page2.find_nearest(wavelength,lim1)
            p2=Page2.find_nearest(wavelength,lim2)
            x1=np.linspace(lim1,lim2,1000)
            x=wavelength[p1:p2]
            y=potencia[p1:p2]

            
        if str(Tipo_ajust)=='Gaussian':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_Gauss,x,y,p0 = [5,Amplitud, lambda_central, 0.1])
            print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_Gauss(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))

        if str(Tipo_ajust)=='Lorentzian':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_Lorentz,x,y,p0 = [5,Amplitud, lambda_central, 0.1])
            print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, gamma=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_Lorentz(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, gamma=%5.3f' % tuple(popt))

        if str(Tipo_ajust)=='Linear':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_linear,x,y,p0 = [-5,1])
            print('fit: a=%5.3f, b=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_linear(x1,*popt), *popt, 'r-', label= 'fit: a=%5.3f, b=%5.3f' % tuple(popt))

        if str(Tipo_ajust)=='Cuadrático':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_square,x,y,p0 = [-5,-10, 1])
            print('fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_square(x1,*popt), *popt, 'r-', label= 'fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

        #if Seguimiento=='Seguir: Sí':
        #    lambda_central=lambda_antigua
        #lambda_central=float(popt[2])

        media_fit=float(popt[2]) # meter la media del fit
        Ajustes.append(media_fit) # Añadirlo a la lista de ajustes

        if Seguimiento=='Seguir: Sí':
            print(media_fit)
            print(type(media_fit))

        plt.xlim(wavelength[0], wavelength[-1])
        canvas.draw()
        
            

                

class Page3(Page):

   global ax2,ax3,fig2,fig3,canvas2,canvas3

   def __init__(self, *args, **kwargs):
       global ax2,ax3,fig2,fig3,canvas2,canvas3
       Page.__init__(self, *args, **kwargs)
       
       
       fig2,ax2= plt.subplots()
       fig3,ax3= plt.subplots()
       
       Archivo= 'Resultados_'+str(contador)+'.csv'
       df = pd.read_csv(Archivo, sep=",")
       wavelength = df.to_numpy()[:,0]
       potencia=np.log10(df.to_numpy()[:,1])*10+30

       label = tk.Label(self, text="This is page 3")
       label.pack(side="top", fill="both", expand=True)
      
       canvas2 = FigureCanvasTkAgg(fig2, master=self)  # Generate canvas instance, Embedding fig in root
       canvas2.get_tk_widget().place(relx = 0.25, rely = 0.6, anchor = 'center')
       canvas2.draw()

       canvas3 = FigureCanvasTkAgg(fig3, master=self)  # Generate canvas instance, Embedding fig in root
       canvas3.get_tk_widget().place(relx = 0.75, rely = 0.6, anchor = 'center')
       canvas3.draw()
    
       toolbar2 = NavigationToolbar2Tk(canvas2, self)
       toolbar2.place(relx = 0.25, rely = 0.2, anchor = 'center')
       toolbar2.update()

       toolbar3 = NavigationToolbar2Tk(canvas3, self)
       toolbar3.place(relx = 0.75, rely = 0.2, anchor = 'center')
       toolbar3.update()

       ax2.plot(wavelength,potencia,'b')
       ax2.set_ylabel('Power(dBm)')
       ax2.set_xlabel('Wavelength')
       #ax2.format_coord = lambda x2, y2: "({0:2}, ".format(y2) +  "{0:2})".format(x2)

       ax3.plot(wavelength,potencia,'g')
       ax3.set_ylabel('Power(dBm)')
       ax3.set_xlabel('Wavelength')


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)
        p3 = Page3(self)
        
        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text="Page 1", command=p1.show)
        b2 = tk.Button(buttonframe, text="Page 2", command=p2.show)
        b3 = tk.Button(buttonframe, text="Page 3", command=p3.show)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        p1.show()    



#def callback(event):
#    print(event.x, event.y)

contador=0
global coords
global Ajustes
Ajustes=[]
coords=[]

def callback(event):

    global coords
    global Amplitud
    xevent=event.xdata
    print(xevent)
    coords.append(xevent)
    #Archivo= 'Resultados_'+str(contador)+'.csv'

    if len(coords)==3:
        df = pd.read_csv(Archivo, sep=",")
        wavelength = df.to_numpy()[:,0]# + 3*contador
        #potencia=np.log10(df.to_numpy()[:,1])*10+30
        #Amplitud=Page2.find_nearest(potencia,coords[2])
        p1=Page2.find_nearest(wavelength,coords[0])
        p2=Page2.find_nearest(wavelength,coords[1])

        lim1=wavelength[p1]
        lim2=wavelength[p2]
        
        yevent=event.ydata
        Amplitud = yevent

        print( 'Illo esto es lo que sale en la y=%5.3f '% yevent)
        
        label1.config(text='lim1=%5.3f, lim2=%5.3f, y=%5.3f' % (lim1,lim2,yevent))
        fig.canvas.callbacks.disconnect(cid)


def reset():
    global coords
    cid=fig.canvas.callbacks.connect('button_press_event', callback)
    coords=[]



if __name__ == "__main__":

    root = tk.Tk()
    
    entry_var = tk.StringVar()
    entry_var1 = tk.StringVar()
    entry_var2 = tk.StringVar()
    entry_var3 = tk.StringVar()
    entry_var4 = tk.StringVar()
    entry_var5 = tk.StringVar()
    entry_var6 = tk.StringVar()
    entry_var7 = tk.StringVar()
    entry_var8 = tk.StringVar()
    entry_var9 = tk.StringVar()
    entry_var10 = tk.StringVar()
    entry_var_lim1 = tk.StringVar()
    entry_var_lim2 = tk.StringVar()
    entry_var_Amplitud = tk.StringVar()
    
    main = MainView(root)
    main.pack(side="bottom", fill="both", expand=True)
    root.wm_geometry("1200x700+100+100")
    root.mainloop()

# Lo que quiere jaime que queda por hacer:
# En la tercera ventana hay que poner dos plots para que plotee el espectro y al lado la evolución de la resonancia en desplazamiento
#  frente a tiempo (tomar el tiempo al acabar cada barrido).
# En la tercera ventana tiene que haber un boton para tirar lso barridos y el experimento en si. También pondría una opción
# para hacer que se puedan guardar las gráficas de cada plot y tal. 