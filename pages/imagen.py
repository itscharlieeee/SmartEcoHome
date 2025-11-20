# pages/imagen.py
import streamlit as st
import mediapipe as mp
import cv2
import numpy as np
import json
import paho.mqtt.client as mqtt
from PIL import Image
import io

st.set_page_config(page_title="Imagen - SmartEcoHome")

with st.sidebar:
    st.subheader("MQTT (Imagen)")
    broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com", key="b_img")
    port = st.number_input("Puerto", value=1883, min_value=1, max_value=65535, key="p_img")
    action_topic = st.text_input("Tópico acciones", value="smarteco/acciones", key="t_img")
    client_id = st.text_input("Client ID", value="smarteco_streamlit_img", key="c_img")

def publish_command(cmd: dict):
    try:
        client = mqtt.Client(client_id=client_id)
        client.connect(broker, int(port), 60)
        client.publish(action_topic, json.dumps(cmd))
        client.disconnect()
        return True, None
    except Exception as e:
        return False, str(e)

st.title("Detección por Imagen - Encender luz si hay persona")

st.markdown("Sube una foto. Si se detecta una persona (rostro) se sugiere encender la luz automáticamente.")

uploaded = st.file_uploader("Sube imagen", type=["png","jpg","jpeg"])
if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Imagen subida", use_column_width=True)

    # Convertir a BGR para OpenCV
    img = np.array(image)[:, :, ::-1].copy()

    mp_face = mp.solutions.face_detection
    with mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as detector:
        results = detector.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if results.detections:
        st.success(f"Persona detectada ({len(results.detections)} detección(es))")
        if st.button("Encender luz automáticamente"):
            ok, err = publish_command({"action": "luz_on", "value": 1})
            st.success("Comando enviado (luz_on)") if ok else st.error(f"Error: {err}")
    else:
        st.info("No se detectaron personas.")
        if st.button("Apagar luz (ninguna persona)"):
            ok, err = publish_command({"action": "luz_off", "value": 0})
            st.success("Comando enviado (luz_off)") if ok else st.error(f"Error: {err}")

    # Mostrar detecciones (si existen)
    if results.detections:
        annotated = img.copy()
        for det in results.detections:
            bbox = det.location_data.relative_bounding_box
            h, w, _ = annotated.shape
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = x1 + int(bbox.width * w)
            y2 = y1 + int(bbox.height * h)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0,255,0), 2)
        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        st.image(annotated, caption="Detecciones", use_column_width=True)
