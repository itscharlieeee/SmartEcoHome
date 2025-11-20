import streamlit as st
import paho.mqtt.client as mqtt
import json
import uuid

BROKER = "broker.hivemq.com"
TOPIC_CONTROL = "smarteco/control"

client = mqtt.Client(client_id=f"voz_{uuid.uuid4()}", protocol=mqtt.MQTTv311)
client.connect(BROKER, 1883, 60)

st.title("🎤 Control por Voz – SmartEcoHome")
st.write("Haz clic en el botón y permite acceso al micrófono.")

# ---------- JavaScript para captura ----------
voice_script = """
<script>
function startRecognition(){
    const recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event){
        const text = event.results[0][0].transcript;
        const input = window.parent.document.getElementById("voice_hidden");
        input.value = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    recognition.start();
}
</script>
"""

st.components.v1.html(voice_script, height=0)

# ---------- INPUT INVISIBLE ----------
hidden_box = st.empty()
text = hidden_box.text_input("", key="voice_hidden", label_visibility="collapsed")

# Botón que activa el micrófono
if st.button("🎙️ Iniciar reconocimiento de voz"):
    st.components.v1.html("<script>startRecognition()</script>", height=0)

# Procesar comando cuando texto cambia
if text:
    st.success(f"Comando detectado: {text}")
    text_l = text.lower()

    if "encender luz" in text_l or "enciende luz" in text_l or "prende luz" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_on"}))

    elif "apagar luz" in text_l or "apaga luz" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_off"}))

    elif "encender ventilador" in text_l or "prende ventilador" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_on"}))

    elif "apagar ventilador" in text_l or "apaga ventilador" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_off"}))

    elif "abrir puerta" in text_l or "abre puerta" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 90}))

    elif "cerrar puerta" in text_l or "cierra puerta" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 0}))

    else:
        st.error("❌ No reconocí un comando válido.")

    # Limpia el input DE MANERA SEGURA sin causar error
    st.session_state["voice_hidden"] = ""

