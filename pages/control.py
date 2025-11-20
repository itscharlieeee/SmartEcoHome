# pages/control.py
import streamlit as st
import json
import time
import paho.mqtt.client as mqtt

st.set_page_config(page_title="Control - SmartEcoHome")

# Sidebar: configuración MQTT
with st.sidebar:
    st.subheader("Configuración MQTT")
    broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
    port = st.number_input("Puerto", value=1883, min_value=1, max_value=65535)
    sensor_topic = st.text_input("Tópico sensores", value="smarteco/sensores")
    action_topic = st.text_input("Tópico acciones", value="smarteco/acciones")
    client_id = st.text_input("Client ID", value="smarteco_streamlit_control")

def publish_command(cmd: dict):
    try:
        client = mqtt.Client(client_id=client_id)
        client.connect(broker, int(port), 60)
        payload = json.dumps(cmd)
        client.publish(action_topic, payload)
        client.disconnect()
        return True, None
    except Exception as e:
        return False, str(e)

st.title("Control - SmartEcoHome")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Controles rápidos")
    if st.button("💡 Encender luz", use_container_width=True):
        ok, err = publish_command({"action": "luz_on", "value": 1})
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")
    if st.button("💡 Apagar luz", use_container_width=True):
        ok, err = publish_command({"action": "luz_off", "value": 0})
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")

    if st.button("🌀 Encender ventilador", use_container_width=True):
        ok, err = publish_command({"action": "vent_on", "value": 1})
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")
    if st.button("🌀 Apagar ventilador", use_container_width=True):
        ok, err = publish_command({"action": "vent_off", "value": 0})
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")

with col2:
    st.subheader("Control de puerta (servo)")
    servo_val = st.slider("Ángulo servo (0-180)", 0, 180, 90)
    if st.button("Mover puerta a ángulo", use_container_width=True):
        ok, err = publish_command({"action": "puerta", "value": int(servo_val)})
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")

st.markdown("---")
st.subheader("Enviar comando por texto (JSON)")

cmd_text = st.text_area("JSON comando (ej. {\"action\":\"luz_on\",\"value\":1})", height=120)
if st.button("Enviar JSON"):
    try:
        cmd = json.loads(cmd_text)
        ok, err = publish_command(cmd)
        st.success("Comando enviado") if ok else st.error(f"Error: {err}")
    except Exception as e:
        st.error(f"JSON inválido: {e}")

st.markdown("---")
st.subheader("Leer último mensaje de sensores")
if st.button("Obtener último mensaje", use_container_width=True):
    with st.spinner("Conectando al broker y esperando mensaje..."):
        # suscribirse temporalmente y esperar un mensaje (timeout corto)
        received = {"payload": None, "done": False}
        def on_message(client, userdata, message):
            try:
                received["payload"] = json.loads(message.payload.decode())
            except:
                received["payload"] = message.payload.decode()
            received["done"] = True

        try:
            client = mqtt.Client(client_id=client_id + "_rx")
            client.on_message = on_message
            client.connect(broker, int(port), 60)
            client.subscribe(sensor_topic)
            client.loop_start()
            timeout = time.time() + 5
            while not received["done"] and time.time() < timeout:
                time.sleep(0.1)
            client.loop_stop()
            client.disconnect()
            if received["payload"]:
                st.success("Datos recibidos")
                if isinstance(received["payload"], dict):
                    cols = st.columns(len(received["payload"]))
                    for i, (k, v) in enumerate(received["payload"].items()):
                        with cols[i]:
                            st.metric(label=k, value=v)
                    with st.expander("Ver JSON completo"):
                        st.json(received["payload"])
                else:
                    st.code(str(received["payload"]))
            else:
                st.warning("No se recibió mensaje en 5s")
        except Exception as e:
            st.error(f"Error conexión: {e}")
