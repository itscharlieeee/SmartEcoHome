import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
import json
import time

# ------------------ MQTT ------------------
broker = "broker.mqttdashboard.com"
port = 1883

client = paho.Client("SmartEcoHome_Voz")
message_received = ""

def on_publish(client, userdata, result):
    print("Mensaje enviado")

def on_message(client, userdata, message):
    global message_received
    message_received = str(message.payload.decode("utf-8"))

client.on_message = on_message

# ------------------ UI ------------------
st.title("🎤 Control por Voz - SmartEcoHome")
st.write("Pulsa el botón y di un comando como:")
st.markdown("""
- **encender luz**
- **apagar luz**
- **encender ventilador**
- **apagar ventilador**
- **abrir puerta**
- **cerrar puerta**
""")

# Botón con Web Speech API
stt_button = Button(label="🎙️ Hablar", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "es-ES";

    recognition.onresult = function (e) {
        var value = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
    }

    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="voz_listener",
    override_height=75,
    debounce_time=0
)

# ------------------ PROCESAR RESULTADOS ------------------
if result and "GET_TEXT" in result:
    texto = result["GET_TEXT"].lower()
    st.success(f"🔊 Dijiste: **{texto}**")

    client.on_publish = on_publish
    client.connect(broker, port)

    # --------------------------------
    # Detectar comandos de voz
    # --------------------------------
    if "encender luz" in texto:
        mqtt_msg = {"action": "luz_on"}

    elif "apagar luz" in texto:
        mqtt_msg = {"action": "luz_off"}

    elif "encender ventilador" in texto:
        mqtt_msg = {"action": "vent_on"}

    elif "apagar ventilador" in texto:
        mqtt_msg = {"action": "vent_off"}

    elif "abrir puerta" in texto:
        mqtt_msg = {"action": "puerta", "value": 90}

    elif "cerrar puerta" in texto:
        mqtt_msg = {"action": "puerta", "value": 0}

    else:
        st.warning("⚠️ Comando no reconocido")
        mqtt_msg = None

    # Enviar si hay mensaje
    if mqtt_msg:
        topic = "smarteco/acciones"
        client.publish(topic, json.dumps(mqtt_msg))
        st.success(f"📡 Enviado a MQTT: `{mqtt_msg}`")
