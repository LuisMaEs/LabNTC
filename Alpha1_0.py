import tkinter as tk
import pyvisa 
from tkinter.constants import DISABLED, NORMAL
import time # Necesario para usar delays.
import numpy as np
import math 
import matplotlib.pyplot as plt
import pandas as pd


rm = pyvisa.ResourceManager() # Creamos el objeto Resource Manager
print(rm.list_resources()) # Imprimimos la lista de recursos: se entiende recursos por instrumentos conectados al pc.

      
class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()


class Page1(Page):

    def GoToLambda():
        if bool(entry_var.get())==1:
            if  1520<float(entry_var.get())<1630:
                inst = rm.open_resource('GPIB0::20::INSTR') 
                inst.read_termination = '\n'
                inst.write_termination = '\n'
                mensaje='SOURCE1:CHAN1:WAVE ' +entry_var.get()+ 'NM'
                inst.write(mensaje)
                inst.close()
            else:
                print('Longitud de onda fuera de rango. Rango válido de 1521 nm a 1629 nm. \n')
    global Power  
    Power=0


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
        root.after(1000)  
 
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        btn_on_off= tk.Button(self, text='State : Off',command=lambda widget="btn_on_off" : Page1.SwitchOnOff(btn_on_off) ,bg='red') 
        btn_on_off.pack(side="top", fill="both", expand=True)

        ELambda=tk.Entry(self,textvariable=entry_var)
        ELambda.pack(side="top", fill="both", expand=True)

        btn_set_lambda=tk.Button(self, text='Go to Lambda', command=Page1.GoToLambda )
        btn_set_lambda.pack(side="top", fill="both", expand=True)
 

class Page2(Page):

    def BarridoContinuo():
        orden=[]
       
        inst = rm.open_resource('GPIB0::20::INSTR')
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.write('*cls')
        wavelength_start=float(entry_var1.get())
        wavelength_finish= float(entry_var2.get())
        wavelength_step= float(entry_var4.get())*math.pow(10,-3)
        scan_speed= float(entry_var3.get())


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

        if  1520<float(entry_var1.get())<1630 and 1520<float(entry_var2.get())<1630 and float(entry_var1.get())<float(entry_var2.get()):
            orden.append('*cls')
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
            
            for i in orden: 
                inst.write(i)

            root.after(estSweepTime*1500)
            loggingStatus = "PROGRESS"
            while loggingStatus.endswith("PROGRESS"):
                loggingStatus = inst.query("SENS2:FUNC:STAT?").strip()
                print(loggingStatus)
                root.after(500)
            print('Tamos bien')
            values=inst.query_binary_values('SENS2:CHAN1:FUNC:RES?')
            print('Tamos mejor')
            wavelengthreal=inst.query_binary_values('SOUR1:CHAN1:READ:DATA? LLOG',datatype='d') 
            print('Tamos mejor')
            #np.savetxt('lab2.out', values, delimiter=',') 
            print('Tamos peor')
            #print('Por qué?')
            inst.write('SENS2:CHAN1:FUNC:STAT STAB,STOP')
            print('Tamos no sé')
            inst.write('TRIG2:CHAN1:INP IGN')
            inst.close()
            wavelengthreal=wavelengthreal[1:int(len(wavelength)+2)] #No entiendo el porqué, pero funciona
            df = pd.DataFrame({"Longitud de onda(nm)" : wavelengthreal, "Potencia(W)" : values})
            print('Tamos no sé')
            df.to_csv("Resultados.csv", index=False)
            potencia = df.to_numpy()[:,1]
            plt.plot(wavelengthreal, 10*np.log10(potencia))
            plt.ylabel('Power(dBm)')
            plt.xlabel('Wavelength(nm)')
            plt.show()

    def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       #label = tk.Label(self, text="This is page 2")
       #label.pack(side="top", fill="both", expand=True)

       label_lambda_min=tk.Label(self,text='Longitud de onda inicial')
       label_lambda_min.grid(row=0,column=0,ipadx=5,ipady=15)
       entry_lambda_min=tk.Entry(self,textvariable=entry_var1)
       entry_lambda_min.grid(row=0,column=1,ipadx=5,ipady=15)
       
       label_lambda_max=tk.Label(self,text='Longitud de onda final')
       label_lambda_max.grid(row=1,column=0,ipadx=5,ipady=15)
       entry_lambda_max=tk.Entry(self,textvariable=entry_var2,)
       entry_lambda_max.grid(row=1,column=1,ipadx=5,ipady=15)
       
       label_lambda_speed=tk.Label(self,text='Velocidad del barrido')
       label_lambda_speed.grid(row=2,column=0,ipadx=5,ipady=15)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var3)
       entry_lambda_speed.grid(row=2,column=1,ipadx=5,ipady=15)
       
       label_lambda_speed=tk.Label(self,text='Resolución (pm)')
       label_lambda_speed.grid(row=3,column=0,ipadx=5,ipady=15)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var4)
       entry_lambda_speed.grid(row=3,column=1,ipadx=5,ipady=15)

       btn_barrido_cont=tk.Button(self, text='Hacer barrido', command=Page2.BarridoContinuo)
       btn_barrido_cont.grid(row=4,column=0,columnspan=3,ipadx=5,ipady=15)





class Page3(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       label = tk.Label(self, text="This is page 3")
       label.pack(side="top", fill="both", expand=True)



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



#MainLoop
if __name__ == "__main__":
    root = tk.Tk()
    entry_var = tk.StringVar()
    entry_var1 = tk.StringVar()
    entry_var2 = tk.StringVar()
    entry_var3 = tk.StringVar()
    entry_var4 = tk.StringVar()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("400x400")
    root.mainloop()

    