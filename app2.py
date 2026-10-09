import streamlit as st
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import time
import os

# Set up the overall page configuration
st.set_page_config(page_title="Flood Assessment Model", layout="wide")

# ==========================================
# Sidebar Navigation
# ==========================================
st.sidebar.title("Navigation")
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
    1. Check the baseline spatial grids on the **Input Data** page.
    2. Navigate to the **Simulation** page.
    3. Adjust the rainfall slider to your desired storm event.
    4. Click **Calculate** to trigger the local routing engine and view the flood risk map.
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
    if st.button("Calculate Flood Risk", type="primary"):
        with st.spinner(f"Running iteration for {rain_input} mm of rain..."):
            
            # --- CONNECT YOUR ENGINE HERE ---
            # import engine
            # model = engine.CatchmentModel("tmp/DEM.tif")
            # final_water_depth = model.run_iteration(rain_mm=rain_input, dt_seconds=60)
            # model.export_raster(final_water_depth, "output/flood_risk.tif")
            
            # Simulating processing time
            time.sleep(2) 
            st.success("✅ Iteration complete! Generating Flood Risk Map...")
            
            # Plot the resulting flood risk map
            # (Assuming your engine outputs a file called flood_risk.tif or similar)
            output_file = "output/flood_risk.tif"
            
            fig, ax = plt.subplots(figsize=(10, 8))
            if os.path.exists(output_file):
                with rasterio.open(output_file) as src:
                    # Mask out areas with zero water so the basemap/background shows through
                    data = src.read(1)
                    water_data = np.ma.masked_where(data <= 0.01, data)
                    
                    im = ax.imshow(water_data, cmap="Blues")
                    ax.set_title(f"Flood Risk Map ({rain_input} mm event)")
                    fig.colorbar(im, ax=ax, label="Water Depth (mm)")
                    ax.axis("off")
            else:
                # Placeholder if the engine isn't connected yet
                ax.text(0.5, 0.5, "output/flood_risk.tif not found.\n(Connect your engine.py to generate it)", 
                        ha='center', va='center', fontsize=12)
                ax.axis("off")
                
            st.pyplot(fig)
            plt.close(fig) # Close the figure to free up memory

# ==========================================
# Page 3: Input Data
# ==========================================
elif page == "Input Data":
    st.title("📂 Model Input Data")
    st.write("Current condition of the dynamic routing grids loaded into the pipeline:")
    
    # Create the 3-panel plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. Conditioned DEM
    if os.path.exists("tmp/DEM.tif"):
        with rasterio.open("tmp/DEM.tif") as src:
            show(src, ax=axes[0], cmap="terrain", title="1. Conditioned DEM\n(Elevation)")
    else:
        axes[0].text(0.5, 0.5, "tmp/DEM.tif not found", ha='center')
        axes[0].axis("off")

    # 2. Flow Direction
    if os.path.exists("tmp/flowdir.tif"):
        with rasterio.open("tmp/flowdir.tif") as src:
            show(src, ax=axes[1], cmap="tab10", title="2. Flow Direction\n(D8 Pointers)")
    else:
        axes[1].text(0.5, 0.5, "tmp/flowdir.tif not found", ha='center')
        axes[1].axis("off")

    # 3. Flow Accumulation
    if os.path.exists("tmp/accumulation.tif"):
        with rasterio.open("tmp/accumulation.tif") as src:
            acc_data = src.read(1)
            # Log transform for visibility of stream network
            acc_log = np.log1p(np.where(acc_data > 0, acc_data, 0))
            axes[2].imshow(acc_log, cmap="Blues")
            axes[2].set_title("3. Flow Accumulation\n(Log Scale)")
            axes[2].axis("off")
    else:
        axes[2].text(0.5, 0.5, "tmp/accumulation.tif not found", ha='center')
        axes[2].axis("off")

    plt.tight_layout()
    
    # Inject the multi-panel plot into Streamlit
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free up memory