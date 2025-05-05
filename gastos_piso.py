import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Título de la app
st.title("Gestión de Gastos del Piso 🏡")

# Ruta del archivo CSV
CSV_PATH = "historial_gastos.csv"

# 1) Cargar historial desde CSV (si existe)
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)  # Cargar historial si ya existe
else:
    # Crear el CSV vacío con las columnas adecuadas si no existe
    df = pd.DataFrame(columns=[
        "Mes", "Agua", "Luz", "Alquiler", 
        "Internet", "Gas", "Total Básico", "Total con Internet",
        "Streaming Total", "Streaming p/p (½)", "60% Ajustado"
    ])
    df.to_csv(CSV_PATH, index=False)  # Crear el archivo vacío

# 2) Mostrar historial existente
if not df.empty:
    st.subheader("📜 Historial de Meses")
    st.dataframe(df)

# 3) Inputs de nuevos gastos
st.subheader("Registrar nuevos gastos")
agua      = st.number_input("Agua (€)",     min_value=0.0, key="agua")
luz       = st.number_input("Luz (€)",      min_value=0.0, key="luz")
alquiler  = st.number_input("Alquiler (€)", min_value=0.0, key="alquiler")
internet  = st.number_input("Internet (€)", min_value=0.0, key="internet")
gas       = st.number_input("Gas (€)",      min_value=0.0, key="gas")

# Streaming
st.markdown("**Gastos de Streaming**")
netflix     = st.number_input("Netflix (€)",         min_value=0.0, key="netflix")
disney      = st.number_input("Disney+ (€)",         min_value=0.0, key="disney")
movistar    = st.number_input("Movistar Plus (€)",   min_value=0.0, key="movistar")

# 4) Cálculos principales
total_basico    = agua + luz + alquiler + gas  # Añadimos el gas al total básico
total_internet  = total_basico + internet

streaming_total = netflix + disney + movistar
streaming_pp    = streaming_total / 2
share_60        = total_internet * 0.6
share_40        = total_internet * 0.4

# Ajustamos el 60% restando la mitad del streaming
share_60_ajust  = share_60 - streaming_pp

# Mostrar resultados
st.subheader(f"Total Básico (con gas): {total_basico:.2f} €")
st.subheader(f"Total con Internet: {total_internet:.2f} €")
st.write(f"- 60% original: {share_60:.2f} €")
st.write(f"- 40%: {share_40:.2f} €")
st.write(f"- Streaming total: {streaming_total:.2f} € (p/p = {streaming_pp:.2f} €)")
st.write(f"- 60% ajustado (60% – p/p streaming): {share_60_ajust:.2f} €")

# 5) Registrar y guardar en historial
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
    df = df.append(nueva, ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    st.success(f"Gastos de {nueva['Mes']} registrados ✅")
    st.dataframe(df)

# 6) Gráficos del historial
if not df.empty:
    fig, ax = plt.subplots()
    ax.bar(df["Mes"], df["Total con Internet"], label="Total c/Internet")
    ax.bar(df["Mes"], df["Streaming Total"], bottom=df["Total con Internet"],
           label="Streaming total")
    ax.set_title("Gastos por Mes (Internet + Streaming)")
    ax.set_ylabel("€")
    ax.legend()
    st.pyplot(fig)
