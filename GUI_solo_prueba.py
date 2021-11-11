import tkinter as tk
from tkinter.constants import DISABLED, NORMAL
import time # Necesario para usar delays.



Power=0
def SwitchOnOff():
    global Power

    if Power==0:
        
        mensaje='SOURCE1:CHAN1:POW:STATE 1'
        print(mensaje)
        btn_on_off.config(bg='green')
        btn_on_off.config(text='State : On')
        Power=1
        
    else:
        
        mensaje='SOURCE1:CHAN1:POW:STATE 0'
        print(mensaje)
        btn_on_off.config(bg='red')
        btn_on_off.config(text='State : Off')
        Power=0
     
    time.sleep(2)



      

#btn_on_off['state'] = NORMAL
    

def GoToLambda():
    
    if bool(entry_var.get())==1:
        if  1520<float(entry_var.get())<1630:
            mensaje='SOURCE1:CHAN1:WAVE ' + entry_var.get() + 'NM'
            print(mensaje)

        else:
            print('Longitud de onda fuera de rango. Rango válido de 1521 nm a 1629 nm. \n')
    



window= tk.Tk()
window.title('Laboratorio Biosensado')
window.geometry('600x400')
entry_var = tk.StringVar()
ELambda=tk.Entry(window,textvariable=entry_var)
ELambda.grid(column=0,row=1)
#Algunas variables utilizadas



btn_on_off= tk.Button(window, text='State : Off',command=SwitchOnOff,bg='red') 

btn_on_off.grid(column=2, row=2)
btn_set_lambda=tk.Button(window, text='Go to Lambda', command=GoToLambda)
btn_set_lambda.grid(column=1, row=1)




window.mainloop()