import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import io
import requests
from streamlit_lottie import st_lottie
import time

# -----------------------------
# Animación de inicio con Lottie
# -----------------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# URL de animación Lottie gratis
lottie_json = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_x62chJ.json")

# Mostrar animación al inicio
st_lottie(lottie_json, height=200)
st.subheader("¡Bienvenido a la gestión de gastos! 🏡")
with st.spinner("Cargando la app... ⏳"):
    time.sleep(2)  # Simula carga de datos

# -----------------------------
# Configuración inicial
# -----------------------------
st.title("Gestión de Gastos del Piso 🏡")

CSV_PATH = "historial_gastos.csv"

# -----------------------------
# 1) Cargar historial CSV
# -----------------------------
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    df = pd.DataFrame(columns=[
        "Mes", "Agua", "Luz", "Alquiler",
        "Internet", "Gas", "Total Básico", "Total con Internet",
        "Streaming Total", "Streaming p/p (½)", "60% Ajustado"
    ])
    df.to_csv(CSV_PATH, index=False)

# -----------------------------
# 2) Mostrar historial existente
# -----------------------------
if not df.empty:
    st.subheader("📜 Historial de Meses")
    st.dataframe(df)

# -----------------------------
# 3) Función para convertir input a float
# -----------------------------
def parse_input(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

# -----------------------------
# 4) Inputs de gastos usando placeholder sombreado
# -----------------------------
st.subheader("Registrar nuevos gastos")

# Gastos básicos
agua_input     = st.text_input("Agua (€)", value="", placeholder="0.00", key="agua")
luz_input      = st.text_input("Luz (€)", value="", placeholder="0.00", key="luz")
alquiler_input = st.text_input("Alquiler (€)", value="", placeholder="0.00", key="alquiler")
internet_input = st.text_input("Internet (€)", value="", placeholder="0.00", key="internet")
gas_input      = st.text_input("Gas (€)", value="", placeholder="0.00", key="gas")

agua     = parse_input(agua_input)
luz      = parse_input(luz_input)
alquiler = parse_input(alquiler_input)
internet = parse_input(internet_input)
gas      = parse_input(gas_input)

# Streaming
st.markdown("**Gastos de Streaming**")
netflix_input  = st.text_input("Netflix (€)", value="", placeholder="0.00", key="netflix")
disney_input   = st.text_input("Disney+ (€)", value="", placeholder="0.00", key="disney")
movistar_input = st.text_input("Movistar Plus (€)", value="", placeholder="0.00", key="movistar")

netflix  = parse_input(netflix_input)
disney   = parse_input(disney_input)
movistar = parse_input(movistar_input)

# -----------------------------
# 5) Cálculos
# -----------------------------
total_basico    = agua + luz + alquiler + gas
total_internet  = total_basico + internet

streaming_total = netflix + disney + movistar
streaming_pp    = streaming_total / 2
share_60        = total_internet * 0.6
share_40        = total_internet * 0.4
share_60_ajust  = share_60 - streaming_pp

st.subheader(f"Total a depositar al señor Luis: {total_basico:.2f} €")
st.subheader(f"Total con Internet: {total_internet:.2f} €")
st.write(f"- 60% original sin ajuste de plataformas streaming: {share_60:.2f} €")
st.write(f"- 40% Papa: {share_40:.2f} €")
st.write(f"- Streaming total: {streaming_total:.2f} € (p/p = {streaming_pp:.2f} €)")
st.write(f"- 60% ajustado Maria y Miguel (60% – p/p streaming): {share_60_ajust:.2f} €")

# -----------------------------
# 6) Registrar y guardar en historial
# -----------------------------
if st.button("Registrar Mes"):
    nueva = {
        "Mes": pd.Timestamp.now().strftime("%Y-%m"),
        "Agua": agua,
        "Luz": luz,
        "Alquiler": alquiler,
        "Internet": internet,
        "Gas": gas,
        "Total Básico": total_basico,
        "Total con Internet": total_internet,
        "Streaming Total": streaming_total,
        "Streaming p/p (½)": streaming_pp,
        "60% Ajustado": share_60_ajust
    }
    df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    st.success(f"Gastos de {nueva['Mes']} registrados ✅")
    st.dataframe(df)

# -----------------------------
# 6b) Botón para borrar último mes
# -----------------------------
if st.button("Borrar último mes"):
    if not df.empty:
        df = df.iloc[:-1]  # elimina la última fila
        df.to_csv(CSV_PATH, index=False)
        st.success("Último mes eliminado ✅")
        st.dataframe(df)
    else:
        st.warning("No hay meses para borrar")

# -----------------------------
# 7) Gráficas
# -----------------------------
if not df.empty:
    st.subheader("📊 Gráficas de Gastos")
    
    # Gráfica completa
    fig, ax = plt.subplots()
    ax.bar(df["Mes"], df["Total con Internet"], label="Total c/Internet")
    ax.bar(df["Mes"], df["Streaming Total"], bottom=df["Total con Internet"],
           label="Streaming total")
    ax.set_title("Gastos por Mes (Internet + Streaming)")
    ax.set_ylabel("€")
    ax.legend()
    st.pyplot(fig)
    
    # Descargar gráfica completa
    buf_total = io.BytesIO()
    fig.savefig(buf_total, format="png")
    buf_total.seek(0)
    st.download_button(
        label="Descargar gráfica completa",
        data=buf_total,
        file_name=f"gastos_total_{pd.Timestamp.now().strftime('%Y-%m-%d')}.png",
        mime="image/png"
    )
    
    # Gráfica del último mes
    ultimo_mes = df.iloc[-1:]
    fig_mes, ax_mes = plt.subplots()
    ax_mes.bar(ultimo_mes["Mes"], ultimo_mes["Total con Internet"], label="Total c/Internet")
    ax_mes.bar(ultimo_mes["Mes"], ultimo_mes["Streaming Total"], bottom=ultimo_mes["Total con Internet"],
               label="Streaming total")
    ax_mes.set_title(f"Gastos {ultimo_mes['Mes'].values[0]}")
    ax_mes.set_ylabel("€")
    ax_mes.legend()
    st.pyplot(fig_mes)
    
    # Descargar gráfica del último mes
    buf_mes = io.BytesIO()
    fig_mes.savefig(buf_mes, format="png")
    buf_mes.seek(0)
    st.download_button(
        label=f"Descargar gráfica del mes {ultimo_mes['Mes'].values[0]}",
        data=buf_mes,
        file_name=f"gastos_{ultimo_mes['Mes'].values[0]}.png",
        mime="image/png"
    )
