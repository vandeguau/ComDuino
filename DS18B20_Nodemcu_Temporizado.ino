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

void setup() {
  sensors.begin();
  pinMode(ACTIVAR_PIN_D1, OUTPUT);
  pinMode(ACTIVAR_PIN_D2, OUTPUT);
  pinMode(BOTON_PIN, INPUT_PULLUP);

  Serial.begin(9600);
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

  if (conteo_iniciado) {
    unsigned long tiempo_transcurrido = (millis() - tiempo_inicial) / 1000;
    if (tiempo_transcurrido >= 23) {
      estado_planta = 1;
    }
    Serial.print(tiempo_transcurrido);
    Serial.print(",");
    Serial.print(sensors.getTempCByIndex(0));
    //Serial.print(",");
    //Serial.println(estado_planta);
    Serial.println();

    if (estado_planta == 1) {
      digitalWrite(ACTIVAR_PIN_D1, HIGH);
      digitalWrite(ACTIVAR_PIN_D2, HIGH);
    } else {
      digitalWrite(ACTIVAR_PIN_D1, LOW);
      digitalWrite(ACTIVAR_PIN_D2, LOW);
    }
  }

  delay(500);
}
