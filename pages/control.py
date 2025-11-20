import streamlit as st
import paho.mqtt.client as mqtt
import json

BROKER = "test.mosquitto.org"
TOPIC_CONTROL = "smarteco/control"
TOPIC_ESTADO = "smarteco/estado"

st.title("🟢 SmartEcoHome - Panel de Control")

# -----------------------------------------
# ESTADO GLOBAL (se refresca automáticamente)
# -----------------------------------------
if "estado_actual" not in st.session_state:
    st.session_state.estado_actual = "Esperando datos..."

estado_box = st.empty()
estado_box.info("Estado del sistema: " + st.session_state.estado_actual)

# -----------------------------------------
# CALLBACKS MQTT
# -----------------------------------------
def on_connect(client, userdata, flags, reason, properties=None):
    client.subscribe(TOPIC_ESTADO)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        tipo = data.get("tipo")
        detalle = data.get("detalle")

        texto = f"{tipo}: {detalle}"
        st.session_state.estado_actual = texto
        estado_box.info("Estado del sistema: " + texto)
    except:
        pass

# -----------------------------------------
# MQTT CONFIG
# -----------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="SmartEcoHome_ControlWeb_123")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_start()

# -----------------------------------------
# FUNCIÓN PARA PUBLICAR
# -----------------------------------------
def publicar(action, value=0):
    payload = json.dumps({"action": action, "value": value})
    client.publish(TOPIC_CONTROL, payload)
    st.success(f"Comando enviado: {action} ({value})")

# -----------------------------------------
# INTERFAZ DE BOTONES
# -----------------------------------------
st.subheader("💡 Control de iluminación")
col1, col2 = st.columns(2)
if col1.button("Encender luz"):
    publicar("luz_on")

if col2.button("Apagar luz"):
    publicar("luz_off")

st.subheader("🌀 Control del ventilador")
col3, col4 = st.columns(2)
if col3.button("Encender ventilador"):
    publicar("vent_on")

if col4.button("Apagar ventilador"):
    publicar("vent_off")

st.subheader("🚪 Control de puerta")
col5, col6 = st.columns(2)
if col5.button("Abrir puerta"):
    publicar("puerta", 90)

if col6.button("Cerrar puerta"):
    publicar("puerta", 0)
