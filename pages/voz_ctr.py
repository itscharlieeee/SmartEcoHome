import streamlit as st
import paho.mqtt.client as mqtt
import json

st.set_page_config(page_title="Control por Voz – SmartEcoHome", page_icon="🎤")

st.title("🎤 Control por Voz – SmartEcoHome")

MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smarteco/acciones"
CLIENT_ID = "streamlit_voice_web"

# --- Función MQTT ---
def send_mqtt(action, value=None):
    try:
        client = mqtt.Client(client_id=CLIENT_ID)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        payload = {"action": action}
        if value is not None:
            payload["value"] = value

        client.publish(MQTT_TOPIC, json.dumps(payload))
        client.disconnect()
        return True
    except Exception as e:
        return False, str(e)

# --- Interpretador de comandos ---
def interpretar(texto):
    t = texto.lower()

    if "encender luz" in t or "prender luz" in t:
        return ("luz_on", None)
    if "apagar luz" in t:
        return ("luz_off", None)
    if "encender ventilación" in t or "encender ventilador" in t:
        return ("vent_on", None)
    if "apagar ventilación" in t or "apagar ventilador" in t:
        return ("vent_off", None)
    if "abrir puerta" in t or "abrir escotilla" in t:
        return ("puerta", 180)
    if "cerrar puerta" in t or "cerrar escotilla" in t:
        return ("puerta", 0)

    return (None, None)

st.write("Haz clic en el botón y da una orden como:")
st.markdown("""
- **'Encender luz'**
- **'Apagar ventilación'**
- **'Abrir puerta'**
- **'Cerrar escotilla'**
""")

# --- CONTENEDOR PARA MOSTRAR TEXTO ---
voice_text = st.empty()

# --- BOTÓN QUE ACTIVA API DE VOZ ---
st.markdown("""
<script>
let recognizer;
function startRecognition() {
    const output = document.getElementById("stVoiceText");
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognizer = new SpeechRecognition();
    recognizer.lang = "es-ES";
    recognizer.interimResults = false;
    recognizer.maxAlternatives = 1;

    recognizer.start();

    recognizer.onresult = function(event) {
        const text = event.results[0][0].transcript;
        output.value = text;
        const streamlitInput = document.querySelector('input[data-baseweb="input"]');
        streamlitInput.value = text;
        streamlitInput.dispatchEvent(new Event("input"));
    };
}
</script>
""", unsafe_allow_html=True)

# Campo oculto para recibir texto desde JS
texto_reconocido = st.text_input("Texto detectado por voz", key="voz_input")
voice_text.text(f"🗣️ Dijiste: {texto_reconocido}")

# Botón HTML que activa la voz
st.markdown("""
<button onclick="startRecognition()" style="
    background-color:#4CAF50;
    color:white;
    padding:12px;
    border:none;
    border-radius:10px;
    cursor:pointer;
    font-size:16px;">
🎤 Hablar
</button>
""", unsafe_allow_html=True)

# --- Procesar comando ---
if texto_reconocido.strip() != "":
    action, value = interpretar(texto_reconocido)

    if action is None:
        st.error("❌ No entendí una orden válida.")
    else:
        ok = send_mqtt(action, value)
        if ok:
            st.success(f"📡 Enviado → acción `{action}`, valor `{value}`")
        else:
            st.error("❌ Error enviando comando MQTT.")
