import streamlit as st

st.set_page_config(page_title="Simulador Ambiental", page_icon="✨")

st.title("✨ Simulador Ambiental de SmartEcoHome")
st.write("Controla la atmósfera del hogar de manera visual, sin afectar los dispositivos reales.")

st.divider()

# ---------------------------
# Ajustes de luz
# ---------------------------

st.subheader("💡 Ajustes de Luz")

brillo = st.slider("Brillo de la luz", 0, 100, 60)
color_luz = st.color_picker("Color de la iluminación", "#FFD966")

# Vista previa de luz
st.write("### Vista previa de la luz:")
st.markdown(
    f"""
    <div style="
        width:180px;
        height:180px;
        border-radius:50%;
        background:{color_luz};
        opacity:{brillo/100};
        margin:auto;
        box-shadow:0 0 30px {color_luz};
    "></div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ---------------------------
# Temperatura ambiental
# ---------------------------

st.subheader("🌡️ Temperatura del Hogar")

temp = st.slider("Temperatura", 10, 40, 23)

if temp <= 18:
    estado_temp = "Frío ❄️"
elif temp <= 28:
    estado_temp = "Agradable 🌤️"
else:
    estado_temp = "Caluroso 🔥"

st.metric("Estado de la habitación", estado_temp)

st.divider()

# ---------------------------
# Resumen general
# ---------------------------

st.subheader("📋 Resumen del Ambiente Configurado")

st.write(f"""
- **Brillo:** {brillo}%
- **Color de luz:** {color_luz}
- **Temperatura:** {temp}°C — *{estado_temp}*
""")
