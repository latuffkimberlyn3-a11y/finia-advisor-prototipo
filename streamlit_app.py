import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="FinIA Advisor - Prototipo", layout="wide")
st.title("🧠 FinIA Advisor")
st.subheader("Tu asesor financiero personal con IA - Versión Prototipo")

st.markdown("""
Sube tu archivo CSV de transacciones bancarias y te ayudo a entender tus finanzas.
Formato esperado del CSV:
- columna **fecha** (formato: YYYY-MM-DD o DD/MM/YYYY)
- columna **descripcion** (texto)
- columna **monto** (número positivo para ingresos, negativo para gastos)
""")

# Subir archivo
uploaded_file = st.file_uploader("Sube tu CSV de transacciones", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Mostrar columnas detectadas
        st.write("Columnas detectadas:", list(df.columns))
        
        # Normalizar nombres de columnas
        df.columns = [col.lower().strip() for col in df.columns]
        
        required_cols = ['fecha', 'descripcion', 'monto']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"Faltan columnas obligatorias: {missing}")
            st.stop()
        
        # Convertir fecha
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        
        # Convertir monto a numérico
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce')
        df = df.dropna(subset=['monto'])
        
        # Categorización simple (aquí empezamos con la "IA")
        categorias = {
            'supermercado': ['supermercado', 'mercado', 'walmart', 'coto', 'carrefour', 'dia', 'jumbo'],
            'transporte': ['uber', 'cabify', 'subte', 'colectivo', 'nafta', 'estacionamiento', 'peaje'],
            'entretenimiento': ['netflix', 'spotify', 'cine', 'bar', 'restaurante', 'delivery', 'rappi', 'pedidosya'],
            'suscripciones': ['netflix', 'spotify', 'disney', 'amazon prime', 'youtube premium'],
            'salud': ['farmacia', 'medico', 'obra social', 'prepaga'],
            'hogar': ['luz', 'gas', 'internet', 'alquiler', 'expensas'],
            'otros': []
        }
        
        def categorizar(descripcion):
            desc = descripcion.lower()
            for categoria, palabras in categorias.items():
                if any(palabra in desc for palabra in palabras):
                    return categoria.capitalize()
            return "Otros"
        
        df['categoria'] = df['descripcion'].apply(categorizar)
        
        # Cálculos
        ingresos = df[df['monto'] > 0]['monto'].sum()
        gastos = df[df['monto'] < 0]['monto'].sum()
        balance = ingresos + gastos  # gastos son negativos
        ahorro_potencial = abs(gastos) * 0.15  # sugerimos ahorrar 15%
        
        # Dashboard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ingresos", f"${ingresos:,.0f}")
        col2.metric("Gastos", f"${abs(gastos):,.0f}")
        col3.metric("Balance", f"${balance:,.0f}", delta=f"{balance:+,.0f}")
        col4.metric("Ahorro sugerido (15%)", f"${ahorro_potencial:,.0f}")
        
        # Gráfico de categorías
        gastos_por_cat = df[df['monto'] < 0].groupby('categoria')['monto'].sum().abs()
        fig = px.pie(gastos_por_cat, values=gastos_por_cat.values, names=gastos_por_cat.index,
                     title="Distribución de Gastos por Categoría",
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recomendación personalizada
                # Recomendación personalizada
        st.subheader("💡 Recomendación de FinIA")
        categoria_mayor_gasto = gastos_por_cat.idxmax()
        monto_mayor = gastos_por_cat.max()
        
        if categoria_mayor_gasto == "Otros":
            recomendacion = "Tienes muchos gastos sin categoría clara. ¡Sería genial revisarlos uno por uno para optimizar!"
        elif categoria_mayor_gasto == "Entretenimiento":
            recomendacion = f"Veo que {categoria_mayor_gasto} es tu mayor gasto (${monto_mayor:,.0f}). ¿Probamos reducir un 20% este mes? Podrías ahorrar ${monto_mayor*0.2:,.0f}."
        else:
            recomendacion = f"Tu mayor gasto es en {categoria_mayor_gasto} (${monto_mayor:,.0f}). Reducirlo un poco podría acercarte más rápido a tu meta de riqueza."
        
        st.success(recomendacion)
        
        st.download_button("Descargar análisis", df.to_csv(index=False), "analisis_finIA.csv")
        
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("👆 Sube un CSV para comenzar el análisis")
    st.markdown("### Ejemplo de CSV que puedes usar para probar:")
    ejemplo = pd.DataFrame({
        'fecha': ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-05', '2026-01-06'],
        'descripcion': ['Sueldo enero', 'Supermercado Dia', 'Uber al trabajo', 'Netflix mensual', 'Spotify'],
        'monto': [500000, -15000, -3200, -4999, -3999]
    })
    st.dataframe(ejemplo)
    st.download_button("Descargar CSV de ejemplo", ejemplo.to_csv(index=False), "ejemplo_transacciones.csv")
