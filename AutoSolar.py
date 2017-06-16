import sys

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

import AutoSolar_support
import random
import time
import matplotlib
from BateriasObserver import *
from ControladorObserver import *
from MotorObserver import *
from mpptObservable import *
from gpsObservable import *
from botonesObservable import *

matplotlib.use('TkAgg')

from tkinter import filedialog
from matplotlib import *
import numpy as np
from math import sqrt
from numpy import arange, sin, pi, cos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = Telemetria_Auto_Escolta (root)
    AutoSolar_support.init(root, top)
    root.mainloop()

w = None
def create_Telemetria_Auto_Escolta(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = Telemetria_Auto_Escolta (w)
    AutoSolar_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Telemetria_Auto_Escolta():
    global w
    w.destroy()
    w = None



def Tabla(Frame,rows,columns):
    Frame._widgets = []
    for row in range(rows):
        current_row = []
        for column in range(columns):
            if(column == 0 and row != 0):
                label = Label(Frame, text="CMU %s" % (row), borderwidth=0, width=10)
            else:
                if(row == 0 and column == 0):
                    label = Label(Frame, text="--", borderwidth=0, width=10)
                else:
                    label = Label(Frame, text="%s/%s" % (row, column), borderwidth=0, width=10)
            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
            current_row.append(label)
        Frame._widgets.append(current_row)

    for column in range(columns):
        Frame.grid_columnconfigure(column, weight=1)

def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)
        if (type(value) == int):
            if((float(value)/1000.0) < 2.5):
                widget.configure(background="red")
            if((float(value)/1000.0) > 4.0):
                widget.configure(background="#0998ee")
            if((float(value)/1000.0) < 0.0):
                widget.configure(background="yellow")
            if((float(value)/1000.0) <= 4.0 and float(value)>= 2.5):
                widget.configure(background="white")


def setter(this,valor):
    this.configure(text=valor)

def setterBar(this,valor):
    this.configure(value=valor)

def setterControlador(this,valor):
    if(valor == 0):
        this.configure(foreground="#000000")
    if(valor == 1):
        this.configure(foreground="#7c7c7c")


def open_file(name):
        datos = open(name)
        datos.readline()
        dato = datos.readline().strip()
        dato = tsplit(dato,",;")
        gps = np.array([[float(dato[2]), float(dato[3]), float(dato[4]), float(dato[5])]])

        for linea in datos.readlines():
            dato = linea.strip()
            dato = tsplit(dato,",;")
            gps = np.append(gps, [[float(dato[2]), float(dato[3]), float(dato[4]), float(dato[5])]], axis=0) #LAT,LONG,ALT,DIST
        datos.close()
        return dato,gps

def tsplit(s, sep):
    stack = [s]
    for char in sep:
        pieces = []
        for substr in stack:
            pieces.extend(substr.split(char))
        stack = pieces
    return stack

def abrir(f,a,p,error,posicion,canvas):
    archivo=filedialog.askopenfilename()
    if(archivo == ''):
        return 0,0
    datos = open(archivo,"r")
    datos.readline()
    dato = datos.readline().strip()
    dato = tsplit(dato,",;")
    gps = np.array([[float(dato[2]), float(dato[3]), float(dato[4]), float(dato[5])]])

    for linea in datos.readlines():
        dato = linea.strip()
        dato = tsplit(linea,",;")
        gps = np.append(gps, [[float(dato[2]), float(dato[3]), float(dato[4]), float(dato[5])]], axis=0) #LAT,LONG,ALT,DIST
    datos.close()

    #se crea la figura con un color de fondo
    f = plt.figure(figsize=(5, 4), dpi=100, facecolor = (0.9294,0.9137,0.8667))
    a = f.add_subplot(111)

    #se grafica la ruta y los marker del gps
    #x = np.arange(len(gps[:,2]))
    plt.plot(gps[:,3], gps[:,2], color=(0, 0.7, 0.2))
    plt.fill_between(gps[:,3], gps[:,2], np.min(gps[:,2]),color=(0.5,0,0,0.5))
    #marcar gps
    p = gpsVsPosiciones(gps, gps[0][0], gps[0][1])

    error = plt.plot(gps[p][3], gps[p][2], marker='o', color=(0.1647,0.4157,1, 0.5), markersize=20)
    posicion = plt.plot(gps[p][3], gps[p][2], marker='o', color=(0.1647,0.4157,1), markersize=6)

    a.grid(True) #crear grid
    a.set_title('Grafico de Perfil')

    # a tk.DrawingArea para el 1er Grafico de latitud VS altitud
    canvas.show()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
    #canvas.configure(width=760)


    return dato,gps


def gpsVsPosiciones(gps, latitud, longitud):
    posicion = 0
    distancia = sqrt((gps[0][0] - latitud)**2 + (gps[0][1] - longitud)**2)
    cont = 0
    for p in gps:
        distancia2 = sqrt(((p[0] - latitud)**2) + ((p[1] - longitud)**2))
        if(distancia > distancia2):
            posicion = cont
            distancia = distancia2
        cont+=1
    return posicion

class Telemetria_Auto_Escolta:

    #TODO DENTRO DE CLOCK SE REALIZA UNA Y OTRA VEZ
    def clock(self,ind =0):

        ##########################################################
        ##############Obteniendo Cambios Observados###############
        ##########################################################

        #Obteniedo variables del observer del motor solo si hay algún cambio
        if self.motObserver.updated:
            motor = self.motObserver.getMotor()
            #errores = int(motor.errores)
            setter(self.Errores,repr(motor.getErrorMSG()))
            setter(self.Flags,repr(motor.getFlagsMSG()))
            #flag = int(motor.flags)
            self.motorActivo= motor.motorActivo
            self.mcurrent = motor.current
            self.mvoltage = motor.voltage
            self.mvelocidad = motor.velocidad
            self.mRPM = motor.RPM
            self.mphaseC = motor.phaseC
            self.mphaseB = motor.phaseB
            self.mvoltage_1= motor.voltage_1
            self.mvoltage_2= motor.voltage_2
            self.mvoltage_3= motor.voltage_3
            self.mvoltage_4= motor.voltage_4
            self.mTmotor= motor.t_motor
            self.mTDSP= motor.t_DSP
            self.mOdo= motor.odometro
            self.mAH= motor.ah

            self.motObserver.updated=False
        else:
            setter(self.Errores,'No hay errores')
            setter(self.Flags,'No hay errores')


        #Obteniedo variables del observer de las baterias solo si hay algún cambio
        if self.batObserver.updated:
            bateria = self.batObserver.getBattery()
            self.bCB1 = bateria.CB1 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bCB2 = bateria.CB2 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bCB3 = bateria.CB3 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bCB4 = bateria.CB4 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bCB5 = bateria.CB5 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bCB6 = bateria.CB6 #{'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
            self.bSOCah = bateria._SOC_ah #0.0
            self.bSOCp = bateria._SOC_p #0.0

            self.bminVolt = bateria.minVolt #{ 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
            self.bmaxVolt = bateria.maxVolt #{ 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
            self.bminTemp = bateria.minTemp #{ 'mT': 0.0, 'CMUNumber':0}
            self.bmaxTemp = bateria.maxTemp #{ 'mT': 0.0, 'CMUNumber':0}
            self.batObserver.updated=False


        #Obteniedo variables del observer de los controladores solo si hay algún cambio
        if self.drvObserver.updated:
            driver = self.drvObserver.getDriver()
            self.creverse = driver.reverse # False
            self.cneutral = driver.neutral # False
            self.cregen = driver.regen #False
            self.cdrive = driver.drive #False
            self.caccesories = driver.accesories#False
            self.crun = driver.run #False
            self.cstart = driver.start #False
            self.cbrakes = driver.brakes #False
            self.cfueldoor = driver.fueldoor#False
            self.cspCurrent = driver.spCurrent#0.0
            self.cspBusCurrent = driver.spBusCurrent# 0.0
            self.cspVelocity = driver.spVelocity#0.0 
            self.drvObserver.updated=False

        #Obteniedo variables del observer de los mppts solo si hay algún cambio
        if self.mpptObserver.updated:
            mpptss = self.mpptObserver.mppt()
            self.mVin       = mpptss.Vin       # 0.0
            self.mIin       = mpptss.Iin       # 0.0
            self.mVout      = mpptss.Vout      # 0.0
            self.mbulr      = mpptss.bulr      # 0.0
            self.mout       = mpptss.out       # 0.0
            self.mnoe       = mpptss.noe       # 0.0
            self.mundv      = mpptss.undv      # 0.0
            self.mt         = mpptss.t         # 0.0
            #estructura extra
            self.mt1        = mpptss.t1        # 0.0
            self.mt2        = mpptss.t2        # 0.0
            self.mcorriente = mpptss.corriente # 0.0
            self.mpptObserver.updated=False

        #Obteniedo variables del observer del GPS solo si hay algún cambio
        if self.gpsObserver.updated:
            gpss = self.gpsObserver.gps()
            #estructura gps
            self.glat        = gpss.lat        #0.0 #latitud:float
            self.glon        = gpss.lon        #0.0 #longitud:float
            self.galt        = gpss.alt        #0.0 #altitud:float
            self.gerr        = gpss.err        #0 #error[metros]:int
            self.glastUpdate = gpss.lastUpdate #datetime.fromtimestamp(0.0)#ultima vez actualizado:datetime
            self.gheading    = gpss.heading    #0.0 #grados de inclinacion respecto de la direccion[grados]:float
            self.gpsObserver.updated=False

        #Obteniedo variables del observer de los Botones solo si hay algún cambio
        if self.botObserver.updated:
            botones = self.botObserver.botones()
            #estructura principal
            self.bmppt      = botones.mppt      # False#int 32 //flag
            self.bpan1      = botones.pan1      # False
            self.bpan2      = botones.pan2      # False
            self.bpan3      = botones.pan3      # False
            self.blucesAl   = botones.lucesAl   # False# int 32 //flag
            self.blucesBa   = botones.lucesBa   # False
            self.blucesEm   = botones.lucesEm   # False
            self.bfan       = botones.fan       # 0#int 32 //[0-255]
            self.bbateria   = botones.bateria   # False# int 32 //flag
            self.botObserver.updated=False

        ################################################
        ##############Cambios en el GPS#################
        ################################################

        ##TODO: CAMBIAR POR LO QUE REALMENTE HACE EL GPS <-----
        #if(self.inicia == len(self.gps)-1):
        #    self.inicia = -1

        #self.inicia = self.inicia+1
        #self.p = self.gps[self.inicia] #LAT,LONG,ALT,DIST
        #print(self.p)
        self.p = [self.glat,self.glon,self.galt]
        po = gpsVsPosiciones(self.gps, self.glat, self.glon)
        self.error[0].set_data(self.gps[po][3],self.gps[po][2]) #actualizar valores
        self.posicion[0].set_data(self.gps[po][3], self.gps[po][2])
        self.f.canvas.draw()

        #self.p1 = self.gps[self.inicia]
        self.error2[0].set_data(self.gps[po][1],self.gps[po][0]) #actualizar valores
        self.posicion2[0].set_data(self.gps[po][1], self.gps[po][0])
        self.fun.canvas.draw()


        print("what?")
        
        #RADOMIZADOR INICIAL
        that = random.randint(0, 100) 
        that0 =random.randint(0, 100) 
        that1 =random.randint(0, 100) 
        that2 =random.randint(0, 100) 
        that3 =random.randint(1, 8) 
        
        
        ################################################
        ##############INFORMACION GENERAL###############
        ################################################
                
        # VELOCIDAD (Km/hr)
        setter(self.velocidad,'%.f'%(self.mvelocidad*3.6)+' Km/hr')
        
        # REVOLUCIONES POR MINUTO
        setter(self.RPM,'%.f'%(self.mRPM)+' RPM')

        # POTENCIA
        setter(self.POTENCIA,str(self.mvoltage*self.mcurrent)+' W')

        # Barra y Porcentaje de Velocidad
        setter(self.SetVelocityPorcentaje,str(round(int(self.cspVelocity))))
        setterBar(self.BarraProgresoSetVelocity,abs(self.cspVelocity/60))

        # Barra y Porcentaje Current
        setter(self.SetCurrentPorcentaje,'%.f'%(self.cspCurrent*100)+'%')
        setterBar(self.BarraProgresoSetCurrent,self.cspCurrent*100)
                
        # Barra y Porcentaje Bus
        setter(self.SetBusPorcentaje,'%.f'%(self.cspBusCurrent*100)+'%')
        setterBar(self.BarraProgresoSetBus,self.cspBusCurrent*100)

        # Ah, Barra y Porcentaje SOC ah / %
        setter(self.SocAh,'%.2f'%(self.bSOCah))
        setter(self.SocPorcentaje,str(self.bSOCp*100)+'%')
        setterBar(self.BarraProgresoSoc,self.bSOCp*100)
            
        #Errores y Flags
        #setter(self.Errores,'DC Bus over voltage ')
        #setter(self.Flags,'Motor Current')

        # Bus current (A)
        setter(self.BusCurrent,'%.2f'%(self.mcurrent))

        # Bus voltaje (V)
        setter(self.BusVoltaje,'%.2f'%(self.mvoltage))

        # Temperatura Motor (C)
        setter(self.TemperaturaMotor,'%.2f'%(self.mTmotor))

        # Temperatura DSP (C)
        setter(self.TemperaturaDSP,'%.2f'%(self.mTDSP))

        # Temperatura MIN y MAX de CMU
        setter(self.TemperaturaMIN,'%.2f'%(self.bminTemp['mT']))
        setter(self.TemperaturaMAX,'%.2f'%(self.bmaxTemp['mT']))
        setter(self.CMUtempMIN,str(self.bminTemp['CMUNumber']))
        setter(self.CMUtempMAX,str(self.bmaxTemp['CMUNumber']))

        # Voltaje MIN y MAX de CMU
        setter(self.VoltajeMIN,'%.2f'%(self.bminVolt['mV']/1000.0))
        setter(self.VoltajeMAX,'%.2f'%(self.bmaxVolt['mV']/1000.0))
        setter(self.CMUvoltMIN,str(self.bminVolt['CMUNumber']))
        setter(self.CMUvoltMAX,str(self.bmaxVolt['CMUNumber']))
 

        ## Estado Controlador
        setterControlador(self.ReverseLabel,not self.creverse)
        setterControlador(self.NeutralLabel,not self.cneutral)
        setterControlador(self.RegenLabel,not self.cregen)
        setterControlador(self.DriveLabel,not self.cdrive)
        setterControlador(self.AccesoriesLabel,not self.caccesories)
        setterControlador(self.RunLabel,not self.crun)
        setterControlador(self.StartLabel,not self.cstart)
        setterControlador(self.BrakesLabel,not self.cbrakes)
        setterControlador(self.FuelDoorLabel,not self.cfueldoor)


        ################################################
        ####################BATERIAS####################
        ################################################

        ##TABLA BATERÍA
        set(self.LabelframeBateria,1,1, self.bCB1['SN'])
        set(self.LabelframeBateria,1,2, self.bCB1['t_PCB'])
        set(self.LabelframeBateria,1,3, self.bCB1['t_Cell'])
        set(self.LabelframeBateria,1,4, self.bCB1['v_Cells'][0])
        set(self.LabelframeBateria,1,5, self.bCB1['v_Cells'][1])
        set(self.LabelframeBateria,1,6, self.bCB1['v_Cells'][2])
        set(self.LabelframeBateria,1,7, self.bCB1['v_Cells'][3])
        set(self.LabelframeBateria,1,8, self.bCB1['v_Cells'][4])
        set(self.LabelframeBateria,1,9, self.bCB1['v_Cells'][5])
        set(self.LabelframeBateria,1,10, self.bCB1['v_Cells'][6])
        set(self.LabelframeBateria,1,11, self.bCB1['v_Cells'][7])

        set(self.LabelframeBateria,2,1, self.bCB2['SN'])
        set(self.LabelframeBateria,2,2, self.bCB2['t_PCB'])
        set(self.LabelframeBateria,2,3, self.bCB2['t_Cell'])
        set(self.LabelframeBateria,2,4, self.bCB2['v_Cells'][0])
        set(self.LabelframeBateria,2,5, self.bCB2['v_Cells'][1])
        set(self.LabelframeBateria,2,6, self.bCB2['v_Cells'][2])
        set(self.LabelframeBateria,2,7, self.bCB2['v_Cells'][3])
        set(self.LabelframeBateria,2,8, self.bCB2['v_Cells'][4])
        set(self.LabelframeBateria,2,9, self.bCB2['v_Cells'][5])
        set(self.LabelframeBateria,2,10, self.bCB2['v_Cells'][6])
        set(self.LabelframeBateria,2,11, self.bCB2['v_Cells'][7])

        set(self.LabelframeBateria,3,1, self.bCB3['SN'])
        set(self.LabelframeBateria,3,2, self.bCB3['t_PCB'])
        set(self.LabelframeBateria,3,3, self.bCB3['t_Cell'])
        set(self.LabelframeBateria,3,4, self.bCB3['v_Cells'][0])
        set(self.LabelframeBateria,3,5, self.bCB3['v_Cells'][1])
        set(self.LabelframeBateria,3,6, self.bCB3['v_Cells'][2])
        set(self.LabelframeBateria,3,7, self.bCB3['v_Cells'][3])
        set(self.LabelframeBateria,3,8, self.bCB3['v_Cells'][4])
        set(self.LabelframeBateria,3,9, self.bCB3['v_Cells'][5])
        set(self.LabelframeBateria,3,10, self.bCB3['v_Cells'][6])
        set(self.LabelframeBateria,3,11, self.bCB3['v_Cells'][7])

        set(self.LabelframeBateria,4,1, self.bCB4['SN'])
        set(self.LabelframeBateria,4,2, self.bCB4['t_PCB'])
        set(self.LabelframeBateria,4,3, self.bCB4['t_Cell'])
        set(self.LabelframeBateria,4,4, self.bCB4['v_Cells'][0])
        set(self.LabelframeBateria,4,5, self.bCB4['v_Cells'][1])
        set(self.LabelframeBateria,4,6, self.bCB4['v_Cells'][2])
        set(self.LabelframeBateria,4,7, self.bCB4['v_Cells'][3])
        set(self.LabelframeBateria,4,8, self.bCB4['v_Cells'][4])
        set(self.LabelframeBateria,4,9, self.bCB4['v_Cells'][5])
        set(self.LabelframeBateria,4,10, self.bCB4['v_Cells'][6])
        set(self.LabelframeBateria,4,11, self.bCB4['v_Cells'][7])

        set(self.LabelframeBateria,5,1, self.bCB5['SN'])
        set(self.LabelframeBateria,5,2, self.bCB5['t_PCB'])
        set(self.LabelframeBateria,5,3, self.bCB5['t_Cell'])
        set(self.LabelframeBateria,5,4, self.bCB5['v_Cells'][0])
        set(self.LabelframeBateria,5,5, self.bCB5['v_Cells'][1])
        set(self.LabelframeBateria,5,6, self.bCB5['v_Cells'][2])
        set(self.LabelframeBateria,5,7, self.bCB5['v_Cells'][3])
        set(self.LabelframeBateria,5,8, self.bCB5['v_Cells'][4])
        set(self.LabelframeBateria,5,9, self.bCB5['v_Cells'][5])
        set(self.LabelframeBateria,5,10, self.bCB5['v_Cells'][6])
        set(self.LabelframeBateria,5,11, self.bCB5['v_Cells'][7])

        set(self.LabelframeBateria,6,1, self.bCB6['SN'])
        set(self.LabelframeBateria,6,2, self.bCB6['t_PCB'])
        set(self.LabelframeBateria,6,3, self.bCB6['t_Cell'])
        set(self.LabelframeBateria,6,4, self.bCB6['v_Cells'][0])
        set(self.LabelframeBateria,6,5, self.bCB6['v_Cells'][1])
        set(self.LabelframeBateria,6,6, self.bCB6['v_Cells'][2])
        set(self.LabelframeBateria,6,7, self.bCB6['v_Cells'][3])
        set(self.LabelframeBateria,6,8, self.bCB6['v_Cells'][4])
        set(self.LabelframeBateria,6,9, self.bCB6['v_Cells'][5])
        set(self.LabelframeBateria,6,10, self.bCB6['v_Cells'][6])
        set(self.LabelframeBateria,6,11, self.bCB6['v_Cells'][7])

        set(self.LabelframeBateria,7,1, 0)
        set(self.LabelframeBateria,7,2, 0)
        set(self.LabelframeBateria,7,3, 0)
        set(self.LabelframeBateria,7,4, 0)
        set(self.LabelframeBateria,7,5, 0)
        set(self.LabelframeBateria,7,6, 0)
        set(self.LabelframeBateria,7,7, 0)
        set(self.LabelframeBateria,7,8, 0)
        set(self.LabelframeBateria,7,9, 0)
        set(self.LabelframeBateria,7,10, 0)
        set(self.LabelframeBateria,7,11, 0)

        set(self.LabelframeBateria,8,1, 0)
        set(self.LabelframeBateria,8,2, 0)
        set(self.LabelframeBateria,8,3, 0)
        set(self.LabelframeBateria,8,4, 0)
        set(self.LabelframeBateria,8,5, 0)
        set(self.LabelframeBateria,8,6, 0)
        set(self.LabelframeBateria,8,7, 0)
        set(self.LabelframeBateria,8,8, 0)
        set(self.LabelframeBateria,8,9, 0)
        set(self.LabelframeBateria,8,10, 0)
        set(self.LabelframeBateria,8,11, 0)


        ################################################
        ####################PANELES#####################
        ################################################
        
        #
        #    self.mVin       = mpptss.Vin       # 0.0
        #    self.mIin       = mpptss.Iin       # 0.0
        #    self.mVout      = mpptss.Vout      # 0.0
        #    self.mbulr      = mpptss.bulr      # 0.0
        #    self.mout       = mpptss.out       # 0.0
        #    self.mnoe       = mpptss.noe       # 0.0
        #    self.mundv      = mpptss.undv      # 0.0
        #    self.mt         = mpptss.t         # 0.0
        #    #estructura extra
        #    self.mt1        = mpptss.t1        # 0.0
        #    self.mt2        = mpptss.t2        # 0.0
        #    self.mcorriente = mpptss.corriente # 0.0

        self.background_label0.config(text=time.asctime())
        ind += 1
        if(ind ==4):
            ind =0
        frame = self.frames[ind]
        frame2 = self.frames[(ind+2)%4]
        frame3 = self.frames[(ind+1)%4]
        
        self.background_label0.configure(image=frame)
        self.background_label1.configure(image=frame2)
        self.background_label.configure(image=frame3)
        
        #Bateria1
        setter(self.VoltajeBateria1,str(that))
        setter(self.CorrienteBateria1,str(that0))
        setter(self.PotenciaBateria1,str(that1))
        #Bateria2
        setter(self.VoltajeBateria2,str(that2))
        setter(self.CorrienteBateria2,str(that3))
        setter(self.PotenciaBateria2,str(that0))
        #Bateria3
        setter(self.VoltajeBateria3,str(that3))
        setter(self.CorrienteBateria3,str(that0))
        setter(self.PotenciaBateria3,str(that1))
        
        #PotenciaTotal
        setter(self.PotenciaTotal,str(that*100))
        #ErroresBaterias
        setter(self.ErrorPanel1,str('No hay errores'))
        setter(self.ErrorPanel2,str('No hay errores'))
        setter(self.ErrorPanel3,str('No hay errores'))


        ################################################
        ####################EXTRAAS#####################
        ################################################

        #Sensores
        setter(self.SensorCorriente,'%.2f'%(self.mcorriente))
        setter(self.SensorTemperatura1,'%.2f'%(self.mt1))
        setter(self.SensorTemperatura2,'%.2f'%(self.mt2))

        # RMS C y B
        setter(self.C0,'%.2f'%(self.mphaseC))
        setter(self.B0,'%.2f'%(self.mphaseB))

        # Voltajes 1.5 / 3.3 / 1.9
        setter(self.V150,'%.2f'%(self.mvoltage_1))#TODO Revisar voltaje real.
        setter(self.V330,'%.2f'%(self.mvoltage_3))
        setter(self.V190,'%.2f'%(self.mvoltage_4))

        # ODOMETRO Km y Bus Ah
        setter(self.OdometroKM0,'%.2f'%(self.mOdo))
        setter(self.OdometroAh0,'%.2f'%(self.mAH))

        # Estado Botons Pantalas
        setterControlador(self.BateriaLabel,not self.bbateria)
        setterControlador(self.mpptLabel,not  self.bmppt)
        setterControlador(self.mppt1Label,not self.bpan1)
        setterControlador(self.mppt2Label,not self.bpan2)
        setterControlador(self.mppt3Label,not self.bpan3)
        setterControlador(self.LucesAltasLabel,not self.blucesAl)
        setterControlador(self.LucesBajasLabel,not self.blucesBa)
        setterControlador(self.LucesEmergenciaLabel,not self.blucesEm)
        if (self.bfan >= 0):
            fan = True
        else:
            fan = False
        setterControlador(self.VentiladorLabel, fan)
        setterControlador(self.VentiladorPorcent,self.bfan)

        self.top.after(70, self.clock,ind)

    def __init__(self, top=None):
        self.top = top
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#eaeaea'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#eaeaea' # X11 color: 'gray85'
        _ana1color = '#eaeaea' # X11 color: 'gray85' 
        _ana2color = '#eaeaea' # X11 color: 'gray85' 
        font11 = "-family {Segoe UI} -size 18 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        font12 = "-family {Segoe UI} -size 22 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        font9 = "-family {Segoe UI} -size 22 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        self.top.geometry("1072x673+457+191")
        self.top.title("Telemetria Auto Escolta")
        self.top.configure(background="#eaeaea")
        self.top.configure(highlightbackground="#d9d9d9")
        self.top.configure(highlightcolor="black")


        self.style.configure('TNotebook.Tab', background=_bgcolor)
        self.style.configure('TNotebook.Tab', foreground=_fgcolor)
        self.style.map('TNotebook.Tab', background=
            [('selected', _compcolor), ('active',_ana2color)])
        self.Tabulador = ttk.Notebook(self.top)
        self.Tabulador.place(relx=0.28, rely=0.01, relheight=0.98, relwidth=0.71)

        self.Tabulador.configure(width=764)
        self.Tabulador.configure(takefocus="")
        self.TabBateriaPaneles = ttk.Frame(self.Tabulador)
        self.Tabulador.add(self.TabBateriaPaneles, padding=3)
        self.Tabulador.tab(0, text="Batería/Paneles",underline="-1",)
        self.TabGPS = ttk.Frame(self.Tabulador)
        self.Tabulador.add(self.TabGPS, padding=3)
        self.Tabulador.tab(1, text="GPS",underline="-1",)


        self.LabelLatitudLongitud = LabelFrame(self.TabGPS)
        self.LabelLatitudLongitud.place(relx=0.0, rely=0.0, relheight=0.35
                , relwidth=1.0)
        self.LabelLatitudLongitud.configure(relief=GROOVE)
        self.LabelLatitudLongitud.configure(foreground="black")
        self.LabelLatitudLongitud.configure(text='''Longitud vs Latitud''')
        self.LabelLatitudLongitud.configure(background="#eaeaea")
        self.LabelLatitudLongitud.configure(highlightbackground="#d9d9d9")
        self.LabelLatitudLongitud.configure(highlightcolor="black")
        self.LabelLatitudLongitud.configure(width=760)

        self.LabelGPS = LabelFrame(self.TabGPS)
        self.LabelGPS.place(relx=0.0, rely=0.36, relheight=0.64
                , relwidth=1.0)
        self.LabelGPS.configure(relief=GROOVE)
        self.LabelGPS.configure(foreground="black")
        self.LabelGPS.configure(text='''GPS''')
        self.LabelGPS.configure(background="#eaeaea")
        self.LabelGPS.configure(highlightbackground="#d9d9d9")
        self.LabelGPS.configure(highlightcolor="black")
        self.LabelGPS.configure(width=760)



        self.LabelframeBateria = LabelFrame(self.TabBateriaPaneles)
        self.LabelframeBateria.place(relx=0.0, rely=0.0, relheight=0.35
                , relwidth=1.0)
        self.LabelframeBateria.configure(relief=GROOVE)
        self.LabelframeBateria.configure(foreground="black")
        self.LabelframeBateria.configure(text='''Baterías''')
        self.LabelframeBateria.configure(background="#eaeaea")
        self.LabelframeBateria.configure(highlightbackground="#d9d9d9")
        self.LabelframeBateria.configure(highlightcolor="black")
        self.LabelframeBateria.configure(width=760)

        self.LabelframePaneles = LabelFrame(self.TabBateriaPaneles)
        self.LabelframePaneles.place(relx=0.0, rely=0.36, relheight=0.35
                , relwidth=1.0)
        self.LabelframePaneles.configure(relief=GROOVE)
        self.LabelframePaneles.configure(foreground="black")
        self.LabelframePaneles.configure(text='''Paneles''')
        self.LabelframePaneles.configure(background="#eaeaea")
        self.LabelframePaneles.configure(highlightbackground="#d9d9d9")
        self.LabelframePaneles.configure(highlightcolor="black")
        self.LabelframePaneles.configure(width=760)

        self.Frame1 = Frame(self.LabelframePaneles)
        self.Frame1.place(relx=0.1, rely=0.09, relheight=0.51, relwidth=0.15)
        self.Frame1.configure(relief=GROOVE)
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief=GROOVE)
        self.Frame1.configure(background="#d9d9d9")
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="black")
        self.Frame1.configure(width=115)

        self.VoltajeBateria1Label = Label(self.LabelframePaneles)
        self.VoltajeBateria1Label.place(relx=0.12, rely=0.67, height=21
                , width=60)
        self.VoltajeBateria1Label.configure(activebackground="#f9f9f9")
        self.VoltajeBateria1Label.configure(activeforeground="black")
        self.VoltajeBateria1Label.configure(background="#eaeaea")
        self.VoltajeBateria1Label.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria1Label.configure(foreground="#000000")
        self.VoltajeBateria1Label.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria1Label.configure(highlightcolor="black")
        self.VoltajeBateria1Label.configure(text='''Voltaje(V):''')

        self.Frame2 = Frame(self.LabelframePaneles)
        self.Frame2.place(relx=0.36, rely=0.09, relheight=0.51, relwidth=0.15)
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(background="#d9d9d9")
        self.Frame2.configure(highlightbackground="#d9d9d9")
        self.Frame2.configure(highlightcolor="black")
        self.Frame2.configure(width=115)

        self.Frame3 = Frame(self.LabelframePaneles)
        self.Frame3.place(relx=0.63, rely=0.09, relheight=0.51, relwidth=0.15)
        self.Frame3.configure(relief=GROOVE)
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief=GROOVE)
        self.Frame3.configure(background="#d9d9d9")
        self.Frame3.configure(highlightbackground="#d9d9d9")
        self.Frame3.configure(highlightcolor="black")
        self.Frame3.configure(width=115)

        self.Corriente1Label = Label(self.LabelframePaneles)
        self.Corriente1Label.place(relx=0.12, rely=0.76, height=21, width=74)
        self.Corriente1Label.configure(activebackground="#f9f9f9")
        self.Corriente1Label.configure(activeforeground="black")
        self.Corriente1Label.configure(background="#eaeaea")
        self.Corriente1Label.configure(disabledforeground="#a3a3a3")
        self.Corriente1Label.configure(foreground="#000000")
        self.Corriente1Label.configure(highlightbackground="#d9d9d9")
        self.Corriente1Label.configure(highlightcolor="black")
        self.Corriente1Label.configure(text='''Corriente(A):''')

        self.Potencia1Label = Label(self.LabelframePaneles)
        self.Potencia1Label.place(relx=0.12, rely=0.85, height=21, width=72)
        self.Potencia1Label.configure(activebackground="#f9f9f9")
        self.Potencia1Label.configure(activeforeground="black")
        self.Potencia1Label.configure(background="#eaeaea")
        self.Potencia1Label.configure(disabledforeground="#a3a3a3")
        self.Potencia1Label.configure(foreground="#000000")
        self.Potencia1Label.configure(highlightbackground="#d9d9d9")
        self.Potencia1Label.configure(highlightcolor="black")
        self.Potencia1Label.configure(text='''Potencia(w):''')

        self.VoltajeBateria2Label = Label(self.LabelframePaneles)
        self.VoltajeBateria2Label.place(relx=0.38, rely=0.67, height=21
                , width=60)
        self.VoltajeBateria2Label.configure(activebackground="#f9f9f9")
        self.VoltajeBateria2Label.configure(activeforeground="black")
        self.VoltajeBateria2Label.configure(background="#eaeaea")
        self.VoltajeBateria2Label.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria2Label.configure(foreground="#000000")
        self.VoltajeBateria2Label.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria2Label.configure(highlightcolor="black")
        self.VoltajeBateria2Label.configure(text='''Voltaje(V):''')

        self.VoltajeBateria3Label = Label(self.LabelframePaneles)
        self.VoltajeBateria3Label.place(relx=0.64, rely=0.67, height=21
                , width=60)
        self.VoltajeBateria3Label.configure(activebackground="#f9f9f9")
        self.VoltajeBateria3Label.configure(activeforeground="black")
        self.VoltajeBateria3Label.configure(background="#eaeaea")
        self.VoltajeBateria3Label.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria3Label.configure(foreground="#000000")
        self.VoltajeBateria3Label.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria3Label.configure(highlightcolor="black")
        self.VoltajeBateria3Label.configure(text='''Voltaje(V):''')

        self.Corriente2Label = Label(self.LabelframePaneles)
        self.Corriente2Label.place(relx=0.38, rely=0.76, height=21, width=74)
        self.Corriente2Label.configure(activebackground="#f9f9f9")
        self.Corriente2Label.configure(activeforeground="black")
        self.Corriente2Label.configure(background="#eaeaea")
        self.Corriente2Label.configure(disabledforeground="#a3a3a3")
        self.Corriente2Label.configure(foreground="#000000")
        self.Corriente2Label.configure(highlightbackground="#d9d9d9")
        self.Corriente2Label.configure(highlightcolor="black")
        self.Corriente2Label.configure(text='''Corriente(A):''')

        self.Corriente3Label = Label(self.LabelframePaneles)
        self.Corriente3Label.place(relx=0.64, rely=0.76, height=21, width=74)
        self.Corriente3Label.configure(activebackground="#f9f9f9")
        self.Corriente3Label.configure(activeforeground="black")
        self.Corriente3Label.configure(background="#eaeaea")
        self.Corriente3Label.configure(disabledforeground="#a3a3a3")
        self.Corriente3Label.configure(foreground="#000000")
        self.Corriente3Label.configure(highlightbackground="#d9d9d9")
        self.Corriente3Label.configure(highlightcolor="black")
        self.Corriente3Label.configure(text='''Corriente(A):''')

        self.Potencia2Label = Label(self.LabelframePaneles)
        self.Potencia2Label.place(relx=0.38, rely=0.85, height=21, width=72)
        self.Potencia2Label.configure(activebackground="#f9f9f9")
        self.Potencia2Label.configure(activeforeground="black")
        self.Potencia2Label.configure(background="#eaeaea")
        self.Potencia2Label.configure(disabledforeground="#a3a3a3")
        self.Potencia2Label.configure(foreground="#000000")
        self.Potencia2Label.configure(highlightbackground="#d9d9d9")
        self.Potencia2Label.configure(highlightcolor="black")
        self.Potencia2Label.configure(text='''Potencia(w):''')

        self.Potencia3Label = Label(self.LabelframePaneles)
        self.Potencia3Label.place(relx=0.64, rely=0.85, height=21, width=72)
        self.Potencia3Label.configure(activebackground="#f9f9f9")
        self.Potencia3Label.configure(activeforeground="black")
        self.Potencia3Label.configure(background="#eaeaea")
        self.Potencia3Label.configure(disabledforeground="#a3a3a3")
        self.Potencia3Label.configure(foreground="#000000")
        self.Potencia3Label.configure(highlightbackground="#d9d9d9")
        self.Potencia3Label.configure(highlightcolor="black")
        self.Potencia3Label.configure(text='''Potencia(w):''')

        self.PotenciaTotalLabel = Label(self.LabelframePaneles)
        self.PotenciaTotalLabel.place(relx=0.83, rely=0.04, height=21, width=82)
        self.PotenciaTotalLabel.configure(activebackground="#f9f9f9")
        self.PotenciaTotalLabel.configure(activeforeground="black")
        self.PotenciaTotalLabel.configure(background="#eaeaea")
        self.PotenciaTotalLabel.configure(disabledforeground="#a3a3a3")
        self.PotenciaTotalLabel.configure(foreground="#000000")
        self.PotenciaTotalLabel.configure(highlightbackground="#d9d9d9")
        self.PotenciaTotalLabel.configure(highlightcolor="black")
        self.PotenciaTotalLabel.configure(text='''Potencia total:''')

        self.PotenciaTotal = Label(self.LabelframePaneles)
        self.PotenciaTotal.place(relx=0.86, rely=0.13, height=21, width=42)
        self.PotenciaTotal.configure(activebackground="#f9f9f9")
        self.PotenciaTotal.configure(activeforeground="black")
        self.PotenciaTotal.configure(background="#eaeaea")
        self.PotenciaTotal.configure(disabledforeground="#a3a3a3")
        self.PotenciaTotal.configure(foreground="#000000")
        self.PotenciaTotal.configure(highlightbackground="#d9d9d9")
        self.PotenciaTotal.configure(highlightcolor="black")
        self.PotenciaTotal.configure(text='''1200 w''')

        self.ErrorPanel1Label = Label(self.LabelframePaneles)
        self.ErrorPanel1Label.place(relx=0.83, rely=0.25, height=21, width=91)
        self.ErrorPanel1Label.configure(activebackground="#f9f9f9")
        self.ErrorPanel1Label.configure(activeforeground="black")
        self.ErrorPanel1Label.configure(background="#eaeaea")
        self.ErrorPanel1Label.configure(disabledforeground="#a3a3a3")
        self.ErrorPanel1Label.configure(foreground="#000000")
        self.ErrorPanel1Label.configure(highlightbackground="#d9d9d9")
        self.ErrorPanel1Label.configure(highlightcolor="black")
        self.ErrorPanel1Label.configure(text='''Error Panel 1:''')
        self.ErrorPanel1Label.configure(width=91)

        self.VoltajeBateria1 = Label(self.LabelframePaneles)
        self.VoltajeBateria1.place(relx=0.22, rely=0.67, height=21, width=34)
        self.VoltajeBateria1.configure(activebackground="#f9f9f9")
        self.VoltajeBateria1.configure(activeforeground="black")
        self.VoltajeBateria1.configure(background="#eaeaea")
        self.VoltajeBateria1.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria1.configure(foreground="#000000")
        self.VoltajeBateria1.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria1.configure(highlightcolor="black")
        self.VoltajeBateria1.configure(text='''0''')

        self.CorrienteBateria1 = Label(self.LabelframePaneles)
        self.CorrienteBateria1.place(relx=0.22, rely=0.76, height=21, width=34)
        self.CorrienteBateria1.configure(activebackground="#f9f9f9")
        self.CorrienteBateria1.configure(activeforeground="black")
        self.CorrienteBateria1.configure(background="#eaeaea")
        self.CorrienteBateria1.configure(disabledforeground="#a3a3a3")
        self.CorrienteBateria1.configure(foreground="#000000")
        self.CorrienteBateria1.configure(highlightbackground="#d9d9d9")
        self.CorrienteBateria1.configure(highlightcolor="black")
        self.CorrienteBateria1.configure(text='''0''')

        self.PotenciaBateria1 = Label(self.LabelframePaneles)
        self.PotenciaBateria1.place(relx=0.22, rely=0.85, height=21, width=34)
        self.PotenciaBateria1.configure(activebackground="#f9f9f9")
        self.PotenciaBateria1.configure(activeforeground="black")
        self.PotenciaBateria1.configure(background="#eaeaea")
        self.PotenciaBateria1.configure(disabledforeground="#a3a3a3")
        self.PotenciaBateria1.configure(foreground="#000000")
        self.PotenciaBateria1.configure(highlightbackground="#d9d9d9")
        self.PotenciaBateria1.configure(highlightcolor="black")
        self.PotenciaBateria1.configure(text='''0''')

        self.VoltajeBateria2 = Label(self.LabelframePaneles)
        self.VoltajeBateria2.place(relx=0.47, rely=0.67, height=21, width=44)
        self.VoltajeBateria2.configure(activebackground="#f9f9f9")
        self.VoltajeBateria2.configure(activeforeground="black")
        self.VoltajeBateria2.configure(background="#eaeaea")
        self.VoltajeBateria2.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria2.configure(foreground="#000000")
        self.VoltajeBateria2.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria2.configure(highlightcolor="black")
        self.VoltajeBateria2.configure(text='''0''')

        self.CorrienteBateria2 = Label(self.LabelframePaneles)
        self.CorrienteBateria2.place(relx=0.47, rely=0.76, height=21, width=44)
        self.CorrienteBateria2.configure(activebackground="#f9f9f9")
        self.CorrienteBateria2.configure(activeforeground="black")
        self.CorrienteBateria2.configure(background="#eaeaea")
        self.CorrienteBateria2.configure(disabledforeground="#a3a3a3")
        self.CorrienteBateria2.configure(foreground="#000000")
        self.CorrienteBateria2.configure(highlightbackground="#d9d9d9")
        self.CorrienteBateria2.configure(highlightcolor="black")
        self.CorrienteBateria2.configure(text='''0''')

        self.PotenciaBateria2 = Label(self.LabelframePaneles)
        self.PotenciaBateria2.place(relx=0.47, rely=0.85, height=21, width=44)
        self.PotenciaBateria2.configure(activebackground="#f9f9f9")
        self.PotenciaBateria2.configure(activeforeground="black")
        self.PotenciaBateria2.configure(background="#eaeaea")
        self.PotenciaBateria2.configure(disabledforeground="#a3a3a3")
        self.PotenciaBateria2.configure(foreground="#000000")
        self.PotenciaBateria2.configure(highlightbackground="#d9d9d9")
        self.PotenciaBateria2.configure(highlightcolor="black")
        self.PotenciaBateria2.configure(text='''0''')

        self.VoltajeBateria3 = Label(self.LabelframePaneles)
        self.VoltajeBateria3.place(relx=0.74, rely=0.67, height=21, width=44)
        self.VoltajeBateria3.configure(activebackground="#f9f9f9")
        self.VoltajeBateria3.configure(activeforeground="black")
        self.VoltajeBateria3.configure(background="#eaeaea")
        self.VoltajeBateria3.configure(disabledforeground="#a3a3a3")
        self.VoltajeBateria3.configure(foreground="#000000")
        self.VoltajeBateria3.configure(highlightbackground="#d9d9d9")
        self.VoltajeBateria3.configure(highlightcolor="black")
        self.VoltajeBateria3.configure(text='''0''')

        self.CorrienteBateria3 = Label(self.LabelframePaneles)
        self.CorrienteBateria3.place(relx=0.74, rely=0.76, height=21, width=44)
        self.CorrienteBateria3.configure(activebackground="#f9f9f9")
        self.CorrienteBateria3.configure(activeforeground="black")
        self.CorrienteBateria3.configure(background="#eaeaea")
        self.CorrienteBateria3.configure(disabledforeground="#a3a3a3")
        self.CorrienteBateria3.configure(foreground="#000000")
        self.CorrienteBateria3.configure(highlightbackground="#d9d9d9")
        self.CorrienteBateria3.configure(highlightcolor="black")
        self.CorrienteBateria3.configure(text='''0''')

        self.PotenciaBateria3 = Label(self.LabelframePaneles)
        self.PotenciaBateria3.place(relx=0.74, rely=0.85, height=21, width=44)
        self.PotenciaBateria3.configure(activebackground="#f9f9f9")
        self.PotenciaBateria3.configure(activeforeground="black")
        self.PotenciaBateria3.configure(background="#eaeaea")
        self.PotenciaBateria3.configure(disabledforeground="#a3a3a3")
        self.PotenciaBateria3.configure(foreground="#000000")
        self.PotenciaBateria3.configure(highlightbackground="#d9d9d9")
        self.PotenciaBateria3.configure(highlightcolor="black")
        self.PotenciaBateria3.configure(text='''0''')

        self.ErrorPanel2Label = Label(self.LabelframePaneles)
        self.ErrorPanel2Label.place(relx=0.83, rely=0.46, height=21, width=95)
        self.ErrorPanel2Label.configure(background="#eaeaea")
        self.ErrorPanel2Label.configure(disabledforeground="#b0b0b0")
        self.ErrorPanel2Label.configure(foreground="#000000")
        self.ErrorPanel2Label.configure(text='''Error Panel 2:''')
        self.ErrorPanel2Label.configure(width=95)

        self.ErrorPanel2 = Label(self.LabelframePaneles)
        self.ErrorPanel2.place(relx=0.83, rely=0.55, height=21, width=83)
        self.ErrorPanel2.configure(background="#eaeaea")
        self.ErrorPanel2.configure(disabledforeground="#b0b0b0")
        self.ErrorPanel2.configure(foreground="#000000")
        self.ErrorPanel2.configure(text='''No hay errores''')

        self.ErrorPanel3Label = Label(self.LabelframePaneles)
        self.ErrorPanel3Label.place(relx=0.84, rely=0.67, height=21, width=75)
        self.ErrorPanel3Label.configure(background="#eaeaea")
        self.ErrorPanel3Label.configure(disabledforeground="#b0b0b0")
        self.ErrorPanel3Label.configure(foreground="#000000")
        self.ErrorPanel3Label.configure(text='''Error Panel 3:''')

        self.ErrorPanel1 = Label(self.LabelframePaneles)
        self.ErrorPanel1.place(relx=0.83, rely=0.34, height=21, width=83)
        self.ErrorPanel1.configure(background="#eaeaea")
        self.ErrorPanel1.configure(disabledforeground="#b0b0b0")
        self.ErrorPanel1.configure(foreground="#000000")
        self.ErrorPanel1.configure(text='''No hay errores''')

        self.ErrorPanel3 = Label(self.LabelframePaneles)
        self.ErrorPanel3.place(relx=0.83, rely=0.76, height=21, width=83)
        self.ErrorPanel3.configure(background="#eaeaea")
        self.ErrorPanel3.configure(disabledforeground="#b0b0b0")
        self.ErrorPanel3.configure(foreground="#000000")
        self.ErrorPanel3.configure(text='''No hay errores''')

        self.LabelFrameEstadoBotonesPantalla = LabelFrame(self.TabBateriaPaneles)
        self.LabelFrameEstadoBotonesPantalla.place(relx=0.71, rely=0.73
                , relheight=0.26, relwidth=0.29)
        self.LabelFrameEstadoBotonesPantalla.configure(relief=GROOVE)
        self.LabelFrameEstadoBotonesPantalla.configure(foreground="black")
        self.LabelFrameEstadoBotonesPantalla.configure(text='''Estado Botones Pantalla''')
        self.LabelFrameEstadoBotonesPantalla.configure(background="#eaeaea")
        self.LabelFrameEstadoBotonesPantalla.configure(highlightbackground="#d9d9d9")
        self.LabelFrameEstadoBotonesPantalla.configure(highlightcolor="black")
        self.LabelFrameEstadoBotonesPantalla.configure(width=220)

        self.BateriaLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.BateriaLabel.place(relx=0.09, rely=0.05, height=21, width=42)
        self.BateriaLabel.configure(activebackground="#ffffff")
        self.BateriaLabel.configure(activeforeground="black")
        self.BateriaLabel.configure(background="#eaeaea")
        self.BateriaLabel.configure(disabledforeground="#a3a3a3")
        self.BateriaLabel.configure(foreground="#7c7c7c")
        self.BateriaLabel.configure(highlightbackground="#eaeaea")
        self.BateriaLabel.configure(highlightcolor="black")
        self.BateriaLabel.configure(text='''Batería''')

        self.mpptLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.mpptLabel.place(relx=0.09, rely=0.23, height=21, width=35)
        self.mpptLabel.configure(activebackground="#ffffff")
        self.mpptLabel.configure(activeforeground="black")
        self.mpptLabel.configure(background="#eaeaea")
        self.mpptLabel.configure(disabledforeground="#a3a3a3")
        self.mpptLabel.configure(foreground="#7c7c7c")
        self.mpptLabel.configure(highlightbackground="#eaeaea")
        self.mpptLabel.configure(highlightcolor="black")
        self.mpptLabel.configure(text='''mppt''')

        self.mppt1Label = Label(self.LabelFrameEstadoBotonesPantalla)
        self.mppt1Label.place(relx=0.09, rely=0.41, height=21, width=41)
        self.mppt1Label.configure(activebackground="#ffffff")
        self.mppt1Label.configure(activeforeground="black")
        self.mppt1Label.configure(background="#eaeaea")
        self.mppt1Label.configure(disabledforeground="#a3a3a3")
        self.mppt1Label.configure(foreground="#7c7c7c")
        self.mppt1Label.configure(highlightbackground="#eaeaea")
        self.mppt1Label.configure(highlightcolor="black")
        self.mppt1Label.configure(text='''mppt1''')

        self.mppt2Label = Label(self.LabelFrameEstadoBotonesPantalla)
        self.mppt2Label.place(relx=0.09, rely=0.59, height=21, width=41)
        self.mppt2Label.configure(activebackground="#ffffff")
        self.mppt2Label.configure(activeforeground="black")
        self.mppt2Label.configure(background="#eaeaea")
        self.mppt2Label.configure(disabledforeground="#a3a3a3")
        self.mppt2Label.configure(foreground="#7c7c7c")
        self.mppt2Label.configure(highlightbackground="#eaeaea")
        self.mppt2Label.configure(highlightcolor="black")
        self.mppt2Label.configure(text='''mppt2''')

        self.mppt3Label = Label(self.LabelFrameEstadoBotonesPantalla)
        self.mppt3Label.place(relx=0.09, rely=0.78, height=21, width=41)
        self.mppt3Label.configure(activebackground="#ffffff")
        self.mppt3Label.configure(activeforeground="black")
        self.mppt3Label.configure(background="#eaeaea")
        self.mppt3Label.configure(disabledforeground="#a3a3a3")
        self.mppt3Label.configure(foreground="#7c7c7c")
        self.mppt3Label.configure(highlightbackground="#eaeaea")
        self.mppt3Label.configure(highlightcolor="black")
        self.mppt3Label.configure(text='''mppt3''')

        self.LucesAltasLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.LucesAltasLabel.place(relx=0.36, rely=0.12, height=21, width=63)
        self.LucesAltasLabel.configure(activebackground="#ffffff")
        self.LucesAltasLabel.configure(activeforeground="black")
        self.LucesAltasLabel.configure(background="#eaeaea")
        self.LucesAltasLabel.configure(disabledforeground="#a3a3a3")
        self.LucesAltasLabel.configure(foreground="#7c7c7c")
        self.LucesAltasLabel.configure(highlightbackground="#eaeaea")
        self.LucesAltasLabel.configure(highlightcolor="black")
        self.LucesAltasLabel.configure(text='''Luces altas''')

        self.LucesBajasLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.LucesBajasLabel.place(relx=0.36, rely=0.3, height=21, width=66)
        self.LucesBajasLabel.configure(activebackground="#ffffff")
        self.LucesBajasLabel.configure(activeforeground="black")
        self.LucesBajasLabel.configure(background="#eaeaea")
        self.LucesBajasLabel.configure(disabledforeground="#a3a3a3")
        self.LucesBajasLabel.configure(foreground="#7c7c7c")
        self.LucesBajasLabel.configure(highlightbackground="#eaeaea")
        self.LucesBajasLabel.configure(highlightcolor="black")
        self.LucesBajasLabel.configure(text='''Luces bajas''')

        self.LucesEmergenciaLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.LucesEmergenciaLabel.place(relx=0.36, rely=0.48, height=21
                , width=117)
        self.LucesEmergenciaLabel.configure(activebackground="#ffffff")
        self.LucesEmergenciaLabel.configure(activeforeground="black")
        self.LucesEmergenciaLabel.configure(background="#eaeaea")
        self.LucesEmergenciaLabel.configure(disabledforeground="#a3a3a3")
        self.LucesEmergenciaLabel.configure(foreground="#7c7c7c")
        self.LucesEmergenciaLabel.configure(highlightbackground="#eaeaea")
        self.LucesEmergenciaLabel.configure(highlightcolor="black")
        self.LucesEmergenciaLabel.configure(text='''Luces de emergencia''')

        self.VentiladorLabel = Label(self.LabelFrameEstadoBotonesPantalla)
        self.VentiladorLabel.place(relx=0.36, rely=0.67, height=21, width=63)
        self.VentiladorLabel.configure(activebackground="#ffffff")
        self.VentiladorLabel.configure(activeforeground="black")
        self.VentiladorLabel.configure(background="#eaeaea")
        self.VentiladorLabel.configure(disabledforeground="#a3a3a3")
        self.VentiladorLabel.configure(foreground="#000000")
        self.VentiladorLabel.configure(highlightbackground="#eaeaea")
        self.VentiladorLabel.configure(highlightcolor="black")
        self.VentiladorLabel.configure(text='''Ventilador:''')

        self.VentiladorPorcent = Label(self.LabelFrameEstadoBotonesPantalla)
        self.VentiladorPorcent.place(relx=0.68, rely=0.67, height=21, width=54)
        self.VentiladorPorcent.configure(background="#eaeaea")
        self.VentiladorPorcent.configure(disabledforeground="#b0b0b0")
        self.VentiladorPorcent.configure(foreground="#000000")
        self.VentiladorPorcent.configure(text='''0%''')
        self.VentiladorPorcent.configure(width=54)

        self.LabelframeSensores = LabelFrame(self.TabBateriaPaneles)
        self.LabelframeSensores.place(relx=0.0, rely=0.73, relheight=0.26
                , relwidth=0.24)
        self.LabelframeSensores.configure(relief=GROOVE)
        self.LabelframeSensores.configure(foreground="black")
        self.LabelframeSensores.configure(text='''Sensores''')
        self.LabelframeSensores.configure(background="#eaeaea")
        self.LabelframeSensores.configure(highlightbackground="#d9d9d9")
        self.LabelframeSensores.configure(highlightcolor="black")
        self.LabelframeSensores.configure(width=180)

        self.SensorCorrienteLabel = Label(self.LabelframeSensores)
        self.SensorCorrienteLabel.place(relx=0.06, rely=0.1, height=21
                , width=58)
        self.SensorCorrienteLabel.configure(activebackground="#f9f9f9")
        self.SensorCorrienteLabel.configure(activeforeground="black")
        self.SensorCorrienteLabel.configure(background="#eaeaea")
        self.SensorCorrienteLabel.configure(disabledforeground="#a3a3a3")
        self.SensorCorrienteLabel.configure(foreground="#000000")
        self.SensorCorrienteLabel.configure(highlightbackground="#d9d9d9")
        self.SensorCorrienteLabel.configure(highlightcolor="black")
        self.SensorCorrienteLabel.configure(text='''Corriente:''')

        self.SensorTemperaturaLabel1 = Label(self.LabelframeSensores)
        self.SensorTemperaturaLabel1.place(relx=0.06, rely=0.36, height=21
                , width=104)
        self.SensorTemperaturaLabel1.configure(activebackground="#f9f9f9")
        self.SensorTemperaturaLabel1.configure(activeforeground="black")
        self.SensorTemperaturaLabel1.configure(background="#eaeaea")
        self.SensorTemperaturaLabel1.configure(disabledforeground="#a3a3a3")
        self.SensorTemperaturaLabel1.configure(foreground="#000000")
        self.SensorTemperaturaLabel1.configure(highlightbackground="#d9d9d9")
        self.SensorTemperaturaLabel1.configure(highlightcolor="black")
        self.SensorTemperaturaLabel1.configure(text='''Temperatura (ºC) :''')

        self.SensorCorriente = Label(self.LabelframeSensores)
        self.SensorCorriente.place(relx=0.67, rely=0.1, height=21, width=44)
        self.SensorCorriente.configure(activebackground="#f9f9f9")
        self.SensorCorriente.configure(activeforeground="black")
        self.SensorCorriente.configure(background="#eaeaea")
        self.SensorCorriente.configure(disabledforeground="#a3a3a3")
        self.SensorCorriente.configure(foreground="#000000")
        self.SensorCorriente.configure(highlightbackground="#d9d9d9")
        self.SensorCorriente.configure(highlightcolor="black")
        self.SensorCorriente.configure(text='''0''')

        self.SensorTemperatura1 = Label(self.LabelframeSensores)
        self.SensorTemperatura1.place(relx=0.67, rely=0.36, height=21, width=44)
        self.SensorTemperatura1.configure(activebackground="#f9f9f9")
        self.SensorTemperatura1.configure(activeforeground="black")
        self.SensorTemperatura1.configure(background="#eaeaea")
        self.SensorTemperatura1.configure(disabledforeground="#a3a3a3")
        self.SensorTemperatura1.configure(foreground="#000000")
        self.SensorTemperatura1.configure(highlightbackground="#d9d9d9")
        self.SensorTemperatura1.configure(highlightcolor="black")
        self.SensorTemperatura1.configure(text='''0''')

        self.SensorTemperaturaLabel2 = Label(self.LabelframeSensores)
        self.SensorTemperaturaLabel2.place(relx=0.06, rely=0.62, height=21
                , width=104)
        self.SensorTemperaturaLabel2.configure(activebackground="#ffffff")
        self.SensorTemperaturaLabel2.configure(activeforeground="black")
        self.SensorTemperaturaLabel2.configure(background="#eaeaea")
        self.SensorTemperaturaLabel2.configure(disabledforeground="#a3a3a3")
        self.SensorTemperaturaLabel2.configure(foreground="#000000")
        self.SensorTemperaturaLabel2.configure(highlightbackground="#eaeaea")
        self.SensorTemperaturaLabel2.configure(highlightcolor="black")
        self.SensorTemperaturaLabel2.configure(text='''Temperatura (ºC) :''')

        self.SensorTemperatura2 = Label(self.LabelframeSensores)
        self.SensorTemperatura2.place(relx=0.67, rely=0.62, height=21, width=42)
        self.SensorTemperatura2.configure(activebackground="#ffffff")
        self.SensorTemperatura2.configure(activeforeground="black")
        self.SensorTemperatura2.configure(background="#eaeaea")
        self.SensorTemperatura2.configure(disabledforeground="#a3a3a3")
        self.SensorTemperatura2.configure(foreground="#000000")
        self.SensorTemperatura2.configure(highlightbackground="#eaeaea")
        self.SensorTemperatura2.configure(highlightcolor="black")
        self.SensorTemperatura2.configure(text='''0''')

        self.RMSLabel0 = Label(self.TabBateriaPaneles)
        self.RMSLabel0.place(relx=0.28, rely=0.75, height=21, width=124)
        self.RMSLabel0.configure(activebackground="#ffffff")
        self.RMSLabel0.configure(activeforeground="black")
        self.RMSLabel0.configure(background="#eaeaea")
        self.RMSLabel0.configure(disabledforeground="#a3a3a3")
        self.RMSLabel0.configure(foreground="#000000")
        self.RMSLabel0.configure(highlightbackground="#eaeaea")
        self.RMSLabel0.configure(highlightcolor="black")
        self.RMSLabel0.configure(text='''RMS Current C / B (A):''')

        self.C0 = Label(self.TabBateriaPaneles)
        self.C0.place(relx=0.49, rely=0.75, height=21, width=54)
        self.C0.configure(activebackground="#ffffff")
        self.C0.configure(activeforeground="black")
        self.C0.configure(background="#eaeaea")
        self.C0.configure(disabledforeground="#a3a3a3")
        self.C0.configure(foreground="#000000")
        self.C0.configure(highlightbackground="#eaeaea")
        self.C0.configure(highlightcolor="black")
        self.C0.configure(text='''0A''')

        self.B0 = Label(self.TabBateriaPaneles)
        self.B0.place(relx=0.58, rely=0.75, height=21, width=54)
        self.B0.configure(activebackground="#ffffff")
        self.B0.configure(activeforeground="black")
        self.B0.configure(background="#eaeaea")
        self.B0.configure(disabledforeground="#a3a3a3")
        self.B0.configure(foreground="#000000")
        self.B0.configure(highlightbackground="#eaeaea")
        self.B0.configure(highlightcolor="black")
        self.B0.configure(text='''0A''')

        self.VoltajesLabel1 = Label(self.TabBateriaPaneles)
        self.VoltajesLabel1.place(relx=0.28, rely=0.81, height=21, width=114)
        self.VoltajesLabel1.configure(activebackground="#ffffff")
        self.VoltajesLabel1.configure(activeforeground="black")
        self.VoltajesLabel1.configure(background="#eaeaea")
        self.VoltajesLabel1.configure(disabledforeground="#a3a3a3")
        self.VoltajesLabel1.configure(foreground="#000000")
        self.VoltajesLabel1.configure(highlightbackground="#eaeaea")
        self.VoltajesLabel1.configure(highlightcolor="black")
        self.VoltajesLabel1.configure(text='''Voltajes 1.5V / 3.3 V :''')

        self.V150 = Label(self.TabBateriaPaneles)
        self.V150.place(relx=0.49, rely=0.81, height=21, width=54)
        self.V150.configure(activebackground="#ffffff")
        self.V150.configure(activeforeground="black")
        self.V150.configure(background="#eaeaea")
        self.V150.configure(disabledforeground="#a3a3a3")
        self.V150.configure(foreground="#000000")
        self.V150.configure(highlightbackground="#eaeaea")
        self.V150.configure(highlightcolor="black")
        self.V150.configure(text='''0''')

        self.V330 = Label(self.TabBateriaPaneles)
        self.V330.place(relx=0.58, rely=0.81, height=21, width=54)
        self.V330.configure(activebackground="#ffffff")
        self.V330.configure(activeforeground="black")
        self.V330.configure(background="#eaeaea")
        self.V330.configure(disabledforeground="#a3a3a3")
        self.V330.configure(foreground="#000000")
        self.V330.configure(highlightbackground="#eaeaea")
        self.V330.configure(highlightcolor="black")
        self.V330.configure(text='''0''')

        self.VoltajesLabel2 = Label(self.TabBateriaPaneles)
        self.VoltajesLabel2.place(relx=0.28, rely=0.87, height=21, width=78)
        self.VoltajesLabel2.configure(activebackground="#ffffff")
        self.VoltajesLabel2.configure(activeforeground="black")
        self.VoltajesLabel2.configure(background="#eaeaea")
        self.VoltajesLabel2.configure(disabledforeground="#a3a3a3")
        self.VoltajesLabel2.configure(foreground="#000000")
        self.VoltajesLabel2.configure(highlightbackground="#eaeaea")
        self.VoltajesLabel2.configure(highlightcolor="black")
        self.VoltajesLabel2.configure(text='''Voltajes 1.9V :''')

        self.V190 = Label(self.TabBateriaPaneles)
        self.V190.place(relx=0.49, rely=0.87, height=21, width=54)
        self.V190.configure(activebackground="#ffffff")
        self.V190.configure(activeforeground="black")
        self.V190.configure(background="#eaeaea")
        self.V190.configure(disabledforeground="#a3a3a3")
        self.V190.configure(foreground="#000000")
        self.V190.configure(highlightbackground="#eaeaea")
        self.V190.configure(highlightcolor="black")
        self.V190.configure(text='''0''')

        self.OdometroLabel0 = Label(self.TabBateriaPaneles)
        self.OdometroLabel0.place(relx=0.28, rely=0.93, height=21, width=131)
        self.OdometroLabel0.configure(activebackground="#ffffff")
        self.OdometroLabel0.configure(activeforeground="black")
        self.OdometroLabel0.configure(background="#eaeaea")
        self.OdometroLabel0.configure(disabledforeground="#a3a3a3")
        self.OdometroLabel0.configure(foreground="#000000")
        self.OdometroLabel0.configure(highlightbackground="#eaeaea")
        self.OdometroLabel0.configure(highlightcolor="black")
        self.OdometroLabel0.configure(text='''Odometro(km)/Bus Ah:''')

        self.OdometroKM0 = Label(self.TabBateriaPaneles)
        self.OdometroKM0.place(relx=0.49, rely=0.93, height=21, width=54)
        self.OdometroKM0.configure(activebackground="#ffffff")
        self.OdometroKM0.configure(activeforeground="black")
        self.OdometroKM0.configure(background="#eaeaea")
        self.OdometroKM0.configure(disabledforeground="#a3a3a3")
        self.OdometroKM0.configure(foreground="#000000")
        self.OdometroKM0.configure(highlightbackground="#eaeaea")
        self.OdometroKM0.configure(highlightcolor="black")
        self.OdometroKM0.configure(text='''0Km''')

        self.OdometroAh0 = Label(self.TabBateriaPaneles)
        self.OdometroAh0.place(relx=0.58, rely=0.93, height=21, width=54)
        self.OdometroAh0.configure(activebackground="#ffffff")
        self.OdometroAh0.configure(activeforeground="black")
        self.OdometroAh0.configure(background="#eaeaea")
        self.OdometroAh0.configure(disabledforeground="#a3a3a3")
        self.OdometroAh0.configure(foreground="#000000")
        self.OdometroAh0.configure(highlightbackground="#eaeaea")
        self.OdometroAh0.configure(highlightcolor="black")
        self.OdometroAh0.configure(text='''0Ah''')

        self.LabelframeGeneral = LabelFrame(self.top)
        self.LabelframeGeneral.place(relx=0.01, rely=0.0, relheight=0.99
                , relwidth=0.27)
        self.LabelframeGeneral.configure(relief=GROOVE)
        self.LabelframeGeneral.configure(foreground="black")
        self.LabelframeGeneral.configure(text='''Información General''')
        self.LabelframeGeneral.configure(background="#eaeaea")
        self.LabelframeGeneral.configure(highlightbackground="#d9d9d9")
        self.LabelframeGeneral.configure(highlightcolor="black")
        self.LabelframeGeneral.configure(width=290)

        self.velocidad = Label(self.LabelframeGeneral)
        self.velocidad.place(relx=0.20, rely=0.01, height=31, width=184)
        self.velocidad.configure(activebackground="#f9f9f9")
        self.velocidad.configure(activeforeground="black")
        self.velocidad.configure(background="#eaeaea")
        self.velocidad.configure(disabledforeground="#a3a3a3")
        self.velocidad.configure(font=font12)
        self.velocidad.configure(foreground="#000000")
        self.velocidad.configure(highlightbackground="#d9d9d9")
        self.velocidad.configure(highlightcolor="black")
        self.velocidad.configure(text='''0 km/hr''')

        self.BarraProgresoSetVelocity = ttk.Progressbar(self.LabelframeGeneral)
        self.BarraProgresoSetVelocity.place(relx=0.52, rely=0.13, relwidth=0.34
                , relheight=0.0, height=22)

        self.SetVelocityLabel = Label(self.LabelframeGeneral)
        self.SetVelocityLabel.place(relx=0.03, rely=0.13, height=21, width=128)
        self.SetVelocityLabel.configure(activebackground="#f9f9f9")
        self.SetVelocityLabel.configure(activeforeground="black")
        self.SetVelocityLabel.configure(background="#eaeaea")
        self.SetVelocityLabel.configure(disabledforeground="#a3a3a3")
        self.SetVelocityLabel.configure(foreground="#000000")
        self.SetVelocityLabel.configure(highlightbackground="#d9d9d9")
        self.SetVelocityLabel.configure(highlightcolor="black")
        self.SetVelocityLabel.configure(text='''Setpoint Velocity (rpm)''')

        self.BarraProgresoSetCurrent = ttk.Progressbar(self.LabelframeGeneral)
        self.BarraProgresoSetCurrent.place(relx=0.52, rely=0.18, relwidth=0.34
                , relheight=0.0, height=22)

        self.SetCurrentLabel = Label(self.LabelframeGeneral)
        self.SetCurrentLabel.place(relx=0.03, rely=0.18, height=21, width=114)
        self.SetCurrentLabel.configure(activebackground="#f9f9f9")
        self.SetCurrentLabel.configure(activeforeground="black")
        self.SetCurrentLabel.configure(background="#eaeaea")
        self.SetCurrentLabel.configure(disabledforeground="#a3a3a3")
        self.SetCurrentLabel.configure(foreground="#000000")
        self.SetCurrentLabel.configure(highlightbackground="#d9d9d9")
        self.SetCurrentLabel.configure(highlightcolor="black")
        self.SetCurrentLabel.configure(text='''SetPoint Current (%)''')

        self.BarraProgresoSetBus = ttk.Progressbar(self.LabelframeGeneral)
        self.BarraProgresoSetBus.place(relx=0.52, rely=0.23, relwidth=0.34
                , relheight=0.0, height=22)

        self.SetBusLabel = Label(self.LabelframeGeneral)
        self.SetBusLabel.place(relx=0.03, rely=0.23, height=21, width=136)
        self.SetBusLabel.configure(activebackground="#f9f9f9")
        self.SetBusLabel.configure(activeforeground="black")
        self.SetBusLabel.configure(background="#eaeaea")
        self.SetBusLabel.configure(disabledforeground="#a3a3a3")
        self.SetBusLabel.configure(foreground="#000000")
        self.SetBusLabel.configure(highlightbackground="#d9d9d9")
        self.SetBusLabel.configure(highlightcolor="black")
        self.SetBusLabel.configure(text='''Setpoint Bus Current (%)''')

        self.BusVoltajeLabel = Label(self.LabelframeGeneral)
        self.BusVoltajeLabel.place(relx=0.03, rely=0.48, height=21, width=85)
        self.BusVoltajeLabel.configure(activebackground="#f9f9f9")
        self.BusVoltajeLabel.configure(activeforeground="black")
        self.BusVoltajeLabel.configure(background="#eaeaea")
        self.BusVoltajeLabel.configure(disabledforeground="#a3a3a3")
        self.BusVoltajeLabel.configure(foreground="#000000")
        self.BusVoltajeLabel.configure(highlightbackground="#d9d9d9")
        self.BusVoltajeLabel.configure(highlightcolor="black")
        self.BusVoltajeLabel.configure(text='''Bus Voltaje (V):''')

        self.TemperaturaDSP = Label(self.LabelframeGeneral)
        self.TemperaturaDSP.place(relx=0.62, rely=0.57, height=21, width=54)
        self.TemperaturaDSP.configure(activebackground="#f9f9f9")
        self.TemperaturaDSP.configure(activeforeground="black")
        self.TemperaturaDSP.configure(background="#eaeaea")
        self.TemperaturaDSP.configure(disabledforeground="#a3a3a3")
        self.TemperaturaDSP.configure(foreground="#000000")
        self.TemperaturaDSP.configure(highlightbackground="#d9d9d9")
        self.TemperaturaDSP.configure(highlightcolor="black")
        self.TemperaturaDSP.configure(text='''0''')

        self.BusCurrentLabel = Label(self.LabelframeGeneral)
        self.BusCurrentLabel.place(relx=0.03, rely=0.44, height=21, width=86)
        self.BusCurrentLabel.configure(activebackground="#f9f9f9")
        self.BusCurrentLabel.configure(activeforeground="black")
        self.BusCurrentLabel.configure(background="#eaeaea")
        self.BusCurrentLabel.configure(disabledforeground="#a3a3a3")
        self.BusCurrentLabel.configure(foreground="#000000")
        self.BusCurrentLabel.configure(highlightbackground="#d9d9d9")
        self.BusCurrentLabel.configure(highlightcolor="black")
        self.BusCurrentLabel.configure(text='''Bus Current(A):''')

        self.TemperaturaMotorLabel = Label(self.LabelframeGeneral)
        self.TemperaturaMotorLabel.place(relx=0.03, rely=0.53, height=21
                , width=134)
        self.TemperaturaMotorLabel.configure(activebackground="#f9f9f9")
        self.TemperaturaMotorLabel.configure(activeforeground="black")
        self.TemperaturaMotorLabel.configure(background="#eaeaea")
        self.TemperaturaMotorLabel.configure(disabledforeground="#a3a3a3")
        self.TemperaturaMotorLabel.configure(foreground="#000000")
        self.TemperaturaMotorLabel.configure(highlightbackground="#d9d9d9")
        self.TemperaturaMotorLabel.configure(highlightcolor="black")
        self.TemperaturaMotorLabel.configure(text='''Temperatura Motor(ºC):''')

        self.TemperaturaDSPLabel = Label(self.LabelframeGeneral)
        self.TemperaturaDSPLabel.place(relx=0.03, rely=0.57, height=21
                , width=125)
        self.TemperaturaDSPLabel.configure(activebackground="#f9f9f9")
        self.TemperaturaDSPLabel.configure(activeforeground="black")
        self.TemperaturaDSPLabel.configure(background="#eaeaea")
        self.TemperaturaDSPLabel.configure(disabledforeground="#a3a3a3")
        self.TemperaturaDSPLabel.configure(foreground="#000000")
        self.TemperaturaDSPLabel.configure(highlightbackground="#d9d9d9")
        self.TemperaturaDSPLabel.configure(highlightcolor="black")
        self.TemperaturaDSPLabel.configure(text='''Temperatura DSP (ºC):''')

        self.TemperaturaMotor = Label(self.LabelframeGeneral)
        self.TemperaturaMotor.place(relx=0.62, rely=0.53, height=21, width=54)
        self.TemperaturaMotor.configure(activebackground="#f9f9f9")
        self.TemperaturaMotor.configure(activeforeground="black")
        self.TemperaturaMotor.configure(background="#eaeaea")
        self.TemperaturaMotor.configure(disabledforeground="#a3a3a3")
        self.TemperaturaMotor.configure(foreground="#000000")
        self.TemperaturaMotor.configure(highlightbackground="#d9d9d9")
        self.TemperaturaMotor.configure(highlightcolor="black")
        self.TemperaturaMotor.configure(text='''0''')

        self.BusCurrent = Label(self.LabelframeGeneral)
        self.BusCurrent.place(relx=0.62, rely=0.44, height=21, width=54)
        self.BusCurrent.configure(activebackground="#f9f9f9")
        self.BusCurrent.configure(activeforeground="black")
        self.BusCurrent.configure(background="#eaeaea")
        self.BusCurrent.configure(disabledforeground="#a3a3a3")
        self.BusCurrent.configure(foreground="#000000")
        self.BusCurrent.configure(highlightbackground="#d9d9d9")
        self.BusCurrent.configure(highlightcolor="black")
        self.BusCurrent.configure(text='''0''')

        self.BusVoltaje = Label(self.LabelframeGeneral)
        self.BusVoltaje.place(relx=0.62, rely=0.48, height=21, width=54)
        self.BusVoltaje.configure(activebackground="#f9f9f9")
        self.BusVoltaje.configure(activeforeground="black")
        self.BusVoltaje.configure(background="#eaeaea")
        self.BusVoltaje.configure(disabledforeground="#a3a3a3")
        self.BusVoltaje.configure(foreground="#000000")
        self.BusVoltaje.configure(highlightbackground="#d9d9d9")
        self.BusVoltaje.configure(highlightcolor="black")
        self.BusVoltaje.configure(text='''0''')

        self.ErroresLabel = Label(self.LabelframeGeneral)
        self.ErroresLabel.place(relx=0.03, rely=0.35, height=21, width=42)
        self.ErroresLabel.configure(activebackground="#f9f9f9")
        self.ErroresLabel.configure(activeforeground="black")
        self.ErroresLabel.configure(background="#eaeaea")
        self.ErroresLabel.configure(disabledforeground="#a3a3a3")
        self.ErroresLabel.configure(foreground="#000000")
        self.ErroresLabel.configure(highlightbackground="#d9d9d9")
        self.ErroresLabel.configure(highlightcolor="black")
        self.ErroresLabel.configure(text='''Errores:''')

        self.LabelframeEstadoControl = LabelFrame(self.LabelframeGeneral)
        self.LabelframeEstadoControl.place(relx=0.03, rely=0.83, relheight=0.16
                , relwidth=0.93)
        self.LabelframeEstadoControl.configure(relief=GROOVE)
        self.LabelframeEstadoControl.configure(foreground="black")
        self.LabelframeEstadoControl.configure(text='''Estado Controlador''')
        self.LabelframeEstadoControl.configure(background="#eaeaea")
        self.LabelframeEstadoControl.configure(highlightbackground="#d9d9d9")
        self.LabelframeEstadoControl.configure(highlightcolor="black")
        self.LabelframeEstadoControl.configure(width=270)

        self.ReverseLabel = Label(self.LabelframeEstadoControl)
        self.ReverseLabel.place(relx=0.04, rely=0.06, height=21, width=46)
        self.ReverseLabel.configure(background="#eaeaea")
        self.ReverseLabel.configure(disabledforeground="#b0b0b0")
        self.ReverseLabel.configure(foreground="#7c7c7c")
        self.ReverseLabel.configure(text='''Reverse''')

        self.NeutralLabel = Label(self.LabelframeEstadoControl)
        self.NeutralLabel.place(relx=0.04, rely=0.26, height=21, width=45)
        self.NeutralLabel.configure(activebackground="#f9f9f9")
        self.NeutralLabel.configure(activeforeground="black")
        self.NeutralLabel.configure(background="#eaeaea")
        self.NeutralLabel.configure(disabledforeground="#a3a3a3")
        self.NeutralLabel.configure(foreground="#7c7c7c")
        self.NeutralLabel.configure(text='''Neutral''')

        self.RegenLabel = Label(self.LabelframeEstadoControl)
        self.RegenLabel.place(relx=0.04, rely=0.46, height=21, width=39)
        self.RegenLabel.configure(activebackground="#f9f9f9")
        self.RegenLabel.configure(activeforeground="black")
        self.RegenLabel.configure(background="#eaeaea")
        self.RegenLabel.configure(disabledforeground="#a3a3a3")
        self.RegenLabel.configure(foreground="#7c7c7c")
        self.RegenLabel.configure(highlightbackground="#d9d9d9")
        self.RegenLabel.configure(highlightcolor="black")
        self.RegenLabel.configure(text='''Regen''')

        self.DriveLabel = Label(self.LabelframeEstadoControl)
        self.DriveLabel.place(relx=0.04, rely=0.66, height=21, width=33)
        self.DriveLabel.configure(activebackground="#f9f9f9")
        self.DriveLabel.configure(activeforeground="black")
        self.DriveLabel.configure(background="#eaeaea")
        self.DriveLabel.configure(disabledforeground="#a3a3a3")
        self.DriveLabel.configure(foreground="#7c7c7c")
        self.DriveLabel.configure(highlightbackground="#d9d9d9")
        self.DriveLabel.configure(highlightcolor="black")
        self.DriveLabel.configure(text='''Drive''')

        self.AccesoriesLabel = Label(self.LabelframeEstadoControl)
        self.AccesoriesLabel.place(relx=0.33, rely=0.06, height=21, width=62)
        self.AccesoriesLabel.configure(activebackground="#f9f9f9")
        self.AccesoriesLabel.configure(activeforeground="black")
        self.AccesoriesLabel.configure(background="#eaeaea")
        self.AccesoriesLabel.configure(disabledforeground="#a3a3a3")
        self.AccesoriesLabel.configure(foreground="#7c7c7c")
        self.AccesoriesLabel.configure(highlightbackground="#d9d9d9")
        self.AccesoriesLabel.configure(highlightcolor="black")
        self.AccesoriesLabel.configure(text='''Accesories''')

        self.RunLabel = Label(self.LabelframeEstadoControl)
        self.RunLabel.place(relx=0.33, rely=0.26, height=21, width=27)
        self.RunLabel.configure(activebackground="#f9f9f9")
        self.RunLabel.configure(activeforeground="black")
        self.RunLabel.configure(background="#eaeaea")
        self.RunLabel.configure(disabledforeground="#a3a3a3")
        self.RunLabel.configure(foreground="#7c7c7c")
        self.RunLabel.configure(highlightbackground="#d9d9d9")
        self.RunLabel.configure(highlightcolor="black")
        self.RunLabel.configure(text='''Run''')

        self.StartLabel = Label(self.LabelframeEstadoControl)
        self.StartLabel.place(relx=0.33, rely=0.46, height=21, width=30)
        self.StartLabel.configure(activebackground="#f9f9f9")
        self.StartLabel.configure(activeforeground="black")
        self.StartLabel.configure(background="#eaeaea")
        self.StartLabel.configure(disabledforeground="#a3a3a3")
        self.StartLabel.configure(foreground="#000000")
        self.StartLabel.configure(highlightbackground="#d9d9d9")
        self.StartLabel.configure(highlightcolor="black")
        self.StartLabel.configure(text='''Start''')

        self.BrakesLabel = Label(self.LabelframeEstadoControl)
        self.BrakesLabel.place(relx=0.67, rely=0.26, height=21, width=40)
        self.BrakesLabel.configure(activebackground="#f9f9f9")
        self.BrakesLabel.configure(activeforeground="black")
        self.BrakesLabel.configure(background="#eaeaea")
        self.BrakesLabel.configure(disabledforeground="#a3a3a3")
        self.BrakesLabel.configure(foreground="#7c7c7c")
        self.BrakesLabel.configure(highlightbackground="#d9d9d9")
        self.BrakesLabel.configure(highlightcolor="black")
        self.BrakesLabel.configure(text='''Brakes''')

        self.FuelDoorLabel = Label(self.LabelframeEstadoControl)
        self.FuelDoorLabel.place(relx=0.67, rely=0.06, height=21, width=57)
        self.FuelDoorLabel.configure(activebackground="#f9f9f9")
        self.FuelDoorLabel.configure(activeforeground="black")
        self.FuelDoorLabel.configure(background="#eaeaea")
        self.FuelDoorLabel.configure(disabledforeground="#a3a3a3")
        self.FuelDoorLabel.configure(foreground="#7c7c7c")
        self.FuelDoorLabel.configure(highlightbackground="#d9d9d9")
        self.FuelDoorLabel.configure(highlightcolor="black")
        self.FuelDoorLabel.configure(text='''Fuel Door''')

        self.RPM = Label(self.LabelframeGeneral)
        self.RPM.place(relx=0.1, rely=0.065, height=36, width=109)
        self.RPM.configure(activebackground="#f9f9f9")
        self.RPM.configure(activeforeground="black")
        self.RPM.configure(background="#eaeaea")
        self.RPM.configure(disabledforeground="#a3a3a3")
        self.RPM.configure(font=font11)
        self.RPM.configure(foreground="#000000")
        self.RPM.configure(highlightbackground="#d9d9d9")
        self.RPM.configure(highlightcolor="black")
        self.RPM.configure(text='''0 RPM''')

        self.FlagsLabel = Label(self.LabelframeGeneral)
        self.FlagsLabel.place(relx=0.03, rely=0.39, height=21, width=36)
        self.FlagsLabel.configure(activebackground="#f9f9f9")
        self.FlagsLabel.configure(activeforeground="black")
        self.FlagsLabel.configure(background="#eaeaea")
        self.FlagsLabel.configure(disabledforeground="#a3a3a3")
        self.FlagsLabel.configure(foreground="#000000")
        self.FlagsLabel.configure(highlightbackground="#d9d9d9")
        self.FlagsLabel.configure(highlightcolor="black")
        self.FlagsLabel.configure(text='''Flags:''')

        self.Errores = Label(self.LabelframeGeneral)
        self.Errores.place(relx=0.45, rely=0.35, height=21, width=112)
        self.Errores.configure(activebackground="#f9f9f9")
        self.Errores.configure(activeforeground="black")
        self.Errores.configure(background="#eaeaea")
        self.Errores.configure(disabledforeground="#a3a3a3")
        self.Errores.configure(foreground="#000000")
        self.Errores.configure(highlightbackground="#d9d9d9")
        self.Errores.configure(highlightcolor="black")
        self.Errores.configure(text='''DC Bus over voltage''')

        self.Flags = Label(self.LabelframeGeneral)
        self.Flags.place(relx=0.45, rely=0.39, height=21, width=112)
        self.Flags.configure(activebackground="#f9f9f9")
        self.Flags.configure(activeforeground="black")
        self.Flags.configure(background="#eaeaea")
        self.Flags.configure(disabledforeground="#a3a3a3")
        self.Flags.configure(foreground="#000000")
        self.Flags.configure(highlightbackground="#d9d9d9")
        self.Flags.configure(highlightcolor="black")
        self.Flags.configure(text='''Motor Current''')

        self.LabelframeBateríaMM = LabelFrame(self.LabelframeGeneral)
        self.LabelframeBateríaMM.place(relx=0.03, rely=0.63, relheight=0.19
                , relwidth=0.93)
        self.LabelframeBateríaMM.configure(relief=GROOVE)
        self.LabelframeBateríaMM.configure(foreground="black")
        self.LabelframeBateríaMM.configure(text='''Batería - Max y Min''')
        self.LabelframeBateríaMM.configure(background="#eaeaea")
        self.LabelframeBateríaMM.configure(highlightbackground="#d9d9d9")
        self.LabelframeBateríaMM.configure(highlightcolor="black")
        self.LabelframeBateríaMM.configure(width=270)

        self.TemperaturaMMLabel = Label(self.LabelframeBateríaMM)
        self.TemperaturaMMLabel.place(relx=0.04, rely=0.07, height=21, width=152)
        self.TemperaturaMMLabel.configure(activebackground="#f9f9f9")
        self.TemperaturaMMLabel.configure(activeforeground="black")
        self.TemperaturaMMLabel.configure(background="#eaeaea")
        self.TemperaturaMMLabel.configure(disabledforeground="#a3a3a3")
        self.TemperaturaMMLabel.configure(foreground="#000000")
        self.TemperaturaMMLabel.configure(highlightbackground="#d9d9d9")
        self.TemperaturaMMLabel.configure(highlightcolor="black")
        self.TemperaturaMMLabel.configure(text='''Tempertura Mín / Max (ºC):''')

        self.TemperaturaMIN = Label(self.LabelframeBateríaMM)
        self.TemperaturaMIN.place(relx=0.63, rely=0.07, height=21, width=35)
        self.TemperaturaMIN.configure(activebackground="#f9f9f9")
        self.TemperaturaMIN.configure(activeforeground="black")
        self.TemperaturaMIN.configure(background="#eaeaea")
        self.TemperaturaMIN.configure(disabledforeground="#a3a3a3")
        self.TemperaturaMIN.configure(foreground="#000000")
        self.TemperaturaMIN.configure(highlightbackground="#d9d9d9")
        self.TemperaturaMIN.configure(highlightcolor="black")
        self.TemperaturaMIN.configure(text='''0ºC''')

        self.TemperaturaMAX = Label(self.LabelframeBateríaMM)
        self.TemperaturaMAX.place(relx=0.81, rely=0.07, height=21, width=35)
        self.TemperaturaMAX.configure(activebackground="#f9f9f9")
        self.TemperaturaMAX.configure(activeforeground="black")
        self.TemperaturaMAX.configure(background="#eaeaea")
        self.TemperaturaMAX.configure(disabledforeground="#a3a3a3")
        self.TemperaturaMAX.configure(foreground="#000000")
        self.TemperaturaMAX.configure(highlightbackground="#d9d9d9")
        self.TemperaturaMAX.configure(highlightcolor="black")
        self.TemperaturaMAX.configure(text='''0ºC''')

        self.VoltajeMMLabel = Label(self.LabelframeBateríaMM)
        self.VoltajeMMLabel.place(relx=0.11, rely=0.53, height=21, width=130)
        self.VoltajeMMLabel.configure(activebackground="#f9f9f9")
        self.VoltajeMMLabel.configure(activeforeground="black")
        self.VoltajeMMLabel.configure(background="#eaeaea")
        self.VoltajeMMLabel.configure(disabledforeground="#a3a3a3")
        self.VoltajeMMLabel.configure(foreground="#000000")
        self.VoltajeMMLabel.configure(highlightbackground="#d9d9d9")
        self.VoltajeMMLabel.configure(highlightcolor="black")
        self.VoltajeMMLabel.configure(text='''Voltaje Mín / Max (V):''')

        self.CMUTempMMLabel = Label(self.LabelframeBateríaMM)
        self.CMUTempMMLabel.place(relx=0.15, rely=0.3, height=21, width=104)
        self.CMUTempMMLabel.configure(activebackground="#f9f9f9")
        self.CMUTempMMLabel.configure(activeforeground="black")
        self.CMUTempMMLabel.configure(background="#eaeaea")
        self.CMUTempMMLabel.configure(disabledforeground="#a3a3a3")
        self.CMUTempMMLabel.configure(foreground="#000000")
        self.CMUTempMMLabel.configure(highlightbackground="#d9d9d9")
        self.CMUTempMMLabel.configure(highlightcolor="black")
        self.CMUTempMMLabel.configure(text='''CMU Mín/Máx:''')

        self.CMUtempMIN = Label(self.LabelframeBateríaMM)
        self.CMUtempMIN.place(relx=0.63, rely=0.3, height=21, width=34)
        self.CMUtempMIN.configure(activebackground="#f9f9f9")
        self.CMUtempMIN.configure(activeforeground="black")
        self.CMUtempMIN.configure(background="#eaeaea")
        self.CMUtempMIN.configure(disabledforeground="#a3a3a3")
        self.CMUtempMIN.configure(foreground="#000000")
        self.CMUtempMIN.configure(highlightbackground="#d9d9d9")
        self.CMUtempMIN.configure(highlightcolor="black")
        self.CMUtempMIN.configure(text='''1''')

        self.CMUtempMAX = Label(self.LabelframeBateríaMM)
        self.CMUtempMAX.place(relx=0.81, rely=0.3, height=21, width=34)
        self.CMUtempMAX.configure(activebackground="#f9f9f9")
        self.CMUtempMAX.configure(activeforeground="black")
        self.CMUtempMAX.configure(background="#eaeaea")
        self.CMUtempMAX.configure(disabledforeground="#a3a3a3")
        self.CMUtempMAX.configure(foreground="#000000")
        self.CMUtempMAX.configure(highlightbackground="#d9d9d9")
        self.CMUtempMAX.configure(highlightcolor="black")
        self.CMUtempMAX.configure(text='''1''')

        self.VoltajeMIN = Label(self.LabelframeBateríaMM)
        self.VoltajeMIN.place(relx=0.63, rely=0.53, height=21, width=34)
        self.VoltajeMIN.configure(activebackground="#f9f9f9")
        self.VoltajeMIN.configure(activeforeground="black")
        self.VoltajeMIN.configure(background="#eaeaea")
        self.VoltajeMIN.configure(disabledforeground="#a3a3a3")
        self.VoltajeMIN.configure(foreground="#000000")
        self.VoltajeMIN.configure(highlightbackground="#d9d9d9")
        self.VoltajeMIN.configure(highlightcolor="black")
        self.VoltajeMIN.configure(text='''0''')

        self.VoltajeMAX = Label(self.LabelframeBateríaMM)
        self.VoltajeMAX.place(relx=0.81, rely=0.53, height=21, width=34)
        self.VoltajeMAX.configure(activebackground="#f9f9f9")
        self.VoltajeMAX.configure(activeforeground="black")
        self.VoltajeMAX.configure(background="#eaeaea")
        self.VoltajeMAX.configure(disabledforeground="#a3a3a3")
        self.VoltajeMAX.configure(foreground="#000000")
        self.VoltajeMAX.configure(highlightbackground="#d9d9d9")
        self.VoltajeMAX.configure(highlightcolor="black")
        self.VoltajeMAX.configure(text='''0''')

        self.CMUvoltMIN = Label(self.LabelframeBateríaMM)
        self.CMUvoltMIN.place(relx=0.63, rely=0.76, height=21, width=34)
        self.CMUvoltMIN.configure(activebackground="#f9f9f9")
        self.CMUvoltMIN.configure(activeforeground="black")
        self.CMUvoltMIN.configure(background="#eaeaea")
        self.CMUvoltMIN.configure(disabledforeground="#a3a3a3")
        self.CMUvoltMIN.configure(foreground="#000000")
        self.CMUvoltMIN.configure(highlightbackground="#d9d9d9")
        self.CMUvoltMIN.configure(highlightcolor="black")
        self.CMUvoltMIN.configure(text='''1''')

        self.CMUvoltMAX = Label(self.LabelframeBateríaMM)
        self.CMUvoltMAX.place(relx=0.81, rely=0.76, height=21, width=34)
        self.CMUvoltMAX.configure(activebackground="#f9f9f9")
        self.CMUvoltMAX.configure(activeforeground="black")
        self.CMUvoltMAX.configure(background="#eaeaea")
        self.CMUvoltMAX.configure(disabledforeground="#a3a3a3")
        self.CMUvoltMAX.configure(foreground="#000000")
        self.CMUvoltMAX.configure(highlightbackground="#d9d9d9")
        self.CMUvoltMAX.configure(highlightcolor="black")
        self.CMUvoltMAX.configure(text='''1''')

        self.CMUVoltMMLabel = Label(self.LabelframeBateríaMM)
        self.CMUVoltMMLabel.place(relx=0.15, rely=0.76, height=21, width=105)
        self.CMUVoltMMLabel.configure(activebackground="#f9f9f9")
        self.CMUVoltMMLabel.configure(activeforeground="black")
        self.CMUVoltMMLabel.configure(background="#eaeaea")
        self.CMUVoltMMLabel.configure(disabledforeground="#a3a3a3")
        self.CMUVoltMMLabel.configure(foreground="#000000")
        self.CMUVoltMMLabel.configure(highlightbackground="#d9d9d9")
        self.CMUVoltMMLabel.configure(highlightcolor="black")
        self.CMUVoltMMLabel.configure(text='''CMU Mín/Máx:''')

        self.SocLabel = Label(self.LabelframeGeneral)
        self.SocLabel.place(relx=0.03, rely=0.28, height=21, width=64)
        self.SocLabel.configure(activebackground="#f9f9f9")
        self.SocLabel.configure(activeforeground="black")
        self.SocLabel.configure(background="#eaeaea")
        self.SocLabel.configure(disabledforeground="#a3a3a3")
        self.SocLabel.configure(foreground="#000000")
        self.SocLabel.configure(highlightbackground="#d9d9d9")
        self.SocLabel.configure(highlightcolor="black")
        self.SocLabel.configure(text='''Soc (Ah/%) :''')

        self.SocAh = Label(self.LabelframeGeneral)
        self.SocAh.place(relx=0.31, rely=0.28, height=21, width=45)
        self.SocAh.configure(activebackground="#f9f9f9")
        self.SocAh.configure(activeforeground="black")
        self.SocAh.configure(background="#eaeaea")
        self.SocAh.configure(disabledforeground="#a3a3a3")
        self.SocAh.configure(foreground="#000000")
        self.SocAh.configure(highlightbackground="#d9d9d9")
        self.SocAh.configure(highlightcolor="black")
        self.SocAh.configure(text='''1000Ah''')

        self.BarraProgresoSoc = ttk.Progressbar(self.LabelframeGeneral)
        self.BarraProgresoSoc.place(relx=0.52, rely=0.28, relwidth=0.34
                , relheight=0.0, height=22)

        self.SocPorcentaje = Label(self.LabelframeGeneral)
        self.SocPorcentaje.place(relx=0.86, rely=0.28, height=21, width=32)
        self.SocPorcentaje.configure(activebackground="#f9f9f9")
        self.SocPorcentaje.configure(activeforeground="black")
        self.SocPorcentaje.configure(background="#eaeaea")
        self.SocPorcentaje.configure(disabledforeground="#a3a3a3")
        self.SocPorcentaje.configure(foreground="#000000")
        self.SocPorcentaje.configure(highlightbackground="#d9d9d9")
        self.SocPorcentaje.configure(highlightcolor="black")
        self.SocPorcentaje.configure(text='''0%''')
        self.SocPorcentaje.configure(width=32)

        self.SetVelocityPorcentaje = Label(self.LabelframeGeneral)
        self.SetVelocityPorcentaje.place(relx=0.86, rely=0.13, height=21
                , width=32)
        self.SetVelocityPorcentaje.configure(activebackground="#f9f9f9")
        self.SetVelocityPorcentaje.configure(activeforeground="black")
        self.SetVelocityPorcentaje.configure(background="#eaeaea")
        self.SetVelocityPorcentaje.configure(disabledforeground="#a3a3a3")
        self.SetVelocityPorcentaje.configure(foreground="#000000")
        self.SetVelocityPorcentaje.configure(highlightbackground="#d9d9d9")
        self.SetVelocityPorcentaje.configure(highlightcolor="black")
        self.SetVelocityPorcentaje.configure(text='''0%''')
        self.SetVelocityPorcentaje.configure(width=32)

        self.SetCurrentPorcentaje = Label(self.LabelframeGeneral)
        self.SetCurrentPorcentaje.place(relx=0.86, rely=0.18, height=21
                , width=32)
        self.SetCurrentPorcentaje.configure(activebackground="#f9f9f9")
        self.SetCurrentPorcentaje.configure(activeforeground="black")
        self.SetCurrentPorcentaje.configure(background="#eaeaea")
        self.SetCurrentPorcentaje.configure(disabledforeground="#a3a3a3")
        self.SetCurrentPorcentaje.configure(foreground="#000000")
        self.SetCurrentPorcentaje.configure(highlightbackground="#d9d9d9")
        self.SetCurrentPorcentaje.configure(highlightcolor="black")
        self.SetCurrentPorcentaje.configure(text='''0%''')
        self.SetCurrentPorcentaje.configure(width=32)

        self.SetBusPorcentaje = Label(self.LabelframeGeneral)
        self.SetBusPorcentaje.place(relx=0.86, rely=0.23, height=21, width=32)
        self.SetBusPorcentaje.configure(activebackground="#f9f9f9")
        self.SetBusPorcentaje.configure(activeforeground="black")
        self.SetBusPorcentaje.configure(background="#eaeaea")
        self.SetBusPorcentaje.configure(disabledforeground="#a3a3a3")
        self.SetBusPorcentaje.configure(foreground="#000000")
        self.SetBusPorcentaje.configure(highlightbackground="#d9d9d9")
        self.SetBusPorcentaje.configure(highlightcolor="black")
        self.SetBusPorcentaje.configure(text='''0%''')
        self.SetBusPorcentaje.configure(width=32)

        self.POTENCIA = Label(self.LabelframeGeneral)
        self.POTENCIA.place(relx=0.55, rely=0.065, height=38, width=111)
        self.POTENCIA.configure(activebackground="#ffffff")
        self.POTENCIA.configure(activeforeground="black")
        self.POTENCIA.configure(background="#eaeaea")
        self.POTENCIA.configure(disabledforeground="#a3a3a3")
        self.POTENCIA.configure(font=font11)
        self.POTENCIA.configure(foreground="#000000")
        self.POTENCIA.configure(highlightbackground="#eaeaea")
        self.POTENCIA.configure(highlightcolor="black")
        self.POTENCIA.configure(text='''0W''')

        self.menubar = Menu(self.top,font=font9,bg=_bgcolor,fg=_fgcolor)
        self.top.configure(menu = self.menubar)

        ##########################################################################

        ##########################################################################

        #Asignación inicial del tamaño de la tabla de la Batería
        Tabla(self.LabelframeBateria, 9,12)

        set(self.LabelframeBateria, 0, 1, "Serial")
        set(self.LabelframeBateria, 0, 2, "PCB ºC")
        set(self.LabelframeBateria, 0, 3, "Cell ºC")
        set(self.LabelframeBateria, 0, 4, "Cell 0 mV")
        set(self.LabelframeBateria, 0, 5, "Cell 1 mV")
        set(self.LabelframeBateria, 0, 6, "Cell 2 mV")
        set(self.LabelframeBateria, 0, 7, "Cell 3 mV")
        set(self.LabelframeBateria, 0, 8, "Cell 4 mV")
        set(self.LabelframeBateria, 0, 9, "Cell 5 mV")
        set(self.LabelframeBateria, 0, 10, "Cell 6 mV")
        set(self.LabelframeBateria, 0, 11, "Cell 7 mV")

        #Paneles
        path = r"Panel.png"
        filename = PhotoImage(file= path)
        self.background_label = Label(self.Frame1, image=filename)
        self.background_label.image = filename
        self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        #Alerta de Paneles
        path0 = "PanelAlert.gif"
        filename0 = PhotoImage(file= path0, format="gif")
        self.background_label0 = Label(self.Frame2, image=filename0)
        self.background_label0.image = filename0
        self.background_label0.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.background_label0.pack()


        self.background_label1 = Label(self.Frame3, image=filename)
        self.background_label1.image = filename
        self.background_label1.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.frames = [PhotoImage(file='PanelAlert.gif',format = 'gif -index %i' %(i)) for i in range(4)]

        ########################
        ####Gráfico de GPS######
        ########################

        archivo=filedialog.askopenfilename()
        self.dato, self.gps=open_file(archivo)
        self.dato2 = self.dato
        self.gps2 = self.gps

        #se crea la figura con un color de fondo
        self.f = plt.figure(figsize=(5, 4), dpi=100, facecolor = (0.9294,0.9137,0.8667))
        self.a = self.f.add_subplot(111)

        

        #se grafica la ruta y los marker del gps
        #self.x = np.arange(len(self.gps[:,2]))
        plt.plot(self.gps[:,3], self.gps[:,2], color=(0, 0.7, 0.2))
        plt.fill_between(self.gps[:,3], self.gps[:,2], np.min(self.gps[:,2]),color=(0.5,0,0,0.5))
        #marcar gps
        self.p = gpsVsPosiciones(self.gps, self.gps[0][0], self.gps[0][1])

        self.error = plt.plot(self.gps[self.p][3], self.gps[self.p][2], marker='o', color=(0.1647,0.4157,1, 0.5), markersize=20)
        self.posicion = plt.plot(self.gps[self.p][3], self.gps[self.p][2], marker='o', color=(0.1647,0.4157,1), markersize=6)

        self.a.grid(True) #crear grid
        self.a.set_title('Grafico de Perfil')


        # a tk.DrawingArea para el 1er Grafico de latitud VS altitud
        self.canvas = FigureCanvasTkAgg(self.f, self.LabelLatitudLongitud)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        #self.canvas.configure(width=760)


        #se crea la figura con un color de fondo
        self.fun = plt.figure(figsize=(5, 4), dpi=100,facecolor = (0.9294,0.9137,0.8667))
        self.range = self.fun.add_subplot(111)

        #se grafica la ruta y los marker del gps2
        plt.plot(self.gps2[:,1], self.gps2[:,0], color=(0, 0.7, 0.2))

        #marcar gps2
        self.error2 = plt.plot(self.gps2[0][1], self.gps2[0][0], marker='o', color=(0.1647,0.4157,1, 0.5), markersize=20)
        self.posicion2 = plt.plot(self.gps2[0][1], self.gps2[0][0], marker='o', color=(0.1647,0.4157,1), markersize=6)

        self.range.grid(True) #crear grid
        plt.title('Ruta de carrera')

        self.canvasGPS = FigureCanvasTkAgg(self.fun, self.LabelGPS)
        self.canvasGPS.show()
        self.canvasGPS.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvasGPS._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        
        #self.inicia = -1

        self.Button1 = Button(self.LabelGPS, command= lambda: abrir(self.f,self.a,self.p,self.error,self.posicion,self.canvas))
        self.Button1.place(relx=0.84, rely=0.94, height=24, width=115)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#eaeaea")
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''Seleccionar Archivo''')


        #######################################
        #########Iniciando Oberserver##########
        #######################################
        self.batObserver = BateriasObserver()
        self.drvObserver = ControladorObserver()
        self.motObserver = MotorObserver()

        self.mpptObserver = mpptObservable()
        self.gpsObserver = gpsObservable()
        self.botObserver = botonesObservable()

        self.drvObserver.connect()#inicia la comunicación con el cambus


        ## Inicializando variables del Motor observado
        self.motorActivo= 0
        self.mcurrent = 0
        self.mvoltage = 0
        self.mvelocidad = 0
        self.mRPM = 0
        self.mphaseC = 0
        self.mphaseB = 0
        self.mvoltage_1= 0
        self.mvoltage_2= 0
        self.mvoltage_3= 0
        self.mvoltage_4= 0
        self.mTmotor= 0
        self.mTDSP= 0
        self.mOdo= 0
        self.mAH= 0    
        
        ## Inicializando variables de las Baterias observadas
        self.bCB1 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bCB2 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bCB3 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bCB4 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bCB5 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bCB6 = {'SN':'0','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
        self.bSOCah = 0.0
        self.bSOCp = 0.0

        self.bminVolt = { 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
        self.bmaxVolt = { 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
        self.bminTemp = { 'mT': 0.0, 'CMUNumber':0}
        self.bmaxTemp = { 'mT': 0.0, 'CMUNumber':0}


        ## Inicializando variables del controlador observadas
        self.creverse = False
        self.cneutral = False
        self.cregen = False
        self.cdrive = False
        self.caccesories = False
        self.crun = False
        self.cstart = False
        self.cbrakes = False
        self.cfueldoor = False
        self.cspCurrent = 0.0
        self.cspBusCurrent = 0.0
        self.cspVelocity = 0.0 


        ##Inicializando variables del Mppt observadas
        self.mVin       = 0.0
        self.mIin       = 0.0
        self.mVout      = 0.0
        self.mbulr      = 0.0
        self.mout       = 0.0
        self.mnoe       = 0.0
        self.mundv      = 0.0
        self.mt         = 0.0
        #estructura extra
        self.mt1        = 0.0
        self.mt2        = 0.0
        self.mcorriente = 0.0

        ##Inicializando variables del GPS observadas
        self.glat        = self.gps[0][0] #latitud:float
        self.glon        = self.gps[0][1] #longitud:float
        self.galt        = 0.0 #altitud:float
        self.gerr        = 0 #error[metros]:int
        self.glastUpdate = datetime.fromtimestamp(0.0)#ultima vez actualizado:datetime
        self.gheading    = 0.0 #grados de inclinacion respecto de la direccion[grados]:float

        ##Inicializando variables de botones observados
        self.bmppt      = False#int 32 //flag
        self.bpan1      = False
        self.bpan2      = False
        self.bpan3      = False
        self.blucesAl   = False# int 32 //flag
        self.blucesBa   = False
        self.blucesEm   = False
        self.bfan       = 0#int 32 //[0-255]
        self.bbateria   = False# int 32 //flag



        self.clock()

if __name__ == '__main__':
    vp_start_gui()