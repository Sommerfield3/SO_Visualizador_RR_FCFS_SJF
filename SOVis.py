import psutil
import tkinter as tk
from tkinter import ttk
import datetime
import time
import random
import threading

event_FCFS = threading.Event()
event_SJF = threading.Event()
event_RR = threading.Event()

def obtener_info_procesos():
    procesos = []
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            pid = p.pid
            nombre = p.name()
            usuario = p.username().split('\\')[-1]  # En Windows, los nombres de usuario pueden incluir el dominio
            memoria = p.memory_info().rss
            tiempo_llegada = random.randint(1, 5)
            tiempo_creacion = p.create_time()
            tiempo_ejecucion = time.time() - tiempo_creacion
            tiempo_ejecucion = round(tiempo_ejecucion, 8)
            #tiempo_cpu_antes = p.cpu_times()
            #tiempo_cpu_despues = p.cpu_times()
            #tiempo_rafaga = tiempo_cpu_despues.user - tiempo_cpu_antes.user
            tiempo_rafaga = random.randint(1, 180)
            procesos.append((pid, nombre, usuario, memoria, tiempo_llegada, tiempo_ejecucion, tiempo_rafaga))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return procesos
def filtro(resul):
    final=[]
    for elem in resul:
        #if elem[5]<1000:
            #final.append(elem)
        if elem[5]<14000:
            final.append(elem)
    return final

def filtro2():
    # Obtener todos los procesos
    todos_los_procesos = obtener_info_procesos()
    data_final=filtro(todos_los_procesos)

    # Extraer solo el nombre y el tiempo de llegada de cada proceso
    nombre_tiempo_llegada = [(proceso[1], proceso[4]) for proceso in data_final]
    
    return nombre_tiempo_llegada

 #Función para actualizar los datos mostrados
def actualizar_datos():
    # Eliminar los datos existentes
    for i in tree.get_children():
        tree.delete(i)
    # Obtener los nuevos datos de los procesos
    
    procesos_origin = obtener_info_procesos()
    procesos = filtro(procesos_origin)

    # Añadir nuevos datos al Treeview
    for proceso in procesos:
        tree.insert('', 'end', values=proceso)

    # Programar la siguiente actualización
    ventana.after(5000, actualizar_datos)  # actualizar cada 5 segundos

#/////////////////////////////////////////////////////////////////////////////////////////////VISUALIZADOR////////////////////////////////////////////////////////////////////////
ventana = tk.Tk()
ventana.geometry("1200x600")
ventana.title("Información de Procesos")

# Crear el Treeview
tree = ttk.Treeview(ventana, columns=('PID', 'Nombre', 'Usuario', 'Memoria','Tiempollegada','Tiempoejecucion','Tiemporafaga'), show='headings')
tree.heading('PID', text='PID')
tree.heading('Nombre', text='Nombre')
tree.heading('Usuario', text='Usuario')
tree.heading('Memoria', text='Memoria (bytes)')
tree.heading('Tiempollegada',text='Tiempo llegada')
tree.heading('Tiempoejecucion',text='Tiempo ejecucion')
tree.heading('Tiemporafaga',text='Tiempo rafaga')
#definimos las columnas
tree.column('PID', width=40, minwidth=5)
tree.column('Nombre', width=100, minwidth=50)
tree.column('Usuario', width=120, minwidth=50)
tree.column('Memoria', width=120, minwidth=40)
tree.column('Tiempollegada', width=140, minwidth=50)
tree.column('Tiempoejecucion', width=160, minwidth=50)
tree.column('Tiemporafaga', width=120, minwidth=50)

#dimensiones del treeview
tree.place(x=0, y=0, width=800, height=500)

# Botón para actualizar manualmente
boton_actualizar = tk.Button(ventana, text="Actualizar", command=actualizar_datos)
boton_actualizar.pack()
boton_actualizar.place(x=0,y=510,width=70,height=25)

#nuevos colas de procesos//////////////////////////////////
labelprolist = tk.Label(ventana,text="Procesos listados")
labelprolist.place(x=805,y=0,width=330,height=20)#inicia en la esquina superior de y=0)
#BOX
prolist = tk.Listbox(ventana, width=20, height=10) 
prolist.place(x=805,y=20,width=380,height=100)
#Procesos registrados///////////////////////////
labelschel = tk.Label(ventana, text="Registro de Procesos")
labelschel.place(x=805,y=125,width=330,height=20)
#BOX
schel = tk.Listbox(ventana, width=20, height=10)  # 20 caracteres de ancho, 10 líneas de alto
schel.place(x=805,y=150,width=380,height=100)
#////////////FUNCIONALIDAD FCFS, SJF, Round Robin///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def fcfs():
    global event_FCFS, event_SJF, event_RR
    event_SJF.clear()
    event_RR.clear()
    event_FCFS.set()
    # Limpiar las Listbox
    prolist.delete(0, tk.END)
    #prores.delete(0,tk.END)
    schel.delete(0, tk.END)
    # Obtener y filtrar los procesos
    procesos = filtro(obtener_info_procesos())
    for proceso in procesos:
        prolist.insert(tk.END, f"{proceso[1]} (PID: {proceso[0]}) Tiempo de llegada: {proceso[4]}")
    # Ordenar los procesos por su tiempo de llegada
    procesos_ordenados = sorted(procesos, key=lambda x: x[4])  # x[4] es el tiempo de llegada
    def simular_ejecucion():
        # Simular la ejecución de cada proceso
        while event_FCFS.is_set(): #verificar
            for proceso in procesos_ordenados:
                # Aquí puedes simular la ejecución, por ejemplo, imprimiendo información del proceso
                schel.insert(tk.END, f"Procesando {proceso[1]} (PID: {proceso[0]}) - Tiempo de llegada: {proceso[4]}")
                time.sleep(1)  # Simular un tiempo de ejecución para cada proceso
    thread_fcfs = threading.Thread(target=simular_ejecucion)
    thread_fcfs.start()
    print("Todos los procesos han sido ejecutados con FCFS.")

def sjf():
    global event_FCFS, event_SJF, event_RR
    event_FCFS.clear()
    event_RR.clear()
    event_SJF.set()
    # Limpiar las Listbox
    prolist.delete(0, tk.END)
    #prores.delete(0,tk.END)
    schel.delete(0, tk.END)
    # Obtener y filtrar los procesos
    procesos = filtro(obtener_info_procesos())
    for proceso in procesos:
        prolist.insert(tk.END, f"{proceso[1]} (PID: {proceso[0]}) Rafaga de: {proceso[6]} segundo(s)")
    # Ordenar los procesos por su duración estimada
    # Aquí estoy asumiendo que la duración está en una posición específica de la tupla del proceso
    procesos_ordenados = sorted(procesos, key=lambda x: x[6])
    def simular_ejecucion2():
        while event_SJF.is_set(): ##verificar
            # Simular la ejecución de cada proceso
            for proceso in procesos_ordenados:
                # Simular la ejecución, por ejemplo, imprimiendo información del proceso
                schel.insert(tk.END, f"Procesando {proceso[1]} (PID: {proceso[0]}) - Duración estimada: {proceso[6]}")
                # Puedes incluir una espera o lógica para simular la ejecución del proceso
                time.sleep(1)  # Simular un tiempo de ejecución para cada proceso

    thread_sjf = threading.Thread(target=simular_ejecucion2)
    thread_sjf.start()
    print("Todos los procesos han sido ejecutados con SJF.")

def round_robin():
    global event_FCFS, event_SJF, event_RR
    event_FCFS.clear()
    event_SJF.clear()
    event_RR.set()
    # Limpiar las Listbox
    prolist.delete(0, tk.END)
    #prores.delete(0,tk.END)
    schel.delete(0, tk.END)
    quantum = 3  # Establece el quantum de tiempo
    procesos = [list(proceso) for proceso in filtro(obtener_info_procesos())]  # Convertir tuplas a listas
    for proceso in procesos:
        prolist.insert(tk.END, f"{proceso[1]} (PID: {proceso[0]}) Rafaga de: {proceso[6]} segundo(s)")
    def simular_ejecucion3():
        while event_RR.is_set(): ##verificar
            while procesos:
                for proceso in procesos.copy():
                    schel.insert(tk.END, f"Procesando {proceso[1]} (PID: {proceso[0]}) por {quantum} segundo(s)")
                    proceso[6] -= quantum  # Disminuir el tiempo restante del proceso

                    if proceso[6] <= 0:
                        schel.insert(tk.END, f"Proceso {proceso[1]} (PID: {proceso[0]}) completado")
                        procesos.remove(proceso)
                    else:
                        # Mover el proceso al final de la cola
                        procesos.append(procesos.pop(0))

                    time.sleep(quantum)  # Esperar el tiempo del quantum

            print("Todos los procesos han sido ejecutados con Round Robin.")
    thread_RR = threading.Thread(target=simular_ejecucion3)
    thread_RR.start()
#BOTON FCFS
boton_fcfs2 =tk.Button(ventana, text='FCFS',command=fcfs)
boton_fcfs2.pack()
boton_fcfs2.place(x=80,y=510,width=70,height=25)
boton_sjf = tk.Button(ventana, text='SJF', command=sjf)
boton_sjf.pack()
boton_sjf.place(x=160, y=510, width=70, height=25)
boton_rr = tk.Button(ventana, text='Round Robin', command=round_robin)
boton_rr.pack()
boton_rr.place(x=240, y=510, width=100, height=25)
actualizar_datos()# Iniciar la actualización automática
ventana.mainloop()##Ciclamos
