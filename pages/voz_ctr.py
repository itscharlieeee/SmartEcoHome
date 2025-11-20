import streamlit as st
import paho.mqtt.client as mqtt
import json

BROKER = "broker.hivemq.com"
TOPIC_CONTROL = "smarteco/control"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883, 60)

st.title("🎤 Control por Voz – SmartEcoHome")
st.write("Haz clic en el botón y permite acceso al micrófono.")

# -----------------------------
# Estado inicial
# -----------------------------
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""


# -----------------------------
# JavaScript para reconocimiento
# -----------------------------
js_code = """
<script>
function startRecognition(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Tu navegador no soporta reconocimiento de voz.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event){
        const text = event.results[0][0].transcript;

        const input = window.parent.document.querySelector('input[id="voice_input"]');
        if (input){
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }

        const submitBtn = window.parent.document.querySelector('button[id="voice_submit"]');
        if (submitBtn){
            submitBtn.click();
        }
    }

    recognition.start();
}
</script>
"""
st.components.v1.html(js_code, height=0)


# -----------------------------
# Formulario de comando
# -----------------------------
with st.form("form"):
    text = st.text_input("Comando:", value=st.session_state.voice_text, key="voice_text", label_visibility="collapsed", id="voice_input")
    submitted = st.form_submit_button("Procesar comando", type="primary", id="voice_submit")


# -----------------------------
# Botón para iniciar captura
# -----------------------------
if st.button("🎙️ Iniciar reconocimiento de voz"):
    st.components.v1.html("<script>startRecognition()</script>", height=0)


# -----------------------------
# Procesamiento de comandos
# -----------------------------
if submitted and text:
    cmd = text.lower()
    st.success(f"Detectado: {cmd}")

    if "encender luz" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_on"}))
        st.info("💡 Luz encendida")
    elif "apagar luz" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_off"}))
        st.info("💡 Luz apagada")
    elif "encender ventilador" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_on"}))
        st.info("🌀 Ventilador encendido")
    elif "apagar ventilador" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_off"}))
        st.info("🌀 Ventilador apagado")
    elif "abrir puerta" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 90}))
        st.info("🚪 Puerta abierta")
    elif "cerrar puerta" in cmd:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 0}))
        st.info("🚪 Puerta cerrada")
    else:
        st.error("❌ No se reconoció un comando válido.")

    # reset del input
    st.session_state.voice_text = ""

    st.rerun()
