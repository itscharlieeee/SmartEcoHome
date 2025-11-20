import streamlit as st
import paho.mqtt.client as paho
import json

broker = "broker.mqttdashboard.com"
port = 1883

# MQTT compatible con Streamlit Cloud
client = paho.Client(client_id="SmartEco_Control", callback_api_version=paho.CallbackAPIVersion.VERSION1)

# ----------- CALLBACKS -----------
def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe("SmartEcoHome/sensores")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    st.session_state.sensores = data

client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port)

# ----------- UI -----------
st.title("Control Manual SmartEco")

# Mostrar sensores
if "sensores" in st.session_state:
    s = st.session_state.sensores
    st.metric("Temperatura", f"{s['temp']} °C")
    st.metric("Humedad", f"{s['hum']} %")
    st.metric("Luz", s["luz"])
    st.metric("Gas", s["gas"])

# ----------- Controles -----------
def enviar(action, value=0):
    msg = json.dumps({"action": action, "value": value})
    client.publish("SmartEcoHome/control", msg)

col1, col2 = st.columns(2)

with col1:
    if st.button("Encender Luz"):
        enviar("luz_on")
    if st.button("Apagar Luz"):
        enviar("luz_off")

with col2:
    if st.button("Ventilador ON"):
        enviar("vent_on")
    if st.button("Ventilador OFF"):
        enviar("vent_off")

pos = st.slider("Abrir/Cerrar puerta", 0, 180, 90)
enviar("puerta", pos)

client.loop_start()

