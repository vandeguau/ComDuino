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
        while not exit_flag.is_set():
            data = ser.readline().decode('utf-8').strip()
            tiempo, valor = data.split(',')

            print(f"Tiempo: {tiempo}, {valor_medido}: {valor}")

            tiempo_data.append(float(tiempo))
            valor_data.append(float(valor))
            
            with open('data.csv', 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([tiempo, valor])

            # Actualiza la gráfica
            ax.clear()
            ax.plot(tiempo_data, valor_data, 'b-')
            ax.set_xlabel('Tiempo')
            ax.set_ylabel(valor_medido)
            ax.set_title(f'Gráfica de {valor_medido}')
            canvas.draw()
    
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

def detener_adquisicion():
    exit_flag.set()
    ser.close()

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
    if 'csvfile' in locals() and not csvfile.closed:
        csvfile.close()

    root.destroy()  # Cierra la ventana y termina la aplicación
    sys.exit()




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
canvas.get_tk_widget().grid(row=0, column=2, rowspan=6, padx=10, pady=10)

exit_flag = threading.Event()
adquisicion_thread = None

# Coloca los elementos en la ventana
puerto_com_label.grid(row=0, column=0, padx=10, pady=10)
puerto_com_combobox.grid(row=0, column=1, padx=10, pady=10)

refrescar_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

vel_comunicacion_label.grid(row=2, column=0, padx=10, pady=10)
vel_comunicacion_entry.grid(row=2, column=1, padx=10, pady=10)

valor_medido_label.grid(row=3, column=0, padx=10, pady=10)
valor_medido_entry.grid(row=3, column=1, padx=10, pady=10)

reiniciar_button.grid(row=4, column=0,  columnspan=2,padx=10, pady=10)

iniciar_button.grid(row=5, column=0, padx=10, pady=10)
desconectar_button.grid(row=5, column=1, padx=10, pady=10)



# Inicia la aplicación
root.mainloop()
