import streamlit as st
import paho.mqtt.client as mqtt
import json
import uuid

BROKER = "broker.hivemq.com"
TOPIC_CONTROL = "smarteco/control"

# MQTT con client_id único (obligatorio en HiveMQ)
client = mqtt.Client(client_id=f"voz_{uuid.uuid4()}", protocol=mqtt.MQTTv311)
client.connect(BROKER, 1883, 60)

st.title("🎤 Control por Voz – SmartEcoHome")
st.write("Haz clic en el botón y permite acceso al micrófono.")

# ----------- JAVASCRIPT PARA CAPTURAR VOZ -----------
voice_script = """
<script>
function startRecognition(){
    const recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event){
        const text = event.results[0][0].transcript;
        const inputBox = window.parent.document.getElementById("voice_text");
        inputBox.value = text;
        const submitEvent = new Event("input", { bubbles: true });
        inputBox.dispatchEvent(submitEvent);
    }

    recognition.onerror = function(event){
        console.log("Error:", event.error);
    }

    recognition.start();
}
</script>
"""

st.components.v1.html(voice_script, height=0)

# ----------- INPUT OCULTO PARA RECIBIR TEXTO -----------

text = st.text_input("", key="voice_text", label_visibility="collapsed")

if st.button("🎙️ Iniciar reconocimiento de voz"):
    st.components.v1.html("<script>startRecognition()</script>", height=0)

# Cuando cambia el texto → procesar
if text:
    st.success(f"Comando detectado: {text}")

    text_l = text.lower()

    # --------- MAPEO ROBUSTO DE COMANDOS ---------
    if "encender luz" in text_l or "enciende luz" in text_l or "prende luz" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_on"}))

    elif "apagar luz" in text_l or "apaga luz" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "luz_off"}))

    elif "encender ventilador" in text_l or "enciende ventilador" in text_l or "prende ventilador" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_on"}))

    elif "apagar ventilador" in text_l or "apaga ventilador" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "vent_off"}))

    elif "abrir puerta" in text_l or "abre puerta" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 90}))

    elif "cerrar puerta" in text_l or "cierra puerta" in text_l:
        client.publish(TOPIC_CONTROL, json.dumps({"action": "puerta", "value": 0}))

    else:
        st.error("❌ No reconocí un comando válido.")

    # Limpiar el texto para permitir nuevos comandos
    st.session_state.voice_text = ""
