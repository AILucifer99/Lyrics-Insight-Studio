import os
import sys
from pathlib import Path
import re
from typing import List, Dict, Any

# PDF extraction
import fitz  # PyMuPDF

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


# Environment variables for API keys
import dotenv
dotenv.load_dotenv()  # Load environment variables from .env file

class LyricsRAG:
    def __init__(self, pdf_path: str, openai_api_key: str = None):
        """
        Initialize the Lyrics RAG system
        
        Args:
            pdf_path: Path to the PDF file containing lyrics
            openai_api_key: OpenAI API key (if not set in environment)
        """
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.pdf_path = pdf_path
        self.lyrics_by_song = {}
        self.lyrics_chunks = []
        self.vectorstore = None
        self.qa_chain = None
        self.conversation_chain = None
        
        # Load and process the PDF
        self._extract_lyrics_from_pdf()
        self._create_vector_store()
        self._setup_rag_chains()
    
    def _extract_lyrics_from_pdf(self):
        """Extract lyrics from the PDF, organizing by song and artist"""
        print(f"Extracting lyrics from {self.pdf_path}...")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        # Open the PDF
        doc = fitz.open(self.pdf_path)
        current_song = "Unknown Song"
        current_artist = "Unknown Artist"
        current_lyrics = []
        
        # Skip the title page (first page)
        for page_num in range(1, len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Try to extract song title and artist
            lines = text.split('\n')
            if len(lines) >= 2:
                # First line is typically the song title
                song_title = lines[0].strip()
                
                # Second line typically starts with "by" for the artist
                artist_line = lines[1].strip()
                if artist_line.startswith("by "):
                    artist = artist_line[3:].strip()
                    
                    # Store previous song if we have one
                    if current_lyrics and current_song != song_title:
                        self.lyrics_by_song[current_song] = {
                            "artist": current_artist,
                            "lyrics": "\n".join(current_lyrics)
                        }
                        current_lyrics = []
                    
                    # Update current song and artist
                    current_song = song_title
                    current_artist = artist
                    
                    # Get lyrics (everything after the second line)
                    if len(lines) > 2:
                        current_lyrics = lines[2:]
        
        # Store the last song
        if current_lyrics:
            self.lyrics_by_song[current_song] = {
                "artist": current_artist,
                "lyrics": "\n".join(current_lyrics)
            }
        
        print(f"Extracted lyrics for {len(self.lyrics_by_song)} songs")
    
    def _create_vector_store(self):
        """Create text chunks and embeddings for the lyrics"""
        print("Creating vector store for lyrics...")
        
        # Create a text splitter for chunking the lyrics
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Prepare texts with metadata
        texts = []
        metadatas = []
        
        for song, data in self.lyrics_by_song.items():
            # Split lyrics into chunks
            song_chunks = text_splitter.split_text(data["lyrics"])
            texts.extend(song_chunks)
            
            # Add metadata for each chunk
            for _ in song_chunks:
                metadatas.append({
                    "song": song,
                    "artist": data["artist"],
                    "source": self.pdf_path
                })
        
        self.lyrics_chunks = texts
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )
        
        print(f"Created vector store with {len(texts)} chunks")
    
    def _setup_rag_chains(self):
        """Set up the RAG chains for lyric generation"""
        # Define the prompt template for lyric generation
        lyric_prompt_template = """
        You are a professional songwriter. Use the following lyrics as inspiration to create original lyrics in a similar style.
        
        Context lyrics:
        {context}
        
        Instructions:
        {question}
        
        Generated Lyrics:
        """
        
        lyric_prompt = PromptTemplate(
            template=lyric_prompt_template,
            input_variables=["context", "question"]
        )
        
        # Set up the basic QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                temperature=0.7, 
                model="gpt-4o-mini", 
                max_tokens=512
            ),
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": lyric_prompt}
        )
        
        # Set up the conversational chain with memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.7),
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=memory
        )
        
        print("RAG pipelines set up successfully")
    
    def generate_lyrics(self, prompt: str) -> str:
        """
        Generate new lyrics based on the prompt and retrieved context
        
        Args:
            prompt: Instructions for generating the lyrics
                   (e.g., "Write a verse about love in the style of Taylor Swift")
        
        Returns:
            Generated lyrics
        """
        result = self.qa_chain.invoke({"query": prompt})
        return result["result"]
    
    def chat(self, message: str) -> str:
        """
        Have a conversation about lyrics with memory of previous exchanges
        
        Args:
            message: User message about lyrics
            
        Returns:
            Response from the model
        """
        result = self.conversation_chain.invoke({"question": message})
        return result["answer"]
    
    def search_lyrics(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for lyrics similar to the query
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of matching lyrics with metadata
        """
        results = self.vectorstore.similarity_search(query, k=k)
        formatted_results = []
        
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "song": doc.metadata.get("song", "Unknown"),
                "artist": doc.metadata.get("artist", "Unknown")
            })
            
        return formatted_results
    
    def list_songs(self) -> List[Dict[str, str]]:
        """
        List all songs in the database
        
        Returns:
            List of songs with their artists
        """
        return [
            {"song": song, "artist": data["artist"]}
            for song, data in self.lyrics_by_song.items()
        ]


def main():
    """Example usage of the LyricsRAG class"""
    if len(sys.argv) != 2:
        print("Usage: python lyrics_rag.py <path_to_lyrics_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if the API key is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY not found in environment variables")
        api_key = input("Please enter your OpenAI API key: ")
    else:
        api_key = None
    
    try:
        # Initialize the RAG system
        lyrics_rag = LyricsRAG(pdf_path, openai_api_key=api_key)
        
        print("\nInteractive Lyrics Generator")
        print("============================")
        print("Options:")
        print("1. Generate lyrics with a prompt")
        print("2. Chat about lyrics")
        print("3. Search for similar lyrics")
        print("4. List all songs")
        print("5. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                prompt = input("\nEnter your generation prompt: ")
                print("\nGenerating lyrics...\n")
                lyrics = lyrics_rag.generate_lyrics(prompt)
                print(lyrics)
                
            elif choice == "2":
                message = input("\nEnter your message: ")
                print("\nProcessing...\n")
                response = lyrics_rag.chat(message)
                print(response)
                
            elif choice == "3":
                query = input("\nEnter your search query: ")
                k = input("Number of results (default 3): ")
                k = int(k) if k.isdigit() else 3
                
                print("\nSearching...\n")
                results = lyrics_rag.search_lyrics(query, k)
                
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"Song: {result['song']} by {result['artist']}")
                    print(f"Lyrics: {result['content'][:200]}...")
                    print()
                    
            elif choice == "4":
                songs = lyrics_rag.list_songs()
                print("\nSongs in database:")
                for i, song_info in enumerate(songs, 1):
                    print(f"{i}. {song_info['song']} by {song_info['artist']}")
                    
            elif choice == "5":
                print("\nExiting. Thank you for using the Lyrics Generator!")
                break
                
            else:
                print("Invalid choice. Please select 1-5.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
