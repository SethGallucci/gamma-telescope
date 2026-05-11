import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv() 

DATABRICKS_URL = os.environ.get("DATABRICKS_URL")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")

st.set_page_config(page_title="MAGIC Gamma Telescopes Classifier", page_icon="🔭", layout="wide")

# Inject Custom CSS for Dimmed Starry Background
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    /* Maintained the 0.65 dark overlay opacity to keep the background visible but not overpowering */
    background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?q=80&w=3000&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
/* Subtle dark overlay to ensure text readability against the stars */
.stMarkdown, .stExpander {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 5px;
    padding: 5px;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Initialize session state variables
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

if "k_length" not in st.session_state: st.session_state.k_length = 25.0
if "k_alpha" not in st.session_state: st.session_state.k_alpha = 15.0
if "k_size" not in st.session_state: st.session_state.k_size = 2.5
if "k_conc1" not in st.session_state: st.session_state.k_conc1 = 0.3
if "k_m3long" not in st.session_state: st.session_state.k_m3long = 15.0

# Callback functions for preset buttons
def load_gamma_preset():
    st.session_state.k_length = 22.0
    st.session_state.k_alpha = 5.0
    st.session_state.k_size = 2.8
    st.session_state.k_conc1 = 0.45
    st.session_state.k_m3long = 8.0

def load_hadron_preset():
    st.session_state.k_length = 135.0
    st.session_state.k_alpha = 75.0
    st.session_state.k_size = 3.5
    st.session_state.k_conc1 = 0.12
    st.session_state.k_m3long = 42.0

st.title("MAGIC Gamma Ray Telescopes Dashboard")
st.markdown("""
Welcome to the Cherenkov Radiation Analysis Dashboard. Adjust the 5 highly-predictive sensor metrics below to simulate a particle detection event. 
The Databricks Serverless MLOps endpoint will assemble the raw data and classify whether the atmospheric shower was caused by a primary **Gamma ray (signal)** or a **Hadronic cosmic ray (background)**.
""")

with st.expander("What am I looking at?"):
    st.write("""
    When high-energy particles from deep space hit our upper atmosphere, they create a brief, faint flash of blue light known as Cherenkov radiation. 
    Telescopes on the ground take incredibly fast pictures of these light flashes. Because background cosmic rays (Hadrons) bombard us constantly, 
    scientists use AI to look at the shape of the light blob in the image to filter out the background noise and identify the rare, highly energetic Gamma rays.
    """)

st.divider()

col_inputs, col_viz, col_history = st.columns([1.2, 1.5, 1.2], gap="large")

with col_inputs:
    st.markdown("<h3 style='text-align: center;'>Sensor Metrics</h3>", unsafe_allow_html=True)
    
    # Preset Buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Load Typical Gamma", on_click=load_gamma_preset, use_container_width=True)
    with btn_col2:
        st.button("Load Typical Hadron", on_click=load_hadron_preset, use_container_width=True)
    
    st.write("") 
    
    f_length = st.slider("f_length (Major axis)", 0.0, 350.0, step=1.0, key="k_length", help="The length of the light flash.")
    f_alpha = st.slider("f_alpha (Angle of major axis)", 0.0, 90.0, step=1.0, key="k_alpha", help="The angle at which the shower points toward the camera's center.")
    f_size = st.slider("f_size (Log of sum of pixels)", 1.0, 4.5, step=0.1, key="k_size", help="The overall brightness or intensity of the light flash.")
    f_conc1 = st.slider("f_conc1 (Ratio of highest pixel)", 0.0, 1.0, step=0.01, key="k_conc1", help="How concentrated the light is in the brightest single pixel.")
    f_m3long = st.slider("f_m3long (3rd root moment long)", -50.0, 50.0, step=1.0, key="k_m3long", help="A measure of the asymmetry of the light flash.")

    st.write("")
    
    # We assign the button to a variable here, but run the logic in the next column
    classify_clicked = st.button("Classify Particle", type="primary", use_container_width=True)


with col_viz:
    st.markdown("<h3 style='text-align: center;'>Geometry Profile</h3>", unsafe_allow_html=True)
    categories = ['Length', 'Alpha', 'Size', 'Concentration', 'M3Long']
    values = [f_length, f_alpha, f_size * 20, f_conc1 * 100, abs(f_m3long)]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        line_color='#00d4ff',
        fillcolor='rgba(0, 212, 255, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig, use_container_width=True)

    # The classification logic is executed here, so the alert renders directly under the visualization
    if classify_clicked:
        with st.spinner("Connecting to Endpoint..."):
            payload = {
                "dataframe_records": [{
                    "f_length": f_length, "f_size": f_size, "f_conc1": f_conc1, 
                    "f_m3long": f_m3long, "f_alpha": f_alpha
                }]
            }
            headers = {
                "Authorization": f"Bearer {DATABRICKS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(DATABRICKS_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    prediction = response.json()["predictions"][0]
                    class_result = "Gamma Ray" if prediction == 0.0 else "Hadron"
                    
                    # Update History State
                    new_record = {
                        "Length": f_length, "Alpha": f_alpha, "Size": f_size, 
                        "Conc1": f_conc1, "M3Long": f_m3long, "Result": class_result
                    }
                    st.session_state.prediction_history.insert(0, new_record)
                    if len(st.session_state.prediction_history) > 10:
                        st.session_state.prediction_history = st.session_state.prediction_history[:10]
                    
                    # Display contextual success/warning message (Now renders in col_viz!)
                    if prediction == 0.0:
                        st.success("**Gamma Ray Detected!** Originates from extreme cosmic events.")
                    else:
                        st.warning("**Hadron Detected!** Standard cosmic background radiation.")
                else:
                    st.error(f"Error {response.status_code}: Databricks rejected the request.")
            except requests.exceptions.RequestException as e:
                st.error("Failed to reach the Databricks URL.")


with col_history:
    st.markdown("<h3 style='text-align: center;'>Classification History</h3>", unsafe_allow_html=True)
    
    if st.session_state.prediction_history:
        df_history = pd.DataFrame(st.session_state.prediction_history)
        
        def highlight_results(val):
            color = 'rgba(0, 212, 255, 0.7)' if val == 'Gamma Ray' else 'rgba(0, 0, 0, 0)'
            return f'background-color: {color}; color: white; font-weight: bold'

        # Chain .format() to format the specific numeric columns to 2 decimal places
        styled_df = (
            df_history.style
            .format("{:.2f}", subset=['Length', 'Alpha', 'Size', 'Conc1', 'M3Long'])
            .map(highlight_results, subset=['Result'])
        )
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("Adjust sliders and click ***Classify Particle*** to begin.")

st.divider()

st.subheader("About the Data Source")
st.markdown("""
The simulated data for this classifier is based on readings from the **MAGIC (Major Atmospheric Gamma Imaging Cherenkov)** telescopes. 
Located at the Roque de los Muchachos Observatory on La Palma in the Canary Islands, MAGIC consists of two massive 17-meter reflector telescopes. 

Rather than looking directly at stars, these telescopes observe the Earth's atmosphere. They act as giant cameras that capture the faint, fleeting flashes of Cherenkov radiation produced when high-energy particles strike the air. By analyzing the shape and intensity of these flashes, scientists can separate the signals of extreme astronomical events (Gamma rays) from the noise of standard space weather (Hadrons).

Learn more about the MAGIC Telescopes: [Official Website (Max Planck Institute)](https://magic.mpp.mpg.de/) or [Wikipedia](https://en.wikipedia.org/wiki/MAGIC_(telescope))
""")

components.html(
    """<iframe src="https://www.google.com/maps/embed?pb=!4v1778470723138!6m8!1m7!1sCAoSFkNJSE0wb2dLRUlDQWdJRHF0Yi1kU0E.!2m2!1d28.76225851585105!2d-17.89186482756159!3f153.25805237594562!4f12.011002234598209!5f0.7820865974627469" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>""",
    height=450,
)
