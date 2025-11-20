import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
import json
import re

st.title("SmartEcoHome – Control por Voz")

broker = "broker.mqttdashboard.com"
port = 1883

client = paho.Client(client_id="SmartEco_Voz",
                     callback_api_version=paho.CallbackAPIVersion.VERSION1)
client.connect(broker, port)

st.write("Pulsa y da una instrución como:")
st.write("• encender luz")
st.write("• apagar ventilador")
st.write("• abrir puerta 120")

btn = Button(label="🎤 Hablar", width=200)

btn.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.lang = "es-ES";
    recognition.onresult = function(e){
        var text = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    btn,
    events="GET_TEXT",
    key="voz",
    refresh_on_update=False
)

def interpretar(texto):
    t = texto.lower()

    if "encender luz" in t: return ("luz_on", 0)
    if "apagar luz" in t: return ("luz_off", 0)
    if "encender ventilador" in t: return ("vent_on", 0)
    if "apagar ventilador" in t: return ("vent_off", 0)

    if "puerta" in t:
        m = re.search(r"\d+", t)
        ang = int(m.group()) if m else 90
        return ("puerta", ang)

    return (None, None)

if result and "GET_TEXT" in result:
    txt = result["GET_TEXT"]
    st.write(f"🗣 Dijiste: {txt}")

    action, value = interpretar(txt)
    if action:
        msg = json.dumps({"action": action, "value": value})
        client.publish("smarteco/voz", msg)
        st.success("Comando enviado")
    else:
        st.error("No entendí la instrucción")
