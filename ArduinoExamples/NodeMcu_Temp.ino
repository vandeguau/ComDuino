//Se utiliza la placa NodeMcu Amica para medir temperatura mediante un sensor de temperatura DS18B20

#include <OneWire.h>
#include <DallasTemperature.h>

// Pin D4 del NodeMCU para el sensor DS18B20
#define ONE_WIRE_BUS 2

// Pin D0 del NodeMCU para el botón (con resistencia pull-up interna)
#define BOTON_PIN 16

// Pin D1 y D2 del NodeMCU para activar cuando el estado de la planta sea 1
#define ACTIVAR_PIN_D1 5
#define ACTIVAR_PIN_D2 4

// Setup de una instancia OneWire para comunicarse con dispositivos OneWire
OneWire oneWire(ONE_WIRE_BUS);

// Paso de la referencia oneWire al sensor Dallas Temperature
DallasTemperature sensors(&oneWire);

// Variable para almacenar el estado de la planta (0: apagada, 1: encendida)
int estado_planta = 0;

// Variable para almacenar el estado anterior del botón
int estado_anterior_boton = HIGH;

void setup() {
  // Inicia la comunicación con el sensor DS18B20
  sensors.begin();

  // Configura el botón como entrada con resistencia pull-up
  pinMode(BOTON_PIN, INPUT_PULLUP);

  // Configura los pines D1 y D2 como salidas
  pinMode(ACTIVAR_PIN_D1, OUTPUT);
  pinMode(ACTIVAR_PIN_D2, OUTPUT);

  Serial.begin(9600);
  Serial.println("Tiempo,Temperatura (C),Estado Planta");

  // Puedes agregar otras configuraciones según sea necesario
}

void loop() {
  // Solicita la temperatura al DS18B20
  sensors.requestTemperatures();
  
  // Lee la temperatura en grados Celsius
  float temperatura = sensors.getTempCByIndex(0);

  // Lee el estado actual del botón (LOW cuando se presiona debido a la resistencia pull-up)
  int estado_boton = digitalRead(BOTON_PIN);

  // Verifica si el estado del botón ha cambiado
  if (estado_boton == LOW && estado_anterior_boton == HIGH) {
    // Invierte el estado de la planta si el botón se ha presionado
    estado_planta = 1 - estado_planta;
   // Para evitar rebotes, espera medio segundo antes de considerar otro cambio
  }

  // Almacena el estado actual del botón para la próxima iteración
  estado_anterior_boton = estado_boton;

  // Imprime la temperatura, el tiempo y el estado de la planta
  Serial.print(millis() / 1000); // Tiempo en segundos
  Serial.print(",");
  Serial.print(temperatura); // Temperatura en grados Celsius
  //Serial.print(",");
  //Serial.print(estado_planta); // Estado de la planta (0 o 1)
  Serial.println();

  // Activa los pines D1 y D2 si el estado de la planta es 1
  if (estado_planta == 1) {
    digitalWrite(ACTIVAR_PIN_D1, HIGH);
    digitalWrite(ACTIVAR_PIN_D2, HIGH);
  } else {
    // Desactiva los pines D1 y D2 si el estado de la planta es 0
    digitalWrite(ACTIVAR_PIN_D1, LOW);
    digitalWrite(ACTIVAR_PIN_D2, LOW);
  }

  // Puedes agregar otro código aquí según sea necesario

  delay(500); // Retraso de 1 segundo antes de la siguiente lectura
}
