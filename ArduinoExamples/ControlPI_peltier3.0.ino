#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
#define BOTON_PIN 16
#define ACTIVAR_PIN_D1 5
#define ACTIVAR_PIN_D2 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

int estado_planta = 0;
unsigned long tiempo_inicial = 0;
int estado_anterior_boton = HIGH;
bool conteo_iniciado = false;

float setpoint = 10; // Variable para almacenar el setpoint recibido
float kp = -397.16;
float ti = -4.433;


float error_previo = 0;
float suma_errores = 0;

void setup() {
  Serial.begin(9600);
  sensors.begin();
  pinMode(ACTIVAR_PIN_D1, OUTPUT);
  pinMode(ACTIVAR_PIN_D2, OUTPUT);
  pinMode(BOTON_PIN, INPUT_PULLUP);

}

void loop() {

  int estado_boton = digitalRead(BOTON_PIN);
  sensors.requestTemperatures();

  if (estado_boton == LOW && estado_anterior_boton == HIGH) {
    tiempo_inicial = millis();
    conteo_iniciado = true;
    estado_planta = 0;
  }
  estado_anterior_boton = estado_boton;
  
  if (Serial.available() > 0) {
    String data_received = Serial.readStringUntil('\n');
    int comma_index = data_received.indexOf(',');
    if (comma_index != -1) {
      String setpoint_str = data_received.substring(0, comma_index);
        int second_comma_index = data_received.indexOf(',', comma_index + 1);
        if (second_comma_index != -1) {
            String kp_str = data_received.substring(comma_index + 1, second_comma_index);
            String ti_str = data_received.substring(second_comma_index + 1);
            
            setpoint = setpoint_str.toFloat();
            kp = kp_str.toFloat();
            ti = ti_str.toFloat();
            
            // Utiliza los valores de setpoint, kp y ti en tu lógica de control aquí
            // Por ejemplo, podrías ajustar el comportamiento del sistema usando estos valores.
            // ...
        }
    }
  }
  
  if (conteo_iniciado) {
    unsigned long tiempo_transcurrido = (millis() - tiempo_inicial) / 1000;
    if (tiempo_transcurrido >= 23) {
      estado_planta = 1;
    }
    float temperatura_actual = sensors.getTempCByIndex(0);
    float error = setpoint - temperatura_actual;
    
    suma_errores += error;

    // Control PI
    float potencia = kp * error + ti * suma_errores;

    // Limitar la potencia para evitar valores extremos
    if (potencia > 255) {
      potencia = 255;
    } else if (potencia < 0) {
      potencia = 0;
    }

    // Actualización de variables para la próxima iteración
    error_previo = error;

    Serial.print(tiempo_transcurrido);
    Serial.print(",");//
    Serial.print(temperatura_actual);
    Serial.println();

    
    if (estado_planta == 1) {
      analogWrite(ACTIVAR_PIN_D1, potencia); // Aplicar la potencia a la celda Peltier
      digitalWrite(ACTIVAR_PIN_D2, HIGH);
    } else {
      analogWrite(ACTIVAR_PIN_D1,0); // Aplicar la potencia a la celda Peltier
      digitalWrite(ACTIVAR_PIN_D2, LOW);
    }
  }

  delay(500);
}
