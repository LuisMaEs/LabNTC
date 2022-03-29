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
#from #pandastable import Table, TableModel
import ctypes

# No sé si ira


class Page(tk.Frame):
    global contador_sesion
    contador_sesion = 0
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
    
class Page1(Page):
    global Power
    Power=0
    def __init__(self, *args, **kwargs):
        global Etiqueta_potencia
        Page.__init__(self, *args, **kwargs)                
        btn_on_off= tk.Button(self, text='State : Off', font=("Calibri",30),justify="center",width=6,fg="black",command=lambda widget="btn_on_off" : Page1.SwitchOnOff(btn_on_off) ,bg='red') 
        btn_on_off.place(relx = 0.35, rely = 0.2, anchor = 'center', relwidth=0.3, relheight=0.2)
        #btn_on_off.grid(row=0,column=0,ipadx=100,ipady=80)

        ELambda=tk.Entry(self,font=("Calibri",30),justify="center",width=6,fg="black",textvariable=entry_var)
        ELambda.place(relx = 0.35, rely = 0.4, anchor = 'center', relwidth=0.3, relheight=0.2)

        btn_set_lambda=tk.Button(self, text='Go to Lambda',font=("Calibri",30),justify="center",width=6,fg="black", command=Page1.GoToLambda )
        btn_set_lambda.place(relx = 0.50, rely = 0.6, anchor = 'center', relwidth=0.3, relheight=0.2)

        btn_Potencia = tk.Button(self, text="Potencia",font=("Calibri",30),justify="center",width=6,fg="black", command=Page1.Potencia)
        btn_Potencia.place(relx = 0.65, rely = 0.4, anchor = 'center', relwidth=0.3, relheight=0.2)

        Etiqueta_potencia=tk.Label(self, text="Potencia",fg="white",font=("Calibri",30),justify="center",bg='grey',width=6,borderwidth=15, relief="solid")
        Etiqueta_potencia.place(relx = 0.65, rely = 0.2, anchor = 'center', relwidth=0.3, relheight=0.2)

    def Potencia():
        #Medimos la potencia
        Etiqueta_potencia.config(text='SE HA MEDIDO LA POWER'+'dBm')



    def SwitchOnOff(button):
        global Power
        button.config(state=tk.DISABLED)
        if Power==0:
        
            mensaje='SOURCE1:CHAN1:POW:STATE 1'
            print(mensaje)
            button.config(bg='green')
            button.config(text='State : On')
            Power=1
        
        else:
        
            mensaje='SOURCE1:CHAN1:POW:STATE 0'
            print(mensaje)
            button.config(bg='red')
            button.config(text='State : Off')
            Power=0
            
        time.sleep(1)
        button.config(state=tk.NORMAL)
        return Power    
    
    def GoToLambda():
        if bool(entry_var.get())==1:
            if  1520<float(entry_var.get())<1630:
                mensaje='SOURCE1:CHAN1:WAVE ' + entry_var.get() + 'NM'
                print(mensaje)

            else:
                print('Longitud de onda fuera de rango. Rango válido de 1521 nm a 1629 nm. \n')


class Page2(Page):
    
    #global OnOff,ax1,fig, cid, canvas, lambda_central,lim1,lim2

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
       global  btn_barrido_cont
       fig,ax1= plt.subplots()
       canvas = FigureCanvasTkAgg(fig, master=self)  # Generate canvas instance, Embedding fig in root
       canvas.draw()
       canvas.get_tk_widget().place(relx = 0.6, rely = 0.4, anchor = 'center', relwidth=0.7, relheight=0.65)
       toolbar = NavigationToolbar2Tk(canvas, self)
       toolbar.place(relx = 0.65, rely = 0.75, anchor = 'center')
       toolbar.update()
       canvas.get_tk_widget().place(relx = 0.65, rely = 0.4, anchor = 'center',relwidth=0.675, relheight=0.65)
       
       ##canvas.get_tk_widget().place(relx = 0.7, rely = 0.3, anchor = 'center')
       #canvas.draw()

       #cid = fig.canvas.mpl_connect('button_press_event', callback)

       cid=fig.canvas.callbacks.connect('button_press_event', callback) # Clicks en el plot
       #canvas = FigureCanvasTkAgg(fig, master=root)  # Generate canvas instance, Embedding fig in root
       #canvas.draw()
       #canvas.get_tk_widget().pack(side='right')
       #toolbar = NavigationToolbar2Tk(canvas,root)
       #toolbar.update()
       #canvas.get_tk_widget().pack(side='right')
       #canvas.draw()



       global lim1,lim2
       global label1, entry_ajust
       
    ######################### LAS CINCO VARIABLES########################
       #englobar=tk.Label
       label_lambda_min=tk.Label(self,text='Longitud de onda inicial (nm)', font=('Helvetica',14), borderwidth=2, relief="groove")
       label_lambda_min.place(relx = 0.1, rely = 0.1, anchor = 'center', relwidth=0.15, relheight=0.05)
       entry_lambda_min=tk.Entry(self,textvariable=entry_var1,font=('Helvetica',14))
       entry_lambda_min.place(relx = 0.2, rely = 0.1, anchor = 'center', relwidth=0.05, relheight=0.05)
       entry_lambda_min.insert(0, "1530")
       
       label_lambda_max=tk.Label(self,text='Longitud de onda final (nm)',font=('Helvetica',14),  borderwidth=2, relief="groove")
       label_lambda_max.place(relx = 0.1, rely = 0.15, anchor = 'center', relwidth=0.15, relheight=0.05)
       entry_lambda_max=tk.Entry(self,textvariable=entry_var2,font=('Helvetica',14))
       entry_lambda_max.place(relx = 0.2, rely = 0.15, anchor = 'center', relwidth=0.05, relheight=0.05)
       entry_lambda_max.insert(0, "1620")
       
       label_lambda_speed=tk.Label(self,text='Velocidad del barrido (nm/s)',font=('Helvetica',14), borderwidth=2, relief="groove")
       label_lambda_speed.place(relx = 0.1, rely = 0.2, anchor = 'center', relwidth=0.15, relheight=0.05)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var3,font=('Helvetica',14))
       entry_lambda_speed.place(relx = 0.2, rely = 0.2, anchor = 'center', relwidth=0.05, relheight=0.05)
       entry_lambda_speed.insert(0, "10")

       label_lambda_res=tk.Label(self,text='Resolución (pm)',font=('Helvetica',14), borderwidth=2, relief="groove")
       label_lambda_res.place(relx = 0.1, rely = 0.25, anchor = 'center', relwidth=0.15, relheight=0.05)
       entry_lambda_res=tk.Entry(self,textvariable=entry_var4,font=('Helvetica',14))
       entry_lambda_res.place(relx = 0.2, rely = 0.25, anchor = 'center', relwidth=0.05, relheight=0.05)
       entry_lambda_res.insert(0, "25")

       #label_lambda_num=tk.Label(self,text='Número de barridos')
       #label_lambda_num.grid(row=4,column=0,ipadx=5,ipady=15)
       #entry_lambda_num=tk.Entry(self,textvariable=entry_var5)
       #entry_lambda_num.grid(row=4,column=1,ipadx=5,ipady=15)
       #entry_lambda_num.insert(0, "1")

    ###################################################### BOTONES #########################################

       btn_barrido_cont=tk.Button(self, text='Hacer barrido',font=('Helvetica',14), borderwidth=2, relief="raised", command= Page2.Hilos)
       btn_barrido_cont.place(relx = 0.125, rely = 0.3, anchor = 'center', relwidth=0.2, relheight=0.05)

       #btn_barrido_cont=tk.Button(self, text='Stop Barrido', command=Page2.Stop)
       #btn_barrido_cont.grid(row=5,column=2,columnspan=5,ipadx=5,ipady=15)

       choices=['dBm','W','mW']
       Seleccion=ttk.Combobox(self, values=choices, state="readonly",textvariable=entry_var6,font=('Helvetica',14) )
       Seleccion.insert(0, "dBm")
       Seleccion.place(relx = 0.2, rely = 0.4, anchor = 'center', relwidth=0.05, relheight=0.05)
       Seleccion.current(0)

       label_unidades = tk.Label(self, text='Unidades:', fg="black",font=('Helvetica',14))
       label_unidades.place(relx = 0.1, rely = 0.4, anchor = 'center', relwidth=0.15, relheight=0.05)


       choices2=['Gaussian', 'Lorentzian','Linear','Cuadrático']
       Seleccion2=ttk.Combobox(self, values=choices2, state="readonly",textvariable=entry_var8,font=('Helvetica',14) )
       Seleccion2.place(relx = 0.075, rely = 0.5, anchor = 'center', relwidth=0.1, relheight=0.05)
       Seleccion2.current(0)

       btn_ajust=tk.Button(self, text='Ajustar', font=('Helvetica',14),command=Page2.Hilos2)
       btn_ajust.place(relx = 0.175, rely = 0.5, anchor = 'center', relwidth=0.075, relheight=0.05)

       btn_reset=tk.Button(self, text='Resetear',font=('Helvetica',14), command=reset)
       btn_reset.place(relx = 0.25, rely = 0.5, anchor = 'center', relwidth=0.075, relheight=0.05)

       label1 = tk.Label(self, text='Puntos del ajuste',font=('Helvetica',14), fg="black")
       label1.place(relx = 0.15, rely = 0.45, anchor = 'center', relwidth=0.15, relheight=0.05)
       label_info = tk.Label(self, text='Ajustes:',font=('Helvetica',14), fg="black")
       label_info.place(relx = 0.05, rely = 0.45, anchor = 'center', relwidth=0.05, relheight=0.05)

       btn_add=tk.Button(self, text='Añadir ajuste',font=('Helvetica',14), command= Page2.Añadir)
       btn_add.place(relx = 0.175, rely = 0.6, anchor = 'center', relwidth=0.075, relheight=0.05)

       btn_supp=tk.Button(self, text='Suprimir ajuste', font=('Helvetica',14),command= Page2.Suprimir)
       btn_supp.place(relx = 0.25, rely = 0.6, anchor = 'center', relwidth=0.075, relheight=0.05)
       #choices3=['Seguir: No','Seguir: Sí' ]
       #Seleccion3=ttk.Combobox(self, values=choices3, state="readonly",textvariable=entry_var9 )
       #Seleccion3.grid(row=10,column=0,columnspan=5,ipadx=5,ipady=12)
       #Seleccion3.current(0)

    global contador_add
    contador_add=1   
    global lista_ajustes
    lista_ajustes=['Todos']
    
    def Suprimir ():
        Ajustes.drop(index=Ajustes.index[-1], axis=0, inplace=True)
        Ajustes_resultados.drop(index=Ajustes_resultados.index[-1], axis=0, inplace=True)
        print(Ajustes)
        print(Ajustes_resultados)
        lista_ajustes=list(Ajustes.index)
        lista_ajustes.append('Todos')

    def Añadir():

         global Ajuste_actual
         global Ajustes
         global Ajustes_resultados
         global contador_add, lista_ajustes
         Ajuste_aux = pd.DataFrame( [(Ajuste_actual)], columns=['lim1' ,'lim2','H','A','x0','sigma'], index=[str(entry_var8.get())+str(contador_add)])

         try :
            Ajustes 
            Ajustes=pd.concat([Ajustes, Ajuste_aux])
         except NameError: Ajustes = Ajuste_aux

         print(Ajustes)

         Ajust_aux = pd.DataFrame( [(lista_results)], columns=['H','A','x0','sigma'], index=[str(entry_var8.get())+str(contador_add)])
        # HAY QUE ARREGLAR LOS NOMBRES DEL CONTADOR SEGUN SEAN LORENTZ O GAUSSS
         try :
            Ajustes_resultados 
            Ajustes_resultados=pd.concat([Ajustes_resultados, Ajust_aux])

         except NameError: Ajustes_resultados = Ajust_aux

         print(Ajustes_resultados
         )
         lista_ajustes=list(Ajustes.index)
         lista_ajustes.append('Todos')
         contador_add=contador_add+1
         #contador_add_lorentz=contador_add_lorentz+1



    def find_nearest(array,value):
        idx = (np.abs(array-value)).argmin()
        #print(type(idx))
        return idx

    def BarridoContinuo(): #SOLO TIRO LA PRUEBA que es cargar el archivo guardado
        global Datos_3D
        global contador_sesion
        btn_barrido_cont.config(state=tk.DISABLED)
        Archivo= 'Resultados_0.csv'
        df = pd.read_csv(Archivo, sep=",")
        potencia = df.to_numpy()[:,1]
        wavelength = df.to_numpy()[:,0]
        ########################   Matriz auxiliar con los plots. Guardamos la matriz auxiliar
        Datos = np.dstack((wavelength,potencia))
        points=1000
        if contador_sesion == 0:
            Datos_3D = np.zeros(( 50, points, 2))
        
        contador_sesion=contador_sesion+1
        Datos_3D[:][:][contador_sesion]=Datos # Copiamos cada Datos en 3d por cada sesion
        time.sleep(3)
        print(contador_sesion)
        Page2.plotear()
        btn_barrido_cont.config(state=tk.NORMAL)
        #Plot=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
        #power=Plot[:,1] # Recuperar el array de power
        #wav=Plot[:,0] # Recuperar el array de wavelenght
    #    global OnOff
    #    global contador
    #    orden=[]
    #    OnOff=1  
    #    
    #    wavelength_start=float(entry_var1.get())
    #    wavelength_finish= float(entry_var2.get())
    #    wavelength_step= float(entry_var4.get())*math.pow(10,-3)
    #    scan_speed= float(entry_var3.get())
    #    num_barrido=int(entry_var5.get())
    #    Unidades=entry_var6.get()
#
    #    avg_time = 0.1 # photodiode average time
    #    rangeMAX = 10 #dBm
    #    sensorAVG = 1 #miliseconds
    #    laserPOWER = 6 #dBm
    #    wavelength = np.arange(wavelength_start,wavelength_finish,wavelength_step) # nm
    #    ###########
    #    calcpoints = (float(wavelength_finish)-float(wavelength_start))/float(wavelength_step)
    #    exppoints = str(int(calcpoints))
    #    points = int(len(wavelength))
    #    estSweepTime =  int((float(wavelength_finish) - float(wavelength_start))/float(scan_speed))
    #    if points>4000:
    #        print('Excede el número máximo de puntos. Bajar resolución.')
    #        return
    #    if 1520>wavelength_start or wavelength_finish>1630 or wavelength_finish<wavelength_start:
    #        print('Intervalo inválido. Ha de estar estrictamente contenido en 1520-1630 nm')
    #        return
    #    n=1
    #    print('Que horror')
#
    #    while OnOff==1:
#
    #        orden.append('SENS2:CHAN1:POW:UNIT 1')
    #        orden.append('SOURCE1:CHAN1:POW 6DBM')
    #        orden.append('SOURCE1:CHAN1:POW:STATE 1')
    #        orden.append('SOUR1:CHAN1:WAV '+str(wavelength_start)+'NM')
    #        orden.append('sour1:AM:stat OFF')       
    #        orden.append('SOUR1:CHAN1:WAV:SWE:STAR '+str(wavelength_start)+'NM')
    #        orden.append('SOUR1:CHAN1:WAV:SWE:STOP '+ str(wavelength_finish)+'NM')
    #        orden.append('SOUR1:CHAN1:WAV:SWE:SPE '+str(scan_speed)+'nm/s')
    #        orden.append('SENS2:CHAN1:POW:ATIM 1ms')
    #        orden.append('SOUR1:CHAN1:WAV:SWE:CYCL 1')
    #        orden.append('TRIG1:CHAN1:OUTP STF'
    #        orden.append('SOUR1:CHAN1:WAV:SWE:MODE CONT')
    #        orden.append('init2:cont 1')
    #        orden.append('sour1:wav:swe:llog 1')
    #        orden.append('SOUR1:CHAN1:WAV:SWE:STEP '+str(wavelength_step)+'nm')
    #        orden.append('SENS2:CHAN1:FUNC:PAR:LOGG '+str(points)+','+str(avg_time)+'ms')
    #        orden.append('TRIG2:CHAN1:INP SME')
    #        orden.append('SENS2:CHAN1:FUNC:STAT STAB,START')
    #        orden.append('SOUR1:CHAN1:WAV:SWE 1')
#
    #        for i in orden: 
    #            print(i)
    #        print('que pasa e')
    #        print('que pasa e')
#
    #        if entry_var7.get()=='Múltiples Barridos':
    #            if num_barrido==n:
    #                OnOff=0
    #        if entry_var7.get()=='Barrido Único':
    #            OnOff=0
    #        n=n+1
    #        time.sleep(0.3)#Funcionaaaaaaaa
    #        print('1')
    #        time.sleep(0.3)
    #        print('2')
    #        time.sleep(0.3)
    #        contador=contador+1
    #        Page2.plotear()
    #        print('Que horror')

            
    

    def plotear():
     
        #Seguimiento= entry_var9.get()
        #Unidades=entry_var6.get()
        Plot=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
        power=Plot[:,1] # Recuperar el array de power
        wav=Plot[:,0]

        ax1.cla()
        ax1.plot(wav,10*np.log10(power)+30)

        ax1.set_ylabel('Power(dBm)')
        ax1.set_xlabel('Wavelength(nm)')
        ax1.set_navigate(True)
        canvas.draw()
        plt.xlim(wav[0], wav[-1])
            
                 
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
       
        global contador
        global lim1,lim2
        global x,y
        global ax1
        global lambda_central
        global Amplitud
        global Ajuste_actual
        global lista_results

        #Archivo= 'Resultados_'+str(contador)+'.csv'
        #Seguimiento= entry_var9.get()
        #df = pd.read_csv(Archivo, sep=",")

        #wavelength = df.to_numpy()[:,0]
        #potencia=np.log10(df.to_numpy()[:,1])*10+30
        #Amplitud=Page2.find_nearest(potencia,coords[2])
        Tipo_ajust=entry_var8.get()
        Plot=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
        potencia=np.log10(Plot[:,1])*10+30 # Recuperar el array de power
        wavelength=Plot[:,0] # Recuperar el array de wavelenght
    
        p1=Page2.find_nearest(wavelength,coords[0])
        p2=Page2.find_nearest(wavelength,coords[1])
        #entry_var_lim1.set(wavelength[p1])
        #entry_var_lim2.set(wavelength[p2])
        Amplitud_auto=potencia[p1:p2].min()
        print(wavelength[p1],wavelength[p2])
        print(contador)
        lim1=wavelength[p1]
        lim2=wavelength[p2]
        label1.config(text='lim1=%5.3f, lim2=%5.3f' % (lim1,lim2))
        x=wavelength[p1:p2]
        y=potencia[p1:p2]

        print(Tipo_ajust)
        print(str(Tipo_ajust))

        x1=np.linspace(lim1,lim2,300)
        
        lambda_central=(lim1+lim2)/2

        offset=(potencia[p1]+potencia[p2])/2
        sigma_init= abs(lim2-lim1)/4

        Ajuste_actual=[lim1, lim2, offset, Amplitud_auto, lambda_central, sigma_init]
        print(Ajuste_actual)

        

        if str(Tipo_ajust)=='Gaussian':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_Gauss,x,y,p0 = Ajuste_actual[2:6])
            print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_Gauss(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))

        if str(Tipo_ajust)=='Lorentzian':
            ax1.cla()
            popt, _=curve_fit(Page2.fun_Lorentz,x,y,p0 = Ajuste_actual[2:6])
            print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, gamma=%5.3f' % tuple(popt))
            ax1.plot(wavelength,potencia,'r.')
            ax1.plot(x1 ,Page2.fun_Lorentz(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, gamma=%5.3f' % tuple(popt))

        #if str(Tipo_ajust)=='Linear':
        #    ax1.cla()
        #    popt, _=curve_fit(Page2.fun_linear,x,y,p0 = [-5,1])
        #    print('fit: a=%5.3f, b=%5.3f' % tuple(popt))
        #    ax1.plot(wavelength,potencia,'r.')
        #    ax1.plot(x1 ,Page2.fun_linear(x1,*popt), *popt, 'r-', label= 'fit: a=%5.3f, b=%5.3f' % tuple(popt))

        #if str(Tipo_ajust)=='Cuadrático':
        #    ax1.cla()
        #    popt, _=curve_fit(Page2.fun_square,x,y,p0 = [-5,-10, 1])
        #    print('fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
        #    ax1.plot(wavelength,potencia,'r.')
        #    ax1.plot(x1 ,Page2.fun_square(x1,*popt), *popt, 'r-', label= 'fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

        #if Seguimiento=='Seguir: Sí':
        #    lambda_central=lambda_antigua
        #lambda_central=float(popt[2])
        #media_fit=float(popt[2])
        
        

        #if Seguimiento=='Seguir: Sí':
        #    print(media_fit)
        #    print(type(media_fit))

        plt.xlim(wavelength[0], wavelength[-1])

        lista_results=list(popt)
        
        canvas.draw()
        
            

                

class Page3(Page):
    
    def Experimento():
        global contador_sesion
        global ax2,ax3,fig2,fig3,canvas2,canvas3, contador_int
        global Ajustes, Datos_3D, OnOff
        OnOff=1
        contador_int = 0 # Contador de en qué ciclo del experimento estamos

        Archivo= 'Resultados_0.csv'
        df = pd.read_csv(Archivo, sep=",")
        potencia = df.to_numpy()[:,1]
        wavelength = df.to_numpy()[:,0]
        ########################   Matriz auxiliar con los plots. Guardamos la matriz auxiliar
        Datos = np.dstack((wavelength,potencia))
        points=1000
        if contador_sesion == 0:
            Datos_3D = np.zeros(( 50, points, 2))

        num_barrido=int(entry_var5.get())

        while OnOff==1:
            if entry_var7.get()=='Múltiples Barridos': #Comprobar si se han hecho los suficientes barridos
                if num_barrido==contador_int:
                    OnOff=0
            contador_sesion=contador_sesion+1
            
            print(contador_sesion)
            print(contador_int)
            Datos_3D[:][:][contador_sesion]=Datos # Copiamos cada Datos en 3d por cada sesion
            Page3.PlotExp()

            contador_int+=1
        Ajustes_finales_exp.to_csv(str(entry_var12.get())+'Ajustes')


        # Ha de ser ejecutada en un hilo distinto al principal de la GUI
    #     global contador_sesion
    #     contador_sesion=0
    #     Plot=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
    #     potencia=np.log10(Plot[:,1])*10+30 # Recuperar el array de power
    #     wavelength=Plot[:,0] # Recuperar el array de wavelenght

    
    # ######################################################### Tirar experimento ##################################################
    # # Habré de descomentar esta parte para el programa de lab real
    #     global contador_int
    #     global OnOff
    #     global Contador
    #     global Archivo
    #     global Datos_3D
    #     orden=[] #Lista con las órdenes que se le van a pasar al módulo láser
    #     OnOff=1  

    #     ########### Conectar el PC con el módulo láser y borrar la cola
    #     inst = rm.open_resource('GPIB0::20::INSTR') 
    #     inst.read_termination = '\n'
    #     inst.write_termination = '\n'
    #     inst.write('*cls')

    #     ########## Parámetros del barrido
    #     wavelength_start=float(entry_var1.get())
    #     wavelength_finish= float(entry_var2.get())
    #     wavelength_step= float(entry_var4.get())*math.pow(10,-3)
    #     scan_speed= float(entry_var3.get())
    #     num_barrido=int(entry_var5.get())
    #     Unidades=entry_var6.get()


    #     avg_time = 0.1 # photodiode average time
    #     rangeMAX = 10 #dBm
    #     sensorAVG = 1 #miliseconds
    #     laserPOWER = 6 #dBm
    #     wavelength = np.arange(wavelength_start,wavelength_finish,wavelength_step) # nm Vector auxiliar que podemos utilizar o no
    #     ###########
    #     calcpoints = (float(wavelength_finish)-float(wavelength_start))/float(wavelength_step)
    #     exppoints = str(int(calcpoints))
    #     points = int(len(wavelength))
    #     estSweepTime =  int((float(wavelength_finish) - float(wavelength_start))/float(scan_speed))

    #     ######### Excepciones básicas
    #     if points>4000:
    #         print('Excede el número máximo de puntos. Bajar resolución.')
    #         return
    #     if 1520>wavelength_start or wavelength_finish>1630 or wavelength_finish<wavelength_start:
    #         print('Intervalo inválido. Ha de estar estrictamente contenido en 1520-1630 nm')
    #         return
        
    #     if contador_sesion == 0:
    #         Datos_3D = np.zeros(( 50, points, 2)) # Primer número es el número máximo de plots que puede almacenar a la vez
    #         # Segundo número los datos por plot (número de muestras)
    #         # Tercer número es fijo y es el número de columnas por plot

    #     ############################################### Lista de órdenes ################################################### 
        
    #     orden.append('SENS2:CHAN1:POW:UNIT 1')  # Unidades W
    #     orden.append('SOURCE1:CHAN1:POW 6DBM')  # 6dBm de potencia láser
    #     orden.append('SOURCE1:CHAN1:POW:STATE 1') # Encender el láser. Por si no está encendido
    #     orden.append('SOUR1:CHAN1:WAV '+str(wavelength_start)+'NM') # Fijar el láser en la longitud de onda de inicio del barrido
    #     orden.append('sour1:AM:stat OFF')  # Amplitude modulation apagada     
    #     orden.append('SOUR1:CHAN1:WAV:SWE:STAR '+str(wavelength_start)+'NM') # Parámetro del barrido: longitud de onda de inicio
    #     orden.append('SOUR1:CHAN1:WAV:SWE:STOP '+ str(wavelength_finish)+'NM') # Parámetro del barrido: longitud de onda de fin
    #     orden.append('SOUR1:CHAN1:WAV:SWE:SPE '+str(scan_speed)+'nm/s') # Parámetro del barrido: velocidad de barrido
    #     orden.append('SENS2:CHAN1:POW:ATIM 1ms') # Parámetro del barrido: tiempo de sampleo
    #     orden.append('SOUR1:CHAN1:WAV:SWE:CYCL 1') # Parámetro del barrido: Realizar solo un ciclo
    #     orden.append('TRIG1:CHAN1:OUTP STF') # Trigger en escucha
    #     orden.append('SOUR1:CHAN1:WAV:SWE:MODE CONT') # Parámetro del barrido: Continuo
    #     orden.append('init2:cont 1') 
    #     orden.append('sour1:wav:swe:llog 1') # Logging de la longitud de onda a la que se realiza cada trigger
    #     orden.append('SOUR1:CHAN1:WAV:SWE:STEP '+str(wavelength_step)+'nm') # Parámetro del barrido: Step 
    #     orden.append('SENS2:CHAN1:FUNC:PAR:LOGG '+str(points)+','+str(avg_time)+'ms') # Logging del sensor
    #     orden.append('TRIG2:CHAN1:INP SME') 
    #     orden.append('SENS2:CHAN1:FUNC:STAT STAB,START') # Empezar a recoger datos del sensor
    #     orden.append('SOUR1:CHAN1:WAV:SWE 1') # Tirar barrido

    #     #####################################################################################################################

    #     contador_int=0 #Contador interno de la funcion pero que se usa en el plot
       
    #     while OnOff==1: #Bucle que se mantienen mientras la variable OnOff sea true==1
        
    #         for i in orden: #Manda todas las órdenes al módulo 
    #             print(i)
    #             inst.write(i)
            
    #         time.sleep(estSweepTime+3) # Tiempo de espera en realizar el barrido más offset necesario.
    #         #root.after(estSweepTime*1000+3000)
    #         loggingStatus = "PROGRESS" # Función que comprueba que el láser sigue realizando el barrido
    #         while loggingStatus.endswith("PROGRESS"):
    #             loggingStatus = inst.query("SENS2:FUNC:STAT?").strip()
    #             print(loggingStatus)
    #             time.sleep(0.5)
    #             #root.after(500)
    #         # Cuando termina el barrido se le pregunta el resultado al módulo
    #         values=inst.query_binary_values('SENS2:CHAN1:FUNC:RES?') # Resultado del logging de potencias
    #         time.sleep(0.2)
    #         wavelengthreal=inst.query_binary_values('SOUR1:CHAN1:READ:DATA? LLOG',datatype='d') # resultado del logging de longitudes de onda

    #         inst.write('SENS2:CHAN1:FUNC:STAT STAB,STOP') #Parar el logging
    #         inst.write('TRIG2:CHAN1:INP IGN') # ignorar el trigger



    #         wavelengthreal=wavelengthreal[1:int(len(wavelength)+2)] # Adecuación de los resultados
    #         wavelengthreal=np.array(wavelengthreal) #Hay que sumarle 2 por las dimensiones, funciona

    #         dfexperimento = pd.DataFrame({"Longitud de onda(nm)" : wavelengthreal, "Potencia(W)" : values}) # Crear el Dataframe del experimento
    #         #10*np.log10(values)+30

    #         if entry_var7.get()=='Múltiples Barridos': #Comprobar si se han hecho los suficientes barridos
    #             if num_barrido==contador_int:
    #                 OnOff=0

    #         if entry_var7.get()=='Barrido Único': # Si el barrido es único
    #             OnOff=0

    #         contador_int=contador_int+1 #contador interno sube una unidad

    #         ####################################### Guardamos los datos ################################################
    #         #Guardamos el archivo con Resultados_ más el nombre que le queramos dar + un contador del total + terminación
    #         Archivo = 'Resultados_'+str(entry_var12.get())+ '_'+ str(contador_int) + '.dat' # El número será el número del experimento
    #         dfexperimento.to_csv(Archivo, index=False) # Se guarda en el archivo que queremos
    #         ########################   Matriz auxiliar con los plots. Guardamos la matriz auxiliar
    #         Datos = np.dstack((wavelengthreal,values))
    #         Datos_3D[:][:][contador_sesion]=Datos # Copiamos cada Datos en 3d por cada sesion
    #         #Plot=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
    #         #power=Plot[:,1] # Recuperar el array de power
    #         #wav=Plot[:,0] # Recuperar el array de wavelenght

    #         #if Contador == 0:
    #         #    new_row = {'Fecha':Fecha, 'contador':Contador}
    #         #    Log = Log.append(new_row, ignore_index=True)
    #         #Log.loc[Log.Fecha==Fecha, 'contador']= Contador
    #         #Log.to_csv('Log.txt', index=False)

            
    #         ################################################## Ploteamos ##########################################################
    #         Page3.PlotExp() # Llamamos al plot dentro de la string en la que estamos

    #         #Contador=Contador+1 #Contador global sube una unidad
    #         #Grabamos en el Log
    #         #f = open("Log.txt", "w")
    #         #f.write('%04d' % Contador)
    #         #f.close()
    #         contador_sesion=contador_sesion+1
    #         contador_int=contador_int+1
            
    #     inst.close #Cerrar el instrumento



    ######################################################### Recoger y guardar datos ##################################################
    def PlotExp():
        global Ajustes_finales_exp,Ajustes, Ajustes_resultados,t1,t2,p1,p2,DatosTemp
        cont_aux=0
        ## Función para el plot del Experimento que es algo distinto al anterior utilizado
        # Cogemos a los amigos de la fig2 y fig 3 para actualizarlos
        if contador_int>3: # Si hay más de tres muestras, sólo mostrar las últimas tres
            ax2.cla()
            for num in range(contador_sesion-2, contador_sesion+1):
                Aux=Datos_3D[:][:][num] # Esto es para recuperar los datos del plot
                power=Aux[:,1] # Recuperar el array de power
                wav=Aux[:,0] # Recuperar el array de wavelenght
                ax2.plot(wav,power)
        
        else:
            Aux=Datos_3D[:][:][contador_sesion] # Esto es para recuperar los datos del plot
            power=Aux[:,1] # Recuperar el array de power
            wav=Aux[:,0] # Recuperar el array de wavelenght
            ax2.plot(wav,power)

        ax2.set_ylabel('Power(dBm)')
        ax2.set_xlabel('Wavelength')
        canvas2.draw()

        ############### Ajustar y plotear ajuste
         
        list_nombres= Ajustes.index


        if contador_int==0:
            DatosTemp=[]
            p1=[0]*len(list_nombres)
            p2=[0]*len(list_nombres)
            for i in range(len(list_nombres)+1):
                DatosTemp.append([])

       
       
        
        for i in list_nombres:

            if i.startswith('Gaussian')==True:

                lim1=float(Ajustes['lim1'][i])
                lim2=float(Ajustes['lim2'][i])

                pos1=Page2.find_nearest(wav,lim1)
                pos2=Page2.find_nearest(wav,lim2)

                xpoints = wav[pos1:pos2]
                ypoints = power[pos1:pos2]

                p0= Ajustes_resultados.loc[i].tolist() # coordenadas iniciales
                popt, _=curve_fit(Page2.fun_Gauss, xpoints, ypoints, p0 )
                print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))

                # No siempre hay que plotearlos! CAMBIAR ESTO
                if str(entry_var11.get()) == i:
                    x1=np.linspace(lim1,lim2,300)
                    ax2.plot(x1 ,Page2.fun_Gauss(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, sigma=%5.3f' % tuple(popt))
                    canvas2.draw()

                if str(entry_var11.get()) == 'Todos':
                    x1=np.linspace(lim1,lim2,300)
                    ax2.plot(x1 ,Page2.fun_Gauss(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, alfa=%5.3f' % tuple(popt))
                    canvas2.draw()

                # Actualizar límites de integración y variables Refrescamos los resultados del ajuste y cambiamos los límites
                Ajustes['lim1'][i] = lim1 + (popt[2]-Ajustes_resultados['x0'][i])
                Ajustes['lim2'][i] = lim2 + (popt[2]-Ajustes_resultados['x0'][i])
                Ajustes_resultados.loc[i]=list(popt)

            else:

                lim1=float(Ajustes['lim1'][i])
                lim2=float(Ajustes['lim2'][i])

                pos1=Page2.find_nearest(wav,lim1)
                pos2=Page2.find_nearest(wav,lim2)

                xpoints = wav[pos1:pos2]
                ypoints = power[pos1:pos2]

                p0= Ajustes_resultados.loc[i].tolist() # coordenadas iniciales CAMBIAR ESTOO
                popt, _=curve_fit(Page2.fun_Lorentz, xpoints, ypoints, p0 )
                print('fit: H=%5.3f, A=%5.3f, x0=%5.3f, alfa=%5.3f' % tuple(popt))

                if str(entry_var11.get()) == i:
                    x1=np.linspace(lim1,lim2,300)
                    ax2.plot(x1 ,Page2.fun_Lorentz(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, alfa=%5.3f' % tuple(popt))
                    canvas2.draw()
                if str(entry_var11.get()) == 'Todos':
                    x1=np.linspace(lim1,lim2,300)
                    ax2.plot(x1 ,Page2.fun_Lorentz(x1,*popt), *popt, 'r-', label= 'fit: H=%5.3f, A=%5.3f, x0=%5.3f, alfa=%5.3f' % tuple(popt))
                    canvas2.draw()
                
                # Actualizar límites de integración y variables Refrescamos los resultados del ajuste y cambiamos los límites

                Ajustes['lim1'][i] = lim1 + (popt[2]-Ajustes_resultados['x0'][i]) # Actualziamos los límites del ajuste
                Ajustes['lim2'][i] = lim2 + (popt[2]-Ajustes_resultados['x0'][i]) # Actualziamos los límites del ajuste
                Ajustes_resultados.loc[i]=list(popt) # Actualizamos los resultados del ajuste para que sean utilizados en el siguiente ciclo

            #Ajustes_finales_exp=Ajustes_finales_exp
            list_aux=[lim1, lim2]+list(popt)
            Ajuste_final_aux = pd.DataFrame( [(list_aux)], columns=['lim1' ,'lim2','H','A','x0','sigma'], index=[i +'_' +str(contador_int)])

            try :
                Ajustes_finales_exp
                Ajustes_finales_exp=pd.concat([Ajustes_finales_exp, Ajuste_final_aux])
            except NameError: Ajustes_finales_exp = Ajuste_final_aux

            if contador_int==0:
                if cont_aux==0:
                    t1 = time.perf_counter()
                p1[cont_aux] = popt[2]
            
            else:
                p2[cont_aux]=popt[2]
                print(p2[cont_aux])
                print(p1[cont_aux])
                print(type(p2[cont_aux]))
                deltapos= float(p2[cont_aux])-float(p1[cont_aux])
                p1[cont_aux]=p2[cont_aux]
                DatosTemp[cont_aux].append(deltapos)
                
                if cont_aux==0:
                    t2 = time.perf_counter()
                    deltaTemp = t2-t1
                    DatosTemp[len(list_nombres)].append(deltaTemp)
                    t1=t2                
            cont_aux+=1
        


            print(Ajustes_finales_exp)

        #Para plotear querremos saber el incremento desde la posición inicial y el incremento en tiempo desde el tiempo inicial
        
        if contador_int>1:
            Datos_procesados=Page3.suma(DatosTemp)
            Tiempo = Datos_procesados[len(list_nombres)]
            Posicion = Datos_procesados[0]
            ax3.cla()
            ax3.plot(Tiempo,Posicion,'r.')
            ax3.set_ylabel('Incremento posicion')
            ax3.set_xlabel('Incremento temporal')
            ax3.set_xlim([Datos_procesados[len(list_nombres)][0],Datos_procesados[len(list_nombres)][-1]]) # HAY QUE SEGUIR CON ESTO
            canvas3.draw()  
 

    def suma(lista_aux): # Lo siento. Esta aberración es culpa de cómo python entiende las listas dentro de listas
        lista=[]
        for t in range(len(lista_aux)):
            lista.append(lista_aux[t][:])
        print(lista)
        for i in range(len(lista)):
            for j in range(len(lista[i])):
                if j==0:
                    print('nada')
                else:
                    lista[i][j]=lista[i][j]+lista[i][j-1]
        return lista

    def __init__(self, *args, **kwargs):

        global Seleccion12
        global ax2,ax3,fig2,fig3,canvas2,canvas3
        Page.__init__(self, *args, **kwargs)
    
        fig2,ax2= plt.subplots()
        fig3,ax3= plt.subplots()

        #Archivo= 'Resultados_'+str(contador)+'.csv'
        #df = pd.read_csv(Archivo, sep=",")
        #wavelength = df.to_numpy()[:,0]
        #potencia=np.log10(df.to_numpy()[:,1])*10+30

        canvas2 = FigureCanvasTkAgg(fig2, master=self)  # Generate canvas instance, Embedding fig in root
        canvas2.get_tk_widget().place(relx = 0.7, rely = 0.25, anchor = 'center', relwidth=0.6, relheight=0.5)
        canvas2.draw()

        canvas3 = FigureCanvasTkAgg(fig3, master=self)  # Generate canvas instance, Embedding fig in root
        canvas3.get_tk_widget().place(relx = 0.7, rely = 0.75, anchor = 'center', relwidth=0.6, relheight=0.5)
        canvas3.draw()

        toolbar2 = NavigationToolbar2Tk(canvas2, self)
        toolbar2.place(relx = 0.7, rely = 0.02, anchor = 'center')
        toolbar2.update()

        toolbar3 = NavigationToolbar2Tk(canvas3, self)
        toolbar3.place(relx = 0.7, rely = 0.52, anchor = 'center')
        toolbar3.update()    

        #ax2.plot(wavelength,potencia,'b')
        #ax2.set_ylabel('Power(dBm)')
        #ax2.set_xlabel('Wavelength')

        #ax3.plot(wavelength,potencia,'g')
        #ax3.set_ylabel('Power(dBm)')
        #ax3.set_xlabel('Wavelength')

        label_lambda_min=tk.Label(self,text='Longitud de onda inicial (nm)', font=('Helvetica',14), borderwidth=2, relief="groove")
        label_lambda_min.place(relx = 0.1, rely = 0.1, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_lambda_min=tk.Entry(self,textvariable=entry_var1,font=('Helvetica',14),state="readonly" )
        entry_lambda_min.place(relx = 0.225, rely = 0.1, anchor = 'center', relwidth=0.1, relheight=0.05)
    
        
        label_lambda_max=tk.Label(self,text='Longitud de onda final (nm)',font=('Helvetica',14),  borderwidth=2, relief="groove")
        label_lambda_max.place(relx = 0.1, rely = 0.15, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_lambda_max=tk.Entry(self,textvariable=entry_var2,font=('Helvetica',14),state="readonly")
        entry_lambda_max.place(relx = 0.225, rely = 0.15, anchor = 'center', relwidth=0.1, relheight=0.05)
  
        
        label_lambda_speed=tk.Label(self,text='Velocidad del barrido (nm/s)',font=('Helvetica',14), borderwidth=2, relief="groove")
        label_lambda_speed.place(relx = 0.1, rely = 0.2, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_lambda_speed=tk.Entry(self,textvariable=entry_var3,font=('Helvetica',14),state="readonly")
        entry_lambda_speed.place(relx = 0.225, rely = 0.2, anchor = 'center', relwidth=0.1, relheight=0.05)
  
 
        label_lambda_res=tk.Label(self,text='Resolución (pm)',font=('Helvetica',14), borderwidth=2, relief="groove")
        label_lambda_res.place(relx = 0.1, rely = 0.25, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_lambda_res=tk.Entry(self,textvariable=entry_var4,font=('Helvetica',14),state="readonly")
        entry_lambda_res.place(relx = 0.225, rely = 0.25, anchor = 'center', relwidth=0.1, relheight=0.05)
    
 
        label_lambda_num=tk.Label(self,text='Número de barridos. Opcional',font=('Helvetica',14), borderwidth=2, relief="groove")
        label_lambda_num.place(relx = 0.1, rely = 0.3, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_lambda_num=tk.Entry(self,textvariable=entry_var5,font=('Helvetica',14))
        entry_lambda_num.place(relx = 0.225, rely = 0.3, anchor = 'center', relwidth=0.1, relheight=0.05)

        label_Seleccion12=tk.Label(self,text='Mostrar en plot:',font=('Helvetica',14),  borderwidth=2, relief="groove")
        label_Seleccion12.place(relx = 0.1, rely = 0.35, anchor = 'center', relwidth=0.15, relheight=0.05)  
        choices12 = ['No hay ajustes']
        Seleccion12 = ttk.Combobox(self, values=choices12, state="readonly", textvariable=entry_var11, postcommand= Page3.Actualizar ,font=('Helvetica',14) )
        Seleccion12.place(relx = 0.225, rely = 0.35, anchor = 'center', relwidth=0.1, relheight=0.05)

        label_nombre=tk.Label(self,text='Nombre del archivo',font=('Helvetica',14),  borderwidth=2, relief="groove")
        label_nombre.place(relx = 0.1, rely = 0.4, anchor = 'center', relwidth=0.15, relheight=0.05)
        entry_nombre=tk.Entry(self,textvariable=entry_var12,font=('Helvetica',14))
        entry_nombre.place(relx = 0.225, rely = 0.4, anchor = 'center', relwidth=0.1, relheight=0.05)

        label_seleccion=tk.Label(self,text='Modo de barrido',font=('Helvetica',14),  borderwidth=2, relief="groove")
        label_seleccion.place(relx = 0.1, rely = 0.45, anchor = 'center', relwidth=0.15, relheight=0.05)
        choices1=['Barrido Único','Múltiples Barridos','Barrido Continuo. Stop manual']
        Seleccion1=ttk.Combobox(self, values=choices1, state="readonly",textvariable=entry_var7,font=('Helvetica',14) )
        Seleccion1.place(relx = 0.225, rely = 0.45, anchor = 'center', relwidth=0.1, relheight=0.05)
        Seleccion1.current(0)

        label_Exp=tk.Label(self,text='Comprobar las opciones elegidas antes de ejecutar el experimento',font=('Helvetica',14),  borderwidth=2, relief="solid")
        label_Exp.place(relx = 0.175, rely = 0.55, anchor = 'center', relwidth=0.30, relheight=0.05)
        
        #btn_showgraf=tk.Button(self, text='Stop', command=Page3.MostrarAjuste)
        #btn_showgraf.grid(row=6,column=2,columnspan=10,ipadx=20,ipady=15)

        btn_stop=tk.Button(self, text='Stop', command=Page2.Stop,font=('Helvetica',14),  borderwidth=4, relief="raise", bg='grey', fg='red')
        btn_stop.place(relx = 0.25, rely = 0.6, anchor = 'center', relwidth=0.15, relheight=0.05)

        btn_exp=tk.Button(self, text='Empezar Experimento', command=Page3.Experimento,font=('Helvetica',14),  borderwidth=4, relief="raised",bg='grey', fg='white')
        btn_exp.place(relx = 0.1, rely = 0.6, anchor = 'center', relwidth=0.15, relheight=0.05)

    def Actualizar():
        Seleccion12['values'] = lista_ajustes #Al tocar el desplegable se inicia esta funcion y lo actualiza

    #def MostrarAjuste():
    #    Ajuste = str(entry_var11.get())
    #    Ajustesloc



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


contador=0
global coords
coords=[]

def callback(event):

    global coords
    global Amplitud
    xevent=event.xdata
    print(xevent)
    coords.append(xevent)
    if len(coords)==2:
        fig.canvas.callbacks.disconnect(cid)
    #Archivo= 'Resultados_'+str(contador)+'.csv'

    #if len(coords)==3:
    #    df = pd.read_csv(Archivo, sep=",")
    #    wavelength = df.to_numpy()[:,0] + 3*contador
    #    #potencia=np.log10(df.to_numpy()[:,1])*10+30
    #    #Amplitud=Page2.find_nearest(potencia,coords[2])
    #    p1=Page2.find_nearest(wavelength,coords[0])
    #    p2=Page2.find_nearest(wavelength,coords[1])
    #    lim1=wavelength[p1]
    #    lim2=wavelength[p2]
    #    
    #    yevent=event.ydata
    #    Amplitud = yevent
    #    print( 'Illo esto es lo que sale en la y=%5.3f '% yevent)
    #    
    #    label1.config(text='lim1=%5.3f, lim2=%5.3f' % (lim1,lim2))
    #    fig.canvas.callbacks.disconnect(cid)


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
    entry_var11 = tk.StringVar()
    entry_var12= tk.StringVar()
    entry_var_lim1 = tk.StringVar()
    entry_var_lim2 = tk.StringVar()
    entry_var_Amplitud = tk.StringVar()
    
    main = MainView(root)
    main.pack(side="bottom", fill="both", expand=True)
    user32 = ctypes.windll.user32
    screenWidth =  user32.GetSystemMetrics(0)
    screenHeight = user32.GetSystemMetrics(1)
    root.wm_geometry("%dx%d" % (screenWidth, screenHeight))
    root.mainloop()
