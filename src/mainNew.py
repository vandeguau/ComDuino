import serial
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from serial.tools import list_ports
import threading
import sys 

# Inicializa el puerto serie
ser = None

def obtener_puertos_com():
    return [port.device for port in list_ports.comports()]

def refrescar_puertos_com():
    puertos_com = obtener_puertos_com()
    puerto_com_combobox['values'] = puertos_com
    # Seleccionar el primer puerto de la lista (o cualquier comportamiento que desees)
    if puertos_com:
        puerto_com_var.set(puertos_com[0])

# Función para abrir el puerto serie
def abrir_puerto_serie(puerto_com, baudios):
    global ser
    ser = serial.Serial(puerto_com, baudios)
    estado_conexion_var.set("Conectado")



# Agrega una función para crear y escribir en el archivo CSV
def escribir_csv(nombre_archivo, encabezados, datos):
    with open(nombre_archivo, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(encabezados)
        csvwriter.writerows(datos)

# Función para iniciar la adquisición de datos en un hilo separado
def iniciar_adquisicion():
    # Obtiene los valores seleccionados por el usuario
    puerto_com = puerto_com_var.get()
    valor_medido = valor_medido_var.get()
    baudios = vel_comunicacion_var.get()

    # Abre el puerto serie
    abrir_puerto_serie(puerto_com, baudios)

    # Inicializa las listas para almacenar los datos
    tiempo_data = []  # Almacena el tiempo proporcionado por Arduino
    valor_data = []  # Almacena el valor medido

    try:
        setpoint = float(setpoint_entry.get())  # Obtiene el valor del Setpoint como un número
        
        while not exit_flag.is_set():
            data = ser.readline().decode('utf-8').strip()
            tiempo, valor = data.split(',')
            actualizar_temperatura(valor)
            
            print(f"Tiempo: {tiempo}, {valor_medido}: {valor}")

            tiempo_data.append(float(tiempo))
            valor_data.append(float(valor))
            
            with open('data.csv', 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([tiempo, valor])

            setpoint_actual = float(setpoint_entry.get())
            if setpoint_actual != setpoint_anterior:
                setpoint_anterior = setpoint_actual
                ax.plot(tiempo_data, [setpoint_actual] * len(tiempo_data), 'y--', label='Setpoint')
                ax.legend()
                canvas.draw()


            # Actualiza la gráfica
            ax.clear()
            ax.plot(tiempo_data, valor_data, 'b-', label=f'{valor_medido}')  # Línea azul para los datos medidos
            ax.plot(tiempo_data, [setpoint] * len(tiempo_data), 'y--', label='Setpoint')  # Línea amarilla para el Setpoint
            ax.set_xlabel('Tiempo')
            ax.set_ylabel(valor_medido)
            ax.set_title(f'Gráfica de {valor_medido}')
            ax.legend()  # Muestra la leyenda en el gráfico
            
            canvas.draw()
    
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()


def detener_adquisicion():
    exit_flag.set()
    ser.close()
    estado_conexion_var.set("Desconectado")

def pausar_adquisicion():
    exit_flag.set()
    ser.close()

def reiniciar_grafico():
    ax.clear()
    ax.set_xlabel('Tiempo')
    ax.set_ylabel(valor_medido_var.get())
    ax.set_title(f'Gráfica de {valor_medido_var.get()}')
    canvas.draw()

def desconectar_equipo():
    ser.close()
    estado_conexion_var.set("Desconectado")

# Función para iniciar la adquisición en un hilo
def iniciar_adquisicion_thread():
    global adquisicion_thread
    adquisicion_thread = threading.Thread(target=iniciar_adquisicion)
    adquisicion_thread.start()

def on_cerrar_ventana():
    global adquisicion_thread
    if adquisicion_thread:
        exit_flag.set()  # Establece la bandera para detener el hilo
        adquisicion_thread.join()  # Espera a que el hilo termine

    if ser and ser.is_open:
        ser.close()  # Cierra el puerto serie si está abierto

    # Cierra el archivo CSV si está abierto
    #if 'csvfile' in locals() and not csvfile.closed:
    #    csvfile.close()

    root.destroy()  # Cierra la ventana y termina la aplicación
    sys.exit()

def enviar_datos_arduino(setpoint, kp,ti):
    if ser and ser.is_open:
        data_to_send = f"{setpoint},{kp},{ti}\n"  # Formato: setpoint,ganancia
        ser.write(data_to_send.encode())


def actualizar_temperatura(temperatura):
    temperatura_actual_var.set(temperatura)

# Agregar una función para enviar setpoint y ganancia al Arduino
def enviar_setpoint_ganancia():
    setpoint = setpoint_entry.get()
    
    kp= kp_entry.get()
    ti= ti_entry.get()
    enviar_datos_arduino(setpoint,kp,ti)



# Crea la ventana de la interfaz de usuario
root = tk.Tk()
root.title('Adquisición de Datos')

root.protocol("WM_DELETE_WINDOW", on_cerrar_ventana)

# Obtiene la lista de puertos COM disponibles
puertos_com = obtener_puertos_com()

# Variables de control para las opciones seleccionadas por el usuario
puerto_com_var = tk.StringVar()
vel_comunicacion_var = tk.StringVar(value="9600")
valor_medido_var = tk.StringVar()

# Etiqueta y lista desplegable para seleccionar el puerto COM
puerto_com_label = ttk.Label(root, text='Puerto COM:')
puerto_com_combobox = ttk.Combobox(root, textvariable=puerto_com_var, values=puertos_com)

# Etiqueta y entrada de texto para la velocidad de comunicación
vel_comunicacion_label = ttk.Label(root, text='Velocidad Com:')
vel_comunicacion_entry = ttk.Entry(root, textvariable=vel_comunicacion_var)

# Etiqueta y entrada de texto para el valor medido
valor_medido_label = ttk.Label(root, text='Valor Medido:')
valor_medido_entry = ttk.Entry(root, textvariable=valor_medido_var)

# Botón para iniciar la adquisición de datos
iniciar_button = ttk.Button(root, text='Iniciar Adquisición', command=iniciar_adquisicion_thread)

# Botón para desconectar el equipo
desconectar_button = ttk.Button(root, text='Desconectar Equipo', command=desconectar_equipo)

reiniciar_button = ttk.Button(root, text='Reiniciar Grafico', command=reiniciar_grafico)

#Boton refrescar
refrescar_button = ttk.Button(root, text='Refrescar Puertos COM', command=refrescar_puertos_com)

# Configura la gráfica
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=2, rowspan=12, padx=10, pady=10)

exit_flag = threading.Event()
adquisicion_thread = None

# Coloca los elementos en la ventana
puerto_com_label.grid(row=0, column=0, padx=10, pady=10)
puerto_com_combobox.grid(row=0, column=1, padx=10, pady=10)

refrescar_button.grid(row=1, column=1, columnspan=1, padx=10, pady=10)

vel_comunicacion_label.grid(row=2, column=0, padx=10, pady=10)
vel_comunicacion_entry.grid(row=2, column=1, padx=10, pady=10)

valor_medido_label.grid(row=3, column=0, padx=10, pady=10)
valor_medido_entry.grid(row=3, column=1, padx=10, pady=10)

# Dentro de la sección donde se define la interfaz gráfica
setpoint_label = ttk.Label(root, text='Setpoint:')
setpoint_entry = ttk.Entry(root)
setpoint_label.grid(row=4, column=0, padx=10, pady=10)
setpoint_entry.grid(row=4, column=1, padx=10, pady=10)

kp_label = ttk.Label(root, text='KP:')
kp_entry = ttk.Entry(root)
kp_label.grid(row=5, column=0, padx=10, pady=10)
kp_entry.grid(row=5, column=1, padx=10, pady=10)
ti_label = ttk.Label(root, text='TI:')
ti_entry = ttk.Entry(root)
ti_label.grid(row=6, column=0, padx=10, pady=10)
ti_entry.grid(row=6, column=1, padx=10, pady=10)

temperatura_actual_label = ttk.Label(root, text='Valor Actual:')
temperatura_actual_var = tk.StringVar()
temperatura_actual_display = ttk.Label(root, textvariable=temperatura_actual_var)
temperatura_actual_label.grid(row=7, column=0, padx=10, pady=10)
temperatura_actual_display.grid(row=7, column=1, padx=10, pady=10)

# En la sección donde se definen los botones y la lógica de la interfaz
enviar_button = ttk.Button(root, text='Enviar Setpoint y Ganancia', command=enviar_setpoint_ganancia)
enviar_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

reiniciar_button.grid(row=8, column=1,  columnspan=2,padx=10, pady=10)

iniciar_button.grid(row=9, column=0, padx=10, pady=10)
desconectar_button.grid(row=9, column=1, padx=10, pady=10)




estado_conexion_var = tk.StringVar()
estado_conexion_label = ttk.Label(root, textvariable=estado_conexion_var, relief='sunken')
estado_conexion_var.set("Desconectado")  # Inicialmente establecido como desconectado
estado_conexion_label.grid(row=11, column=0, columnspan=2, sticky='we', padx=10, pady=10)



# Inicia la aplicación
root.mainloop()
