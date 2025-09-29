import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

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
# Función para borrar input al click
# -----------------------------
def reset_input(key):
    if st.session_state[key + "_clicked"] == False:
        st.session_state[key] = 0.0
        st.session_state[key + "_clicked"] = True

# -----------------------------
# Inicializar session_state
# -----------------------------
keys = ["agua", "luz", "alquiler", "internet", "gas", "netflix", "disney", "movistar"]
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 0.0
    if key + "_clicked" not in st.session_state:
        st.session_state[key + "_clicked"] = False

# -----------------------------
# 3) Inputs de nuevos gastos
# -----------------------------
st.subheader("Registrar nuevos gastos")

agua     = st.number_input("Agua (€)", value=st.session_state["agua"], min_value=0.0,
                           key="agua", on_change=reset_input, args=("agua",))
luz      = st.number_input("Luz (€)", value=st.session_state["luz"], min_value=0.0,
                           key="luz", on_change=reset_input, args=("luz",))
alquiler = st.number_input("Alquiler (€)", value=st.session_state["alquiler"], min_value=0.0,
                           key="alquiler", on_change=reset_input, args=("alquiler",))
internet = st.number_input("Internet (€)", value=st.session_state["internet"], min_value=0.0,
                           key="internet", on_change=reset_input, args=("internet",))
gas      = st.number_input("Gas (€)", value=st.session_state["gas"], min_value=0.0,
                           key="gas", on_change=reset_input, args=("gas",))

st.markdown("**Gastos de Streaming**")
netflix  = st.number_input("Netflix (€)", value=st.session_state["netflix"], min_value=0.0,
                           key="netflix", on_change=reset_input, args=("netflix",))
disney   = st.number_input("Disney+ (€)", value=st.session_state["disney"], min_value=0.0,
                           key="disney", on_change=reset_input, args=("disney",))
movistar = st.number_input("Movistar Plus (€)", value=st.session_state["movistar"], min_value=0.0,
                           key="movistar", on_change=reset_input, args=("movistar",))

# -----------------------------
# 4) Cálculos
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
st.write(f"- 60% original: {share_60:.2f} €")
st.write(f"- 40%: {share_40:.2f} €")
st.write(f"- Streaming total: {streaming_total:.2f} € (p/p = {streaming_pp:.2f} €)")
st.write(f"- 60% ajustado: {share_60_ajust:.2f} €")

# -----------------------------
# 5) Registrar Mes
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
# 6) Gráficas
# -----------------------------
if not df.empty:
    st.subheader("📊 Gráficas de Gastos")
    
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
    
    # Gráfica último mes
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
