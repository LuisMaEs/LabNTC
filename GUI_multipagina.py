import tkinter as tk
import time
# Ejemplo con páginas 

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()


class Page1(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        btn_on_off= tk.Button(self, text='State : Off', command=lambda widget="btn_on_off" : SwitchOnOff(btn_on_off) ,bg='red') 
        btn_on_off.pack(side="top", fill="both", expand=True)

        ELambda=tk.Entry(self,textvariable=entry_var)
        ELambda.pack(side="top", fill="both", expand=True)

        btn_set_lambda=tk.Button(self, text='Go to Lambda', command=GoToLambda )
        btn_set_lambda.pack(side="top", fill="both", expand=True)
 

class Page2(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       #label = tk.Label(self, text="This is page 2")
       #label.pack(side="top", fill="both", expand=True)

       label_lambda_min=tk.Label(self,text='Longitud de onda inicial (nm)')
       label_lambda_min.grid(row=0,column=0,ipadx=5,ipady=15)
       entry_lambda_min=tk.Entry(self,textvariable=entry_var1)
       entry_lambda_min.grid(row=0,column=1,ipadx=5,ipady=15)
       
       label_lambda_max=tk.Label(self,text='Longitud de onda final (nm)')
       label_lambda_max.grid(row=1,column=0,ipadx=5,ipady=15)
       entry_lambda_max=tk.Entry(self,textvariable=entry_var2,)
       entry_lambda_max.grid(row=1,column=1,ipadx=5,ipady=15)
       
       label_lambda_speed=tk.Label(self,text='Velocidad del barrido (nm/s)')
       label_lambda_speed.grid(row=2,column=0,ipadx=5,ipady=15)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var3)
       entry_lambda_speed.grid(row=2,column=1,ipadx=5,ipady=15)

       label_lambda_speed=tk.Label(self,text='Resolución (pm)')
       label_lambda_speed.grid(row=3,column=0,ipadx=5,ipady=15)
       entry_lambda_speed=tk.Entry(self,textvariable=entry_var4)
       entry_lambda_speed.grid(row=3,column=1,ipadx=5,ipady=15)
       

       btn_barrido_cont=tk.Button(self, text='Hacer barrido', command=BarridoContinuo)
       btn_barrido_cont.grid(row=4,column=0,columnspan=5,ipadx=5,ipady=15)





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

if __name__ == "__main__":


    def GoToLambda():
        if bool(entry_var.get())==1:
            if  1520<float(entry_var.get())<1630:
                mensaje='SOURCE1:CHAN1:WAVE ' + entry_var.get() + 'NM'
                print(mensaje)

            else:
                print('Longitud de onda fuera de rango. Rango válido de 1521 nm a 1629 nm. \n')

    Power=0
    def SwitchOnOff(button):
        global Power

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
    
    def BarridoContinuo():
        orden=[]
        if  1520<float(entry_var1.get())<1630 and 1520<float(entry_var2.get())<1630 and float(entry_var1.get())<float(entry_var2.get()):
            orden.append('SOURCE1:CHAN1:WAV:SWE:MODE CON')
            orden.append('SOURCE1:CHAN1:WAV:SWE:STAR ' + entry_var1.get() + 'NM')
            orden.append('SOURCE1:CHAN1:WAV:SWE:STOP ' + entry_var2.get() + 'NM')
            orden.append('SOURCE1:CHAN1:WAV:SWE:SPE ' + entry_var3.get() + 'nm/s')
            for i in orden: 
                print(i)
            print('SOURCE1:CHAN1:WAV:SWE STAR')


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

    