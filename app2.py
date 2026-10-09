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
elif page == "Simulation Dashboard":
    st.title("⚙️ Flood Simulation")
    
    # Split the screen: Controls on the left (25%), Map on the right (75%)
    col_controls, col_map = st.columns([1, 3])
    
    with col_controls:
        st.subheader("Storm Parameters")
        rain_input = st.slider("Rainfall Amount (mm)", min_value=0.0, max_value=150.0, value=50.0, step=5.0)
        
        run_btn = st.button("Calculate Routing", type="primary", use_container_width=True)
        
    with col_map:
        if run_btn:
            with st.spinner(f"Simulating {rain_input} mm of rainfall..."):
                # --- RUN YOUR ENGINE HERE ---
                # import engine
                # model = engine.CatchmentModel("tmp/Fused_DTM_DSM.tif")
                # water_depth = model.run_iteration(rain_mm=rain_input, dt_seconds=60)
                
                # Simulating processing time for demonstration
                time.sleep(2.5) 
                
                st.success("Simulation complete! Surface water accumulation rendered below.")
                
                # Render the resulting output raster directly into the webpage
                m = leafmap.Map(center=[51.9692, 5.6667], zoom=13)
                
                # Check if the output file actually exists to display it
                output_raster = "output/Flow_Accumulation.tif"
                if os.path.exists(output_raster):
                    m.add_raster(output_raster, colormap="Blues", layer_name="Flood Accumulation")
                else:
                    m.add_basemap("OpenTopoMap")
                    st.warning("Displaying basemap. Run the engine to generate the accumulation raster.")
                    
                m.to_streamlit(height=600)
        else:
            # Show a blank starting map before calculation
            st.info("Adjust the parameters on the left and click Calculate to view the projection.")
            m = leafmap.Map(center=[51.9692, 5.6667], zoom=13)
            m.add_basemap("OpenStreetMap")
            m.to_streamlit(height=600)

# ==========================================
# Page 3: Input Data
# ==========================================
elif page == "Baseline Terrain":
    st.title("🗺️ Baseline Terrain Model")
    st.write("This map displays the conditioned elevation model (buildings acting as flow barriers) used as the foundation for the routing algorithms.")
    
    # Render the input raster directly instead of showing file paths
    m_input = leafmap.Map(center=[51.9692, 5.6667], zoom=13)
    
    fused_dem = "tmp/DEM.tif"
    if os.path.exists(fused_dem):
        m_input.add_raster(fused_dem, colormap="terrain", layer_name="Conditioned Elevation")
    else:
        m_input.add_basemap("OpenTopoMap")
        st.warning("Elevation model not found on disk. Displaying standard basemap.")
        
    m_input.to_streamlit(height=650)