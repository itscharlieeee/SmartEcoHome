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

        // Selecciona el input de Streamlit mediante su data-testid
        const input = window.parent.document.querySelector('[data-testid="voice_input"]');
        if (input){
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }

        // Selecciona el botón de submit
        const submitBtn = window.parent.document.querySelector('[data-testid="voice_submit"]');
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
    text = st.text_input(
        "",
        value=st.session_state.voice_text,
        key="voice_text",
        placeholder="Aquí aparecerá el comando...",
        label_visibility="collapsed"
    )

    # Agregamos testid con HTML post-insertado
    submit = st.form_submit_button("Procesar comando")

# Agregar atributos testid después de renderizar
st.components.v1.html("""
<script>
let inputs = window.parent.document.querySelectorAll('input[type="text"]');
if (inputs.length > 0){
    inputs[inputs.length - 1].setAttribute("data-testid", "voice_input");
}

let buttons = window.parent.document.querySelectorAll('button');
buttons[buttons.length - 1].setAttribute("data-testid", "voice_submit");
</script>
""", height=0)



# -----------------------------
# Botón para activar micrófono
# -----------------------------
if st.button("🎙️ Iniciar reconocimiento de voz"):
    st.components.v1.html("<script>startRecognition()</script>", height=0)


# -----------------------------
# Procesamiento de comandos
# -----------------------------
if submit and text:
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

    # Limpia el estado y recarga
    st.session_state.voice_text = ""
    st.rerun()
