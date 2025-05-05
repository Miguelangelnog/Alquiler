import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Gestión de Gastos del Piso 🏡")

# Entradas
agua    = st.number_input("Agua (€)",    min_value=0.0)
luz     = st.number_input("Luz (€)",     min_value=0.0)
alquiler= st.number_input("Alquiler (€)",min_value=0.0)
internet= st.number_input("Internet (€)",min_value=0.0)

# Cálculos
total_basico  = agua + luz + alquiler
total_internet= total_basico + internet

# Mostrar resultados
st.subheader(f"Total Básico: {total_basico:.2f} €")
st.subheader(f"Total con Internet: {total_internet:.2f} €")
st.write("- 60%:", f"{total_internet*0.6:.2f} €")
st.write("- 40%:", f"{total_internet*0.4:.2f} €")

# Botón para ver y guardar historial
if st.button("Registrar Mes y Ver Historial"):
    fecha = pd.Timestamp.now().strftime("%Y-%m")
    fila = {
        "Mes": fecha,
        "Agua": agua, "Luz": luz, "Alquiler": alquiler,
        "Internet": internet,
        "Total Básico": total_basico,
        "Total con Internet": total_internet
    }
    try:
        df = pd.read_csv("historial_gastos.csv")
        df = df.append(fila, ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([fila])
    df.to_csv("historial_gastos.csv", index=False)
    st.success("✅ Gastos registrados.")
    st.dataframe(df)

# Gráficos
if 'df' in locals():
    fig1, ax1 = plt.subplots()
    ax1.bar(df["Mes"], df["Total con Internet"])
    ax1.set_title("Total con Internet por Mes")
    ax1.set_ylabel("€")
    st.pyplot(fig1)
