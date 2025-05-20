# Lyrics Insight Studio - Retrieval Augemented Generation for Music
LyricsInsightStudio 🎵✨ | Unlocking the Heart of Music with Retrieval-Augmented Generation. Dive deep into lyrics, discover hidden meanings, and craft melodies that resonate. Where technology meets creativity, one verse at a time. 🎤🚀

## The components for the Web Application

Application Home Page - 
---
![Lyrics Insight Studio](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Home.png)
---

Generate Original Lyrics - RAG Approach
---
![Original Lyrics Generation using RAG](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Generate-Original-Lyrics.png)
---


Lyrics Vectordata chat
---
![Chat with Lyrics](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Lyrics-VDB-Chat.png)
---


Analytics on the lyrics data
---
![Lyrics Data Analysis](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Lyrics-Analytics.png)
---


Search different lyrics - Hybrid Search on Vectordatabase
---
![Search Lyrics in the Vector Database](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Search-Lyrics-Database.png)
---

---
Application Settings
![Web Application Settings](https://github.com/AILucifer99/Lyrics-Insight-Studio/blob/main/architecture/Settings.png)
---

## 📖 Overview

Lyrics Insight Studio is a powerful Streamlit application designed to help users analyze, generate, and explore song lyrics using advanced AI techniques. The application provides a comprehensive suite of tools for working with lyrics collections, making it useful for songwriters, music researchers, and lyric enthusiasts.

## ✨ Features

- **Upload Lyrics**: Import PDF collections of song lyrics for analysis
- **Generate Lyrics**: Create original song lyrics based on style, theme, and custom prompts
- **Lyrics Chat**: Conversational interface to discuss and analyze lyrics with AI
- **Search Lyrics**: Find specific themes, phrases, or content across your lyrics collection
- **Analytics**: Visualize patterns, themes, and stylistic elements in your lyrics collection
- **Easy Configuration**: Simple setup with OpenAI API integration

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AILucifer99/Lyrics-Insight-Studio.git
   cd Lyrics-Insight-Studio
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Requirements

The application requires the following Python packages:
- streamlit
- plotly
- pandas
- numpy
- lyricsRAG (custom package for lyrics analysis)

## 🚀 Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Configure your OpenAI API key in the Settings section

4. Upload a lyrics PDF following the specified format (song title on first line, "by Artist Name" on second line, lyrics following)

5. Explore the various features through the sidebar navigation

## 📋 Features Details

### Upload Lyrics
- Upload PDF collections of song lyrics
- Automatic processing and indexing
- View statistics about your collection

### Generate Lyrics
- Create original lyrics with AI assistance
- Customize style, theme, structure, and length
- Download generated lyrics as text files

### Lyrics Chat
- Ask questions about themes, styles, and patterns
- Get AI-powered insights about your lyrics collection
- Interactive chat interface with suggestion chips

### Search Lyrics
- Semantic, keyword, or combined search modes
- Find specific content across all lyrics
- View and explore search results with context

### Analytics
- Visualize metrics like word count, complexity scores
- Explore thematic analysis and emotional tones
- Examine stylistic elements and imagery across songs

### Settings
- Configure OpenAI API key
- Adjust model parameters (temperature, chunk size)
- Manage session data and history

## 📊 Data Visualization

The analytics section provides various visual insights:
- Bar charts for word counts and complexity scores
- Pie charts for theme distribution
- Radar charts for emotional tone analysis
- Artist comparisons and style metrics

## 🔒 Security

- API keys are stored securely for the current session only
- No data is permanently saved on servers
- All processing is done client-side when possible

## 💻 Technical Implementation

The application is built using:
- **Streamlit**: For the web interface and interaction
- **OpenAI**: For text generation and embeddings
- **LangChain**: For RAG (Retrieval-Augmented Generation) capabilities
- **Plotly**: For interactive data visualizations
- **Pandas**: For data manipulation and analysis

## 🧩 Architecture

The application follows a modular structure:
1. **Frontend**: Streamlit-based UI with custom CSS styling
2. **Backend Processing**: PDF parsing, text chunking, and embedding generation
3. **AI Integration**: OpenAI API for generation and question answering
4. **Data Visualization**: Plotly charts for analytics

## 🔍 Example Use Cases

- **Songwriters**: Generate new lyrics and analyze writing patterns
- **Music Researchers**: Study thematic elements across artists or genres
- **Teachers**: Analyze literary devices in song lyrics
- **Music Enthusiasts**: Explore favorite songs in new ways

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Project Link: [https://github.com/yourusername/lyrics-insight-studio](https://github.com/yourusername/lyrics-insight-studio)

---

Made with ❤️ for lyric lovers everywhere
