import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json

# Archivo para guardar y cargar los datos
datos_file = "datos_experimentos.json"

# Función para cargar datos desde un archivo
def cargar_datos():
    try:
        with open(datos_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Función para guardar datos en un archivo
def guardar_datos(datos):
    with open(datos_file, "w") as f:
        json.dump(datos, f)

# Inicializar la lista de datos en session_state si no existe
if "datos" not in st.session_state:
    st.session_state["datos"] = cargar_datos()

# 📌 **Enunciado del problema**
st.markdown(
    r"""
    # 📖 Cálculo de la Masa Molar de un Polímero  
    Se tiene un polímero en solución y se miden las presiones osmóticas ($\Pi$) a diferentes concentraciones ($c$) a una temperatura de 298 K.  
    """
    )
st.latex(r"""
\Pi = \frac{c R T}{M}
""")
st.markdown("""
    De donde se puede obtener la masa molar del polímero:  
    """)
st.latex(r"""
M = \frac{c R T}{\Pi}
""")
st.markdown(r"""
    Adicionalmente, la gráfica de $\Pi / c$ vs. $c$ permite obtener la masa molar desde la ordenada en el origen:
    """)
st.latex(r"""
\frac{\Pi}{c} = \frac{R T}{M}
""")
st.latex(r"""
M = \frac{R T}{\text{ordenada en el origen}}
""")

# Sidebar para entrada de datos
st.sidebar.header("Añadir o Modificar Experimentos")

# Número de experimento
num_experimento = st.sidebar.number_input("Número de Experimento", min_value=1, step=1, value=1)

# Entrada de datos
c = st.sidebar.number_input("Concentración (g/L)", min_value=0.1, max_value=10.0, value=2.5)
pi = st.sidebar.number_input("Presión Osmótica (Pa)", min_value=1.0, max_value=50.0, value=14.0)

# Botón para añadir o modificar el experimento
if st.sidebar.button("Guardar Datos"):
    pi_c = pi / c  # Cálculo de la nueva columna Pi/c
    experimento_existente = next((exp for exp in st.session_state["datos"] if exp["Experimento"] == num_experimento), None)
    if experimento_existente:
        # Si el experimento ya existe, modificar los valores
        experimento_existente["Concentración"] = c
        experimento_existente["Presión"] = pi
        experimento_existente["Pi/C"] = pi_c
        st.sidebar.success(f"Experimento {num_experimento} actualizado.")
    else:
        # Si no existe, añadirlo a la lista
        nuevo_punto = {"Experimento": num_experimento, "Concentración": c, "Presión": pi, "Pi/C": pi_c}
        st.session_state["datos"].append(nuevo_punto)
        st.sidebar.success(f"Experimento {num_experimento} añadido.")
    guardar_datos(st.session_state["datos"])

# Botón para borrar todos los datos
if st.sidebar.button("Borrar Todos los Datos"):
    st.session_state["datos"] = []
    guardar_datos([])
    st.sidebar.success("Todos los datos han sido eliminados.")

# 📋 **Mostrar tabla de experimentos guardados**
st.subheader("📋 Tabla de Experimentos Guardados")
if st.session_state["datos"]:
    st.table(st.session_state["datos"])
else:
    st.info("Aún no hay experimentos guardados. Agrega datos usando el botón en la barra lateral.")

# 📈 Gráfica de Pi/C vs Concentración con ajuste lineal
if st.session_state["datos"]:
    st.subheader(r"📈 Gráfica de $\Pi / c$ vs Concentración con Ajuste Lineal")

    # Obtener valores
    c_values = np.array([d["Concentración"] for d in st.session_state["datos"]])
    pi_c_values = np.array([d["Pi/C"] for d in st.session_state["datos"]])

    # Ajuste lineal (regresión)
    coef = np.polyfit(c_values, pi_c_values, 1)  # Ajuste lineal de primer grado
    polinomio = np.poly1d(coef)  # Crear la ecuación de la recta

    # Extender la línea hasta c=0
    c_extended = np.linspace(0, max(c_values), 100)
    ajuste_extended = polinomio(c_extended)

    # Calcular la masa molar desde la ordenada en el origen
    ordenada_origen = coef[1]
    if ordenada_origen > 0:
        masa_molar_ordenada = (8.314 * 298) / ordenada_origen
    else:
        masa_molar_ordenada = None

    # Graficar los datos y el ajuste
    plt.figure(figsize=(6, 4))
    plt.scatter(c_values, pi_c_values, color="r", label="Datos ingresados")
    plt.plot(c_extended, ajuste_extended, color="b", linestyle="--", label=f"Ajuste lineal: {coef[0]:.2f}c + {coef[1]:.2f}")
    plt.xlabel("Concentración (g/L)")
    plt.ylabel("Pi / c (Pa·L/g)")
    plt.legend()
    plt.grid(True)

    # Mostrar la gráfica en Streamlit
    st.pyplot(plt)

    # Mostrar la masa molar calculada desde la ordenada en el origen
    if masa_molar_ordenada:
        st.subheader("📌 Masa Molar Estimada desde la Ordenada en el Origen")
        st.latex(rf"M = {masa_molar_ordenada:.2f} \text{{ g/mol}}")
    else:
        st.warning("No se pudo calcular la masa molar desde la ordenada en el origen.")
