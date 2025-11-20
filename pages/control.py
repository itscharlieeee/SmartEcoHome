import streamlit as st
import paho.mqtt.client as paho
import json

st.title("🟢 Control & Sensores - SmartEcoHome")

broker = "broker.mqttdashboard.com"
port = 1883

# Cliente MQTT compatible con Paho 2.0
client = paho.Client(
    client_id="SmartEcoHome_Control",
    userdata=None,
    protocol=paho.MQTTv311,
    transport="tcp",
    callback_api_version=1
)

sensor_data = {"temp": 0, "hum": 0, "luz": 0, "gas": 0}


def on_message(client, userdata, message):
    global sensor_data
    try:
        payload = json.loads(message.payload.decode())
        sensor_data = payload
    except:
        pass

client.on_message = on_message
client.connect(broker, port)
client.subscribe("smarteco/sensores")
client.loop_start()

# ------------- UI SENSORES --------------
st.subheader("📊 Sensores en tiempo real")

col1, col2 = st.columns(2)

with col1:
    st.metric("🌡 Temperatura", f"{sensor_data['temp']} °C")
    st.metric("💡 Luz (LDR)", sensor_data["luz"])

with col2:
    st.metric("💧 Humedad", f"{sensor_data['hum']} %")
    st.metric("🧪 Gas", sensor_data["gas"])

st.divider()

# ----------- CONTROL DE DISPOSITIVOS ----------
st.subheader("🎛 Control de dispositivos")

def enviar_accion(action, value=None):
    msg = {"action": action}
    if value is not None:
        msg["value"] = value
    client.publish("smarteco/acciones", json.dumps(msg))

colA, colB = st.columns(2)

with colA:
    st.write("💡 **Luz**")
    if st.button("Encender Luz"):
        enviar_accion("luz_on")
    if st.button("Apagar Luz"):
        enviar_accion("luz_off")

with colB:
    st.write("🌀 **Ventilador**")
    if st.button("Encender Ventilador"):
        enviar_accion("vent_on")
    if st.button("Apagar Ventilador"):
        enviar_accion("vent_off")

st.write("🚪 **Puerta (servo)**")
if st.button("Abrir Puerta"):
    enviar_accion("puerta", 90)
if st.button("Cerrar Puerta"):
    enviar_accion("puerta", 0)
