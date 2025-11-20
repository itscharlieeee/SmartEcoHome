import streamlit as st
import json
import paho.mqtt.client as paho

st.title("SmartEcoHome – Control Manual")

broker = "broker.mqttdashboard.com"
port = 1883

if "estado" not in st.session_state:
    st.session_state.estado = "Sin datos"

if "sensores" not in st.session_state:
    st.session_state.sensores = {}

def on_connect(client, userdata, flags, rc):
    client.subscribe("smarteco/sensores")
    client.subscribe("smarteco/estado")

def on_message(client, userdata, msg):
    topic = msg.topic
    data = json.loads(msg.payload.decode())

    if topic == "smarteco/sensores":
        st.session_state.sensores = data
    elif topic == "smarteco/estado":
        st.session_state.estado = f"{data['tipo']}: {data['detalle']}"

client = paho.Client(client_id="SmartEco_Control",
                     callback_api_version=paho.CallbackAPIVersion.VERSION1)

client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port)
client.loop_start()

st.subheader("Estado del sistema")
st.write(st.session_state.estado)

st.subheader("Sensores")
if st.session_state.sensores:
    s = st.session_state.sensores
    st.json(s)

def enviar(action, value=0):
    msg = json.dumps({"action": action, "value": value})
    client.publish("smarteco/control", msg)

col1, col2 = st.columns(2)

with col1:
    if st.button("Encender Luz"):
        enviar("luz_on")
    if st.button("Apagar Luz"):
        enviar("luz_off")

with col2:
    if st.button("Encender Ventilador"):
        enviar("vent_on")
    if st.button("Apagar Ventilador"):
        enviar("vent_off")

pos = st.slider("Ángulo de la Puerta", 0, 180, 90)
if st.button("Mover Puerta"):
    enviar("puerta", pos)

def on_connect(client, userdata, flags, rc):
    client.subscribe("smarteco/sensores")
    client.subscribe("smarteco/estado")
    
def on_message(client, userdata, msg):
    topic = msg.topic
    data = json.loads(msg.payload.decode())

    if topic == "smarteco/sensores":
        st.session_state.sensores = data

    if topic == "smarteco/estado":
        tipo = data["tipo"]
        detalle = data["detalle"]
        st.session_state.estado = f"{tipo}: {detalle}"

