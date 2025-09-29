import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# -----------------------------
# Configuración inicial
# -----------------------------
st.title("Gestión de Gastos del Piso 🏡")

CSV_PATH = "historial_gastos.csv"
EXPORT_PATH = "graficas"
os.makedirs(EXPORT_PATH, exist_ok=True)

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

required_columns = [
    "Mes", "Agua", "Luz", "Alquiler",
    "Internet", "Gas", "Total Básico", "Total con Internet",
    "Streaming Total", "Streaming p/p (½)", "60% Ajustado"
]

for col in required_columns:
    if col not in df.columns:
        df[col] = pd.NA

# -----------------------------
# 2) Mostrar historial existente
# -----------------------------
if not df.empty:
    st.subheader("📜 Historial de Meses")
    st.dataframe(df)

# -----------------------------
# 3) Inputs de nuevos gastos (se borran al hacer click)
# -----------------------------
st.subheader("Registrar nuevos gastos")

def parse_input(key):
    """Convierte text_input a float o 0 si está vacío"""
    val = st.session_state.get(key, "")
    try:
        return float(val)
    except ValueError:
        return 0.0

# Inputs principales
agua_input = st.text_input("Agua (€)", value="", key="agua")
luz_input = st.text_input("Luz (€)", value="", key="luz")
alquiler_input = st.text_input("Alquiler (€)", value="", key="alquiler")
internet_input = st.text_input("Internet (€)", value="", key="internet")
gas_input = st.text_input("Gas (€)", value="", key="gas")

agua     = parse_input("agua")
luz      = parse_input("luz")
alquiler = parse_input("alquiler")
internet = parse_input("internet")
gas      = parse_input("gas")

# Streaming
st.markdown("**Gastos de Streaming**")
netflix_input = st.text_input("Netflix (€)", value="", key="netflix")
disney_input  = st.text_input("Disney+ (€)", value="", key="disney")
movistar_input= st.text_input("Movistar Plus (€)", value="", key="movistar")

netflix  = parse_input("netflix")
disney   = parse_input("disney")
movistar = parse_input("movistar")

# -----------------------------
# 4) Cálculos principales
# -----------------------------
total_basico    = agua + luz + alquiler + gas
total_internet  = total_basico + internet

streaming_total = netflix + disney + movistar
streaming_pp    = streaming_total / 2
share_60        = total_internet * 0.6
share_40        = total_internet * 0.4
share_60_ajust  = share_60 - streaming_pp

# Mostrar resultados
st.subheader(f"Total a depositar al señor Luis: {total_basico:.2f} €")
st.subheader(f"Total con Internet: {total_internet:.2f} €")
st.write(f"- 60% original sin ajuste de plataformas streaming: {share_60:.2f} €")
st.write(f"- 40% Papa: {share_40:.2f} €")
st.write(f"- Streaming total: {streaming_total:.2f} € (p/p = {streaming_pp:.2f} €)")
st.write(f"- 60% ajustado Maria y Miguel (60% – p/p streaming): {share_60_ajust:.2f} €")

# -----------------------------
# 5) Registrar y guardar en historial
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
# 6) Gráficos del historial
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
    
    # Guardar gráfica completa
    filename_total = f"{EXPORT_PATH}/gastos_total_{pd.Timestamp.now().strftime('%Y-%m-%d')}.png"
    fig.savefig(filename_total)
    st.success(f"Gráfica completa exportada como {filename_total}")

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

    filename_mes = f"{EXPORT_PATH}/gastos_{ultimo_mes['Mes'].values[0]}.png"
    fig_mes.savefig(filename_mes)
    st.success(f"Gráfica del mes {ultimo_mes['Mes'].values[0]} exportada ✅")
