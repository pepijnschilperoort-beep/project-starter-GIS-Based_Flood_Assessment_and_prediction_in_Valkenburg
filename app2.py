import streamlit as st
import time
import os

# Set up the overall page configuration
st.set_page_config(page_title="Flood Assessment Model", layout="centered")

# ==========================================
# Sidebar Navigation
# ==========================================
st.sidebar.title("Navigation")
# This radio button controls which "page" is currently displayed
page = st.sidebar.radio("Select a page:", ["Introduction", "Simulation", "Input Data"])

# ==========================================
# Page 1: Introduction
# ==========================================
if page == "Introduction":
    st.title("🌧️ Pluvial Flood Assessment")
    st.markdown("""
    Welcome to the automated pluvial flood assessment pipeline for Wageningen.
    
    This interface allows you to interact with the underlying Cellular Automaton model. 
    It routes surface water across a fused high-resolution DTM/DSM, factoring in local 
    building obstructions, river sinks, and surface roughness.
    
    **Instructions:**
    1. Navigate to the **Simulation** page using the sidebar.
    2. Adjust the rainfall slider to your desired storm event.
    3. Click **Calculate** to trigger the local engine.
    4. View your configured files on the **Input Data** tab.
    """)

# ==========================================
# Page 2: Simulation (Slider & Execution)
# ==========================================
elif page == "Simulation":
    st.title("⚙️ Run Simulation")
    st.write("Set the storm parameters below to calculate the new water heights.")
    
    # Slider for rainfall
    rain_input = st.slider("Rainfall Amount (mm)", min_value=0.0, max_value=150.0, value=50.0, step=5.0)
    
    # Calculate Button
    if st.button("Calculate Flood Routing", type="primary"):
        # The spinner gives visual feedback while your heavy math runs
        with st.spinner(f"Running local model iterations for {rain_input} mm of rain..."):
            
            try:
                # --- CONNECT YOUR ENGINE HERE ---
                # import engine
                # model = engine.CatchmentModel("tmp/Fused_DTM_DSM.tif")
                # water_depth = model.run_iteration(rain_mm=rain_input, dt_seconds=60)
                
                # Simulating processing time for demonstration
                time.sleep(2.5) 
                
                st.success("✅ Iteration complete! New cell values calculated.")
                st.info("Check your 'output/' folder for the updated water height rasters.")
                
            except Exception as e:
                st.error(f"An error occurred while running the script: {e}")

# ==========================================
# Page 3: Input Data
# ==========================================
elif page == "Input Data":
    st.title("📂 Model Input Data")
    st.write("The following datasets are currently registered in the local pipeline:")
    
    # Create two columns for a cleaner layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Elevation & Terrain")
        st.code("data/AHN_DTM.tif\ntmp/DEM.tif")
        
        # st.subheader("Hydrology")
        # st.code("data/BGT_Waterdelen.gpkg")

    with col2:
        st.subheader("Dynamic Routing Grids")
        st.code("tmp/Flow_Direction.tif\ntmp/Flow_Accumulation.tif")
        
        st.subheader("Surface Parameters")
        st.code("data/Ksat_Infiltration.tif")
        
    # Optional: Check if a crucial file actually exists on the local machine
    st.divider()
    if os.path.exists("tmp/Fused_DTM_DSM.tif"):
        st.success("Status: Fused DEM is ready on local disk.")
    else:
        st.warning("Status: Fused DEM not found. You may need to run the pre-processing step first.")