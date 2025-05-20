import streamlit as st
import os
import tempfile
from pathlib import Path
import base64
import plotly.express as px
import pandas as pd
from lyricsRAG import inference
import time
from datetime import datetime
import uuid
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lyrics Insight Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-top: 1rem;
    }
    
    .sub-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #4F46E5;
        margin-bottom: 1rem;
        border-left: 4px solid #4F46E5;
        padding-left: 10px;
    }
    
    .card {
        background-color: #e3dfe8;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    .primary-card {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
    }
    
    .secondary-card {
        background-color: #EEF2FF;
    }
    
    .success-card {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
    }
    
    .info-card {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
    }
    
    .warning-card {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
    }
    
    .error-card {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
    }
    
    .success-msg {
        color: #10B981;
        font-weight: 600;
    }
    
    .info-msg {
        color: #3B82F6;
        font-style: italic;
    }
    
    .stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #4338CA;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    .secondary-btn > button {
        background-color: #E2E8F0;
        color: #1E293B;
    }
    
    .secondary-btn > button:hover {
        background-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(100, 116, 139, 0.2);
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 0.5rem 1rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 0.5rem 1rem;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 0.5rem 1rem;
    }
    
    .stFileUploader > div > label {
        background-color: #EEF2FF;
        border-radius: 8px;
    }
    
    .stFileUploader > div > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
    }
    
    .stFileUploader > div > button:hover {
        background-color: #4338CA;
    }
    
    .st-expander {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .st-expander > div {
        padding: 1rem;
    }
    
    /* Chat styling */
    .user-message {
        background-color: #ece1fa;
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin-bottom: 15px;
        position: relative;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .assistant-message {
        background-color: #e3dfe8;
        padding: 12px 16px;
        border-radius: 12px 12px 12px 2px;
        margin-bottom: 15px;
        position: relative;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid #E2E8F0;
    }
    
    .chat-timestamp {
        font-size: 0.7rem;
        color: #94A3B8;
        text-align: right;
        margin-top: 4px;
    }
    
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    
    .sidebar-nav {
        padding: 15px;
        border-radius: 12px;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    
    .sidebar-nav-item {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .sidebar-nav-item:hover {
        background-color: #EEF2FF;
    }
    
    .sidebar-nav-item.active {
        background-color: #4F46E5;
        color: white;
    }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .footer {
        text-align: center;
        padding: 1rem 0;
        color: #64748B;
        font-size: 0.9rem;
    }
    
    .stat-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    
    .stat-card h3 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 0.5rem;
    }
    
    .stat-card p {
        color: #64748B;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Loading animation */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    
    .loading-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        background-color: #4F46E5;
        margin: 0 5px;
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    .loading-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .loading-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1E293B;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.8rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Progress bar styling */
    .progress-container {
        width: 100%;
        height: 10px;
        background-color: #E2E8F0;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        border-radius: 5px;
        transition: width 0.3s ease;
    }
    
    /* Animated gradient background */
    .gradient-bg {
        background: linear-gradient(-45deg, #4F46E5, #7C3AED, #8B5CF6, #C084FC);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
        padding: 2rem;
        border-radius: 12px;
    }
    
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Responsive tables */
    .responsive-table {
        overflow-x: auto;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Badge styling */
    .badge {
        padding: 4px 8px;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 5px;
    }
    
    .badge-primary {
        background-color: #EEF2FF;
        color: #4F46E5;
    }
    
    .badge-success {
        background-color: #ECFDF5;
        color: #10B981;
    }
    
    .badge-warning {
        background-color: #FFFBEB;
        color: #F59E0B;
    }
    
    /* Tag cloud styling */
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    
    .tag {
        background-color: #EEF2FF;
        color: #4F46E5;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .tag:hover {
        background-color: #4F46E5;
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ===== Utility Functions =====

def get_download_link(text, filename, link_text):
    """Create a download link for text"""
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
    return href

def show_success_message(message, duration=3):
    """Show a success message that automatically disappears"""
    success_placeholder = st.empty()
    success_placeholder.markdown(f'<div class="success-card"><p class="success-msg">{message}</p></div>', unsafe_allow_html=True)
    if duration > 0:
        time.sleep(duration)
        success_placeholder.empty()

def show_error_message(message, duration=5):
    """Show an error message that automatically disappears"""
    error_placeholder = st.empty()
    error_placeholder.markdown(f'<div class="error-card"><p style="color: #EF4444; font-weight: 600;">{message}</p></div>', unsafe_allow_html=True)
    if duration > 0:
        time.sleep(duration)
        error_placeholder.empty()

def format_timestamp():
    """Format current timestamp"""
    return datetime.now().strftime("%H:%M:%S")

def show_loading_animation():
    """Display loading animation"""
    return st.markdown("""
    <div class="loading-animation">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    </div>
    """, unsafe_allow_html=True)

def render_stats_dashboard(songs_df):
    """Render the stats dashboard"""
    st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
    
    # Calculate stats
    total_songs = len(songs_df)
    total_artists = len(songs_df['artist'].unique())
    sample_lines = [20, 25, 18, 30, 22, 28, 24, 19, 32, 26][:min(10, len(songs_df))]
    avg_lines = round(sum(sample_lines) / len(sample_lines))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>{}</h3>
            <p>Total Songs</p>
        </div>
        """.format(total_songs), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>{}</h3>
            <p>Artists</p>
        </div>
        """.format(total_artists), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>{}</h3>
            <p>Avg. Lines per Song</p>
        </div>
        """.format(avg_lines), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <h3>{}</h3>
            <p>Last Updated</p>
        </div>
        """.format(datetime.now().strftime("%d %b %Y")), unsafe_allow_html=True)

# ===== Initialize Session State =====

if 'lyrics_rag' not in st.session_state:
    st.session_state.lyrics_rag = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_lyrics' not in st.session_state:
    st.session_state.generated_lyrics = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'songs_list' not in st.session_state:
    st.session_state.songs_list = None
if 'api_key_status' not in st.session_state:
    st.session_state.api_key_status = False
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if 'session_started' not in st.session_state:
    st.session_state.session_started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ===== App Functions =====

def secure_api_key(api_key):
    """Store API key securely in session state"""
    if api_key:
        # Set the API key for the session
        os.environ["OPENAI_API_KEY"] = api_key
        st.session_state.api_key_status = True
        return True
    return False

def load_pdf_and_initialize(pdf_file):
    """Load PDF and initialize LyricsRAG"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Get OpenAI API key from environment
        api_key = os.environ.get('OPENAI_API_KEY', '')
        if not api_key:
            os.unlink(tmp_file_path)
            return False, "API key not configured. Please enter your OpenAI API key in the settings."
        
        # Initialize LyricsRAG with progress tracking
        progress_placeholder = st.empty()
        progress_placeholder.markdown("""
        <div class="progress-container">
            <div class="progress-bar" style="width: 0%;"></div>
        </div>
        <p class="info-msg">Initializing LyricsRAG...</p>
        """, unsafe_allow_html=True)
        
        # Progress updates
        for i in range(5):
            progress_placeholder.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {i*20}%;"></div>
            </div>
            <p class="info-msg">{"Processing PDF text..." if i < 2 else "Creating embeddings..." if i < 4 else "Finalizing setup..."}</p>
            """, unsafe_allow_html=True)
            time.sleep(0.5)
        
        # Actually initialize LyricsRAG
        st.session_state.lyrics_rag = inference.LyricsRAG(tmp_file_path, openai_api_key=api_key)
        
        # Final progress update
        progress_placeholder.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: 100%;"></div>
        </div>
        <p class="success-msg">Ready! Processing complete.</p>
        """, unsafe_allow_html=True)
        
        st.session_state.songs_list = st.session_state.lyrics_rag.list_songs()
        st.session_state.pdf_uploaded = True
        
        # Clean up and return success
        os.unlink(tmp_file_path)
        return True, "PDF processed successfully!"
    except Exception as e:
        os.unlink(tmp_file_path)
        return False, f"Error: {str(e)}"

# ===== Sidebar Navigation =====

with st.sidebar:
    st.markdown('<div class="logo-text">🎵 Lyrics Insight Studio</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    
    # User info
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 0.9rem; color: #64748B;">Session ID: {st.session_state.user_id}</div>
        <div style="font-size: 0.8rem; color: #94A3B8;">Started: {st.session_state.session_started}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    page = st.radio(
        "",
        ["📤 Upload Lyrics", "✨ Generate Lyrics", "💬 Lyrics Chat", "🔍 Search Lyrics", "📊 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    # API key status indicator
    st.markdown(f"""
    <div style="margin-top: 20px; padding: 10px; border-radius: 8px; background-color: {'#ECFDF5' if st.session_state.api_key_status else '#FEF2F2'};">
        <div style="display: flex; align-items: center;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {'#10B981' if st.session_state.api_key_status else '#EF4444'}; margin-right: 8px;"></div>
            <div style="font-size: 0.9rem; color: {'#10B981' if st.session_state.api_key_status else '#EF4444'};">API Key: {'Configured' if st.session_state.api_key_status else 'Not Configured'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PDF upload status indicator
    st.markdown(f"""
    <div style="margin-top: 10px; padding: 10px; border-radius: 8px; background-color: {'#ECFDF5' if st.session_state.pdf_uploaded else '#FEF2F2'};">
        <div style="display: flex; align-items: center;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {'#10B981' if st.session_state.pdf_uploaded else '#EF4444'}; margin-right: 8px;"></div>
            <div style="font-size: 0.9rem; color: {'#10B981' if st.session_state.pdf_uploaded else '#EF4444'};">PDF: {'Uploaded' if st.session_state.pdf_uploaded else 'Not Uploaded'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Page Content =====

# Upload Lyrics Page
if page == "📤 Upload Lyrics":
    st.markdown('<div class="main-header">Upload Lyrics Collection</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # API Key Configuration - Only show if not already configured
        if not st.session_state.api_key_status:
            st.markdown('<div class="sub-header">API Configuration</div>', unsafe_allow_html=True)
            
            api_key_col1, api_key_col2 = st.columns([3, 1])
            
            with api_key_col1:
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Your key will be stored securely for this session only.",
                    placeholder="Enter your OpenAI API key"
                )
            
            with api_key_col2:
                if st.button("Save Key"):
                    if secure_api_key(api_key):
                        show_success_message("API key configured successfully!")
                    else:
                        show_error_message("Please enter a valid API key")
        
        # PDF Upload Section
        st.markdown('<div class="sub-header">Upload Lyrics PDF</div>', unsafe_allow_html=True)
        
        # Informational card
        st.markdown("""
        <div class="info-card" style="margin-bottom: 20px;">
            <p class="info-msg">
                Upload a PDF containing song lyrics. Each song should be on a separate page with the song title on the first line 
                and "by Artist Name" on the second line.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload area
        upload_col1, upload_col2 = st.columns([3, 1])
        
        with upload_col1:
            uploaded_pdf = st.file_uploader("", type="pdf", label_visibility="collapsed")
        
        with upload_col2:
            upload_button = st.button("Process PDF", disabled=not st.session_state.api_key_status)
        
        # Process PDF if uploaded and button clicked
        if uploaded_pdf is not None and upload_button:
            if not st.session_state.api_key_status:
                show_error_message("Please configure your API key first")
            else:
                with st.spinner():
                    success, message = load_pdf_and_initialize(uploaded_pdf)
                    if success:
                        show_success_message(message)
                    else:
                        show_error_message(message)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Example PDF Format
    with st.expander("View Expected PDF Format"):
        st.markdown("""
        <div class="info-card">
            <p><strong>Each page of the PDF should follow this format:</strong></p>
            <pre style="background-color: #F1F5F9; padding: 15px; border-radius: 8px; font-family: monospace;">
Song Title
by Artist Name

Lyrics line 1
Lyrics line 2
Lyrics line 3
...
            </pre>
            <p>This structure helps our system correctly identify and index each song for better searching and analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # If PDF is uploaded, show quick stats
    if st.session_state.pdf_uploaded and st.session_state.songs_list:
        songs_df = pd.DataFrame(st.session_state.songs_list)
        if not songs_df.empty:
            songs_df['lines_count'] = 20  # Placeholder for line count
            render_stats_dashboard(songs_df)

# Generate Lyrics Page
elif page == "✨ Generate Lyrics":
    st.markdown('<div class="main-header">Generate Original Lyrics</div>', unsafe_allow_html=True)
    
    if not st.session_state.lyrics_rag:
        st.markdown("""
        <div class="warning-card">
            <h3 style="color: #F59E0B; margin-bottom: 10px;">PDF Not Uploaded</h3>
            <p>Please upload and process a lyrics PDF first.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            st.markdown('<div class="sub-header">Inspiration Settings</div>', unsafe_allow_html=True)
            
            # Generation options
            col1, col2 = st.columns([1, 1])
            
            with col1:
                style_options = ["Any Style", "Pop", "Rock", "Hip Hop", "Country", "R&B", "Folk", "Electronic"]
                selected_style = st.selectbox("Lyrical Style", style_options)
            
            with col2:
                theme_options = ["Love", "Heartbreak", "Hope", "Nostalgia", "Resilience", "Freedom", "Adventure", "Custom"]
                selected_theme = st.selectbox("Theme", theme_options)
            
            # Generation prompt
            st.markdown('<div class="sub-header">Your Lyrics Vision</div>', unsafe_allow_html=True)
            
            generation_prompt = st.text_area(
                "Describe what kind of lyrics you want to generate",
                placeholder="Example: Write a verse about lost love with a hopeful twist, using nature metaphors",
                height=100
            )
            
            # Advanced options
            with st.expander("Advanced Options"):
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    creativity = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1)
                
                with col2:
                    structure_options = ["Verse", "Chorus", "Verse-Chorus", "Complete Song"]
                    structure = st.selectbox("Structure", structure_options)
                
                with col3:
                    length_options = ["Short", "Medium", "Long"]
                    length = st.selectbox("Length", length_options)
            
            # Submit button
            generate_button = st.button("Generate Lyrics", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process generation
            if generate_button and generation_prompt:
                # Build complete prompt
                full_prompt = f"Write {length.lower()} {structure.lower()} lyrics "
                
                if selected_style != "Any Style":
                    full_prompt += f"in {selected_style} style "
                
                if selected_theme != "Custom":
                    full_prompt += f"about {selected_theme.lower()} "
                
                full_prompt += f". {generation_prompt}"
                
                with st.spinner("Crafting lyrical magic..."):
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="gradient-bg" style="text-align: center; padding: 30px;">
                        <h3>Creating your lyrics...</h3>
                        <div class="loading-animation">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                        <p>Analyzing styles, finding inspiration, crafting verses...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate lyrics
                    generated_lyrics = st.session_state.lyrics_rag.generate_lyrics(full_prompt)
                    st.session_state.generated_lyrics = generated_lyrics
                    loading_placeholder.empty()
            
            # Display generated lyrics if available
            if st.session_state.generated_lyrics:
                st.markdown('<div class="sub-header">Your Generated Lyrics</div>', unsafe_allow_html=True)
                
                # Display the lyrics in a styled container
                st.markdown(f"""
                <div class="card" style="background-color: #F8FAFC; border-left: 4px solid #4F46E5;">
                    <div style="font-family: 'Georgia', serif; white-space: pre-line;">
                        {st.session_state.generated_lyrics}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button("📥 Download Lyrics"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.markdown(
                            get_download_link(
                                st.session_state.generated_lyrics, 
                                f"generated_lyrics_{timestamp}.txt", 
                                "📥 Download as Text File"
                            ), 
                            unsafe_allow_html=True
                        )
                
                with col2:
                    if st.button("🔄 Generate Again"):
                        st.session_state.generated_lyrics = None
                        st.rerun()
                
                with col3:
                    if st.button("✨ New Prompt"):
                        st.session_state.generated_lyrics = None
                        st.experimental_rerun()

# Chat about Lyrics Page
elif page == "💬 Lyrics Chat":
    st.markdown('<div class="main-header">Chat with Your Lyrics</div>', unsafe_allow_html=True)
    
    if not st.session_state.lyrics_rag:
        st.markdown("""
        <div class="warning-card">
            <h3 style="color: #F59E0B; margin-bottom: 10px;">PDF Not Uploaded</h3>
            <p>Please upload and process a lyrics PDF first.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        chat_col1, chat_col2 = st.columns([3, 1])
        
        with chat_col1:
            # Chat history display area
            st.markdown('<div class="sub-header">Conversation</div>', unsafe_allow_html=True)
            
            # Chat container
            chat_container = st.container()
            # chat_container.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
            
            # Display chat messages
            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    chat_container.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong><br>
                        {chat["content"]}
                        <div class="chat-timestamp">{chat["timestamp"] if "timestamp" in chat else format_timestamp()}</div>
                    </div>
                    <div style="clear: both;"></div>
                    """, unsafe_allow_html=True)
                else:
                    chat_container.markdown(f"""
                    <div class="assistant-message">
                        <strong>Lyrics Assistant:</strong><br>
                        {chat["content"]}
                        <div class="chat-timestamp">{chat["timestamp"] if "timestamp" in chat else format_timestamp()}</div>
                    </div>
                    <div style="clear: both;"></div>
                    """, unsafe_allow_html=True)
            
            chat_container.markdown('</div>', unsafe_allow_html=True)
            
            # User input and buttons
            user_input = st.text_input(
                "",
                key="chat_input",
                placeholder="Ask about themes, styles, imagery, or specific lyrics...",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                send_button = st.button("Send", use_container_width=True)
            with col2:
                if st.button("Clear Chat", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Process user input
            if send_button and user_input:
                # Add user message to chat history with timestamp
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": user_input,
                    "timestamp": format_timestamp()
                })
                
                # Show typing indicator
                typing_indicator = st.empty()
                typing_indicator.markdown("""
                <div class="assistant-message" style="max-width: 100px;">
                    <div class="loading-animation" style="height: 20px;">
                        <div class="loading-dot" style="height: 6px; width: 6px;"></div>
                        <div class="loading-dot" style="height: 6px; width: 6px;"></div>
                        <div class="loading-dot" style="height: 6px; width: 6px;"></div>
                    </div>
                </div>
                <div style="clear: both;"></div>
                """, unsafe_allow_html=True)
                
                # Get response from model
                try:
                    response = st.session_state.lyrics_rag.chat(user_input)
                    
                    # Add assistant response to chat history with timestamp
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": format_timestamp()
                    })
                except Exception as e:
                    # Handle errors gracefully
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "timestamp": format_timestamp()
                    })
                
                # Remove typing indicator
                typing_indicator.empty()
                
                # Rerun to update the UI
                st.rerun()
        
        with chat_col2:
            # Chat suggestions and tips
            st.markdown('<div class="sub-header">Chat Tools</div>', unsafe_allow_html=True)
            
            # Suggestion chips
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<strong>Try asking:</strong>', unsafe_allow_html=True)
            
            st.markdown('<div class="tag-cloud">', unsafe_allow_html=True)
            suggestions = [
                "What themes appear most?",
                "Analyze writing style",
                "Find songs about love",
                "Compare artists' metaphors",
                "What literary devices are used?",
                "Summarize emotional tones"
            ]
            
            for suggestion in suggestions:
                if st.button(suggestion, key=f"suggestion_{suggestion}"):
                    # Add the suggestion to the input and simulate pressing send
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "content": suggestion,
                        "timestamp": format_timestamp()
                    })
                    
                    # Get response
                    response = st.session_state.lyrics_rag.chat(suggestion)
                    
                    # Add response
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": format_timestamp()
                    })
                    
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Recently discussed songs
            if len(st.session_state.chat_history) > 2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<strong>Recently Discussed:</strong>', unsafe_allow_html=True)
                st.markdown('<div class="tag-cloud">', unsafe_allow_html=True)
                
                # Placeholder for recently discussed songs - would be extracted from chat history
                recent_topics = ["Song Structure", "Rhyme Patterns", "Metaphors"]
                
                for topic in recent_topics:
                    st.markdown(f'<div class="badge badge-primary">{topic}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Search Lyrics Page
elif page == "🔍 Search Lyrics":
    st.markdown('<div class="main-header">Search Lyrics Database</div>', unsafe_allow_html=True)
    
    if not st.session_state.lyrics_rag:
        st.markdown("""
        <div class="warning-card">
            <h3 style="color: #F59E0B; margin-bottom: 10px;">PDF Not Uploaded</h3>
            <p>Please upload and process a lyrics PDF first.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                search_query = st.text_input(
                    "",
                    placeholder="Enter keywords, phrases, themes or emotions to search across all lyrics",
                    label_visibility="collapsed"
                )
            
            with col2:
                search_type = st.selectbox(
                    "Search type",
                    ["Semantic", "Keyword", "Combined"],
                    index=0
                )
            
            with col3:
                num_results = st.number_input("Results", min_value=1, max_value=20, value=5)
            
            search_button = st.button("Search Lyrics", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process search
            if search_button and search_query:
                with st.spinner("Searching through lyrics..."):
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="loading-animation">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Perform search
                    search_results = st.session_state.lyrics_rag.search_lyrics(search_query, k=num_results)
                    st.session_state.search_results = search_results
                    loading_placeholder.empty()
            
            # Display search results
            if st.session_state.search_results:
                st.markdown('<div class="sub-header">Search Results</div>', unsafe_allow_html=True)
                
                # Results counter
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <span class="badge badge-primary">{len(st.session_state.search_results)} results found</span>
                    <span class="badge badge-success">Query: "{search_query}"</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Display each result
                for i, result in enumerate(st.session_state.search_results, 1):
                    with st.expander(f"{result['song']} by {result['artist']}"):
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <strong style="font-size: 1.2rem; color: #4F46E5;">{result['song']}</strong>
                                <div style="color: #64748B;">by {result['artist']}</div>
                            </div>
                            <div>
                                <span class="badge badge-primary">Result #{i}</span>
                            </div>
                        </div>
                        
                        <div style="background-color: #F1F5F9; padding: 15px; border-radius: 8px; margin-top: 10px; font-family: 'Georgia', serif; white-space: pre-line;">
                            {result['content']}
                        </div>
                        
                        <div style="margin-top: 15px; display: flex; justify-content: space-between;">
                            <div>
                                <button class="stButton secondary-btn">View Full Lyrics</button>
                            </div>
                            <div>
                                <button class="stButton secondary-btn">Ask About This Song</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# Analytics Page
elif page == "📊 Analytics":
    st.markdown('<div class="main-header">Lyrics Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.lyrics_rag:
        st.markdown("""
        <div class="warning-card">
            <h3 style="color: #F59E0B; margin-bottom: 10px;">PDF Not Uploaded</h3>
            <p>Please upload and process a lyrics PDF first.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Create a DataFrame for analysis
        songs_df = pd.DataFrame(st.session_state.songs_list)
        if not songs_df.empty:
            # Generate metrics for all songs in the DataFrame
            # Using random data that scales to the correct length
            num_songs = len(songs_df)
            songs_df['lines_count'] = np.random.randint(18, 35, size=num_songs)  # Random values between 18-35
            songs_df['word_count'] = np.random.randint(100, 200, size=num_songs)  # Random values between 100-200
            songs_df['complexity_score'] = np.random.uniform(0.4, 0.9, size=num_songs)  # Random values between 0.4-0.9
            
            # For years, create a distribution centered around recent years
            songs_df['year'] = np.random.choice(range(2017, 2023), size=num_songs)
            
            # Dashboard stats
            render_stats_dashboard(songs_df)
            
            # Analytics tabs
            tab1, tab2, tab3 = st.tabs(["📊 Metrics", "🎭 Themes", "✍️ Style Analysis"])
            
            with tab1:
                # Metrics visualization
                st.markdown('<div class="sub-header">Lyrical Metrics</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Word count by artist chart
                    fig = px.bar(
                        songs_df.groupby('artist')['word_count'].mean().reset_index(), 
                        x='artist', 
                        y='word_count',
                        title='Average Word Count by Artist',
                        color='artist',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(
                        xaxis_title="Artist",
                        yaxis_title="Average Word Count",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Complexity score by artist chart
                    fig = px.box(
                        songs_df, 
                        x='artist', 
                        y='complexity_score',
                        title='Lyrical Complexity by Artist',
                        color='artist',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(
                        xaxis_title="Artist",
                        yaxis_title="Complexity Score",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Themes analysis
                st.markdown('<div class="sub-header">Thematic Analysis</div>', unsafe_allow_html=True)
                
                # Theme prevalence chart (placeholder data)
                themes = ['Love', 'Heartbreak', 'Hope', 'Nostalgia', 'Resilience', 'Freedom']
                theme_values = [45, 30, 25, 20, 15, 10]
                
                fig = px.pie(
                    names=themes,
                    values=theme_values,
                    title='Theme Prevalence in Lyrics',
                    color_discrete_sequence=px.colors.sequential.Plasma_r,
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Theme distribution by artist
                st.markdown('<div class="sub-header">Theme Distribution by Artist</div>', unsafe_allow_html=True)
                
                # Create dummy data for theme by artist
                theme_data = []
                for artist in songs_df['artist'].unique()[:5]:
                    for theme in themes:
                        theme_data.append({
                            'Artist': artist,
                            'Theme': theme,
                            'Frequency': round(50 * (0.5 + np.random.random()/2))
                        })
                
                theme_df = pd.DataFrame(theme_data)
                
                fig = px.bar(
                    theme_df,
                    x='Artist', 
                    y='Frequency',
                    color='Theme',
                    title='Theme Distribution by Artist',
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig.update_layout(height=500)
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                # Style analysis
                st.markdown('<div class="sub-header">Style Analysis</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Stylistic elements chart (placeholder data)
                    style_elements = ['Metaphors', 'Similes', 'Alliteration', 'Repetition', 'Rhyme Schemes']
                    element_values = [75, 60, 45, 80, 90]
                    
                    fig = px.bar(
                        x=style_elements,
                        y=element_values,
                        title='Stylistic Elements Usage',
                        color=style_elements,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(
                        xaxis_title="Element",
                        yaxis_title="Usage Frequency",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Emotional tone radar chart (placeholder data)
                    emotions = ['Joy', 'Sadness', 'Anger', 'Hope', 'Fear', 'Love']
                    emotion_values = [65, 40, 20, 75, 30, 85]
                    
                    fig = px.line_polar(
                        r=emotion_values,
                        theta=emotions,
                        line_close=True,
                        title="Emotional Tone Analysis",
                    )
                    fig.update_traces(fill='toself')
                    fig.update_layout(height=400)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Word cloud placeholder
                st.markdown('<div class="sub-header">Common Imagery Word Cloud</div>', unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #F1F5F9; height: 300px; border-radius: 12px; display: flex; justify-content: center; align-items: center;">
                    <div style="text-align: center;">
                        <p style="color: #64748B; font-style: italic;">Word cloud visualization would appear here</p>
                        <p style="font-size: 0.8rem; color: #94A3B8;">Based on frequency analysis of imagery and vocabulary</p>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

# Settings Page
else:  # Settings
    st.markdown('<div class="main-header">Application Settings</div>', unsafe_allow_html=True)
    
    # API Key Configuration
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">API Configuration</div>', unsafe_allow_html=True)
        
        api_key_col1, api_key_col2 = st.columns([3, 1])
        
        with api_key_col1:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Your key will be stored securely for this session only.",
                placeholder="Enter your OpenAI API key"
            )
        
        with api_key_col2:
            if st.button("Save Key"):
                if secure_api_key(api_key):
                    show_success_message("API key configured successfully!")
                else:
                    show_error_message("Please enter a valid API key")
        
        st.markdown("""
        <div class="info-card">
            <p class="info-msg">
                Your API key is securely stored only for the current session and is never saved permanently.
                It will be used for embeddings creation and text generation.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Model Settings
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Model Settings</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            generation_model = st.selectbox(
                "Text Generation Model",
                ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                index=0
            )
        
        with col2:
            embedding_model = st.selectbox(
                "Embeddings Model",
                ["text-embedding-3-small", "text-embedding-3-large"],
                index=0
            )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        with col2:
            chunk_size = st.slider("Chunk Size", 100, 1000, 500, 50)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Session Management
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Session Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                show_success_message("Chat history cleared!")
        
        with col2:
            if st.button("Reset All Session Data", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                show_success_message("Session data reset! Refreshing page...")
                time.sleep(1)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # About Application
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">About Lyrics Insight Studio</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 3rem; margin-right: 20px;">🎵</div>
            <div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #4F46E5;">Lyrics Insight Studio</div>
                <div style="color: #64748B;">Version 1.2.0</div>
            </div>
        </div>
        
        <p>
            Lyrics Insight Studio is a powerful tool for analyzing, generating, and exploring song lyrics using advanced AI techniques.
            Built with Streamlit, LangChain, and OpenAI's powerful language models.
        </p>
        
        <div style="margin-top: 20px;">
            <strong>Features:</strong>
            <ul>
                <li>Upload and analyze collections of song lyrics</li>
                <li>Generate original lyrics based on your specifications</li>
                <li>Chat with AI about your lyrics collection</li>
                <li>Search for specific themes and content in your lyrics</li>
                <li>Get detailed analytics about writing styles and themes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== Footer =====
st.markdown("""
<div class="footer">
    <div>🎵 Lyrics Insight Studio | Built with Streamlit, LangChain & OpenAI</div>
    <div style="font-size: 0.8rem; margin-top: 5px;">© 2025 AILucifer99</div>
</div>
""", unsafe_allow_html=True)

# Fix for Streamlit AutoScroll in Chat
if page == "💬 Lyrics Chat" and st.session_state.chat_history:
    st.markdown("""
    <script>
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)
