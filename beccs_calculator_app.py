import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def calculate_beccs_carbon_credits(biomass_type, biomass_quantity_tons, capture_efficiency, calorific_value, moisture_content, emission_factor):
    """
    Calculate potential carbon credits for a BECCS project with biomass-specific parameters.
    
    Parameters:
    - biomass_type (str): Type of biomass
    - biomass_quantity_tons (float): Biomass input in tons
    - capture_efficiency (float): CO2 capture efficiency (0 to 1)
    - calorific_value (float): Energy content in MJ/kg
    - moisture_content (float): Moisture percentage (0 to 1)
    - emission_factor (float): CO2 emissions per ton of biomass (tCO2/ton)
    
    Returns:
    - dict: Results with calculated outputs only
    """
    # Adjust calorific value for moisture
    effective_calorific_value = calorific_value * (1 - moisture_content)
    
    # Calculate energy output (30% conversion efficiency to electricity)
    conversion_efficiency = 0.3
    energy_output_mwh = (biomass_quantity_tons * effective_calorific_value * 1000 * conversion_efficiency) / 3600
    
    # Calculate CO2 captured
    total_co2_emitted = biomass_quantity_tons * emission_factor
    co2_captured = total_co2_emitted * capture_efficiency
    
    # Carbon credits (equal to CO2 captured, in tons)
    carbon_credits = co2_captured
    
    # Energy efficiency
    energy_efficiency = energy_output_mwh / biomass_quantity_tons if biomass_quantity_tons > 0 else 0
    
    results = {
        'CO2 Captured (tons)': round(co2_captured, 2),
        'Carbon Credits (credits)': round(carbon_credits, 2),
        'Energy Output (MWh)': round(energy_output_mwh, 2),
        'Energy Efficiency (MWh/ton)': round(energy_efficiency, 2)
    }
    
    return results

def visualize_results(results):
    """
    Create a bar chart to visualize Energy Output and Carbon Credits.
    """
    labels = ['Energy Output (MWh)', 'Carbon Credits (credits)']
    values = [results['Energy Output (MWh)'], results['Carbon Credits (credits)']]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=['orange', 'blue'])
    ax.set_title("BECCS Energy and Carbon Credit Results")
    ax.set_ylabel('Value')
    ax.grid(axis='y')
    return fig

def main():
    st.set_page_config(page_title="BECCS Carbon Credit Calculator", layout="wide")
    st.title("BECCS Carbon Credit Calculator")
    st.markdown("Estimate carbon credits and energy output for Bioenergy with Carbon Capture and Storage (BECCS) projects.")

    # Sidebar for inputs
    with st.sidebar:
        st.header("Input Parameters")
        
        biomass_type = st.text_input("Biomass Type (e.g., hardwood, corn_stover, algae)", value="hardwood")
        
        biomass_quantity = st.number_input("Biomass Quantity (tons)", min_value=0.0, value=50.0, step=1.0)
        
        calorific_value = st.number_input("Calorific Value (MJ/kg)", min_value=0.0, value=18.0, step=0.1)
        
        moisture_content = st.slider("Moisture Content (%)", min_value=0, max_value=100, value=10) / 100.0
        
        emission_factor = st.number_input("Emission Factor (tCO2/ton)", min_value=0.0, value=1.76, step=0.01)
        
        capture_efficiency = st.slider("Capture Efficiency (%)", min_value=0, max_value=100, value=85) / 100.0

    # Validate inputs
    error = None
    if not biomass_type.strip():
        error = "Biomass type cannot be empty."
    elif biomass_quantity <= 0:
        error = "Biomass quantity must be positive."
    elif calorific_value <= 0:
        error = "Calorific value must be positive."
    elif emission_factor <= 0:
        error = "Emission factor must be positive."

    if error:
        st.error(error)
    else:
        # Calculate results
        try:
            results = calculate_beccs_carbon_credits(
                biomass_type, biomass_quantity, capture_efficiency,
                calorific_value, moisture_content, emission_factor
            )
            
            # Display results
            st.header("Results")
            st.table(pd.DataFrame([results]))
            
            # Display chart
            st.header("Visualization")
            fig = visualize_results(results)
            st.pyplot(fig)
            
            # Save and provide download button for CSV
            df = pd.DataFrame([results])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv_buffer.getvalue(),
                file_name="beccs_results.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()