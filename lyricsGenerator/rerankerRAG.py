import os
import sys
from pathlib import Path
import re
from typing import List, Dict, Any, Optional, Union
import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# PDF extraction
import fitz  # PyMuPDF

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain

# Environment variables for API keys
import dotenv
dotenv.load_dotenv()  # Load environment variables from .env file


class AsyncLyricsRAG:
    def __init__(self, pdf_path: str, openai_api_key: str = None, 
                model_name: str = "gpt-4o-mini", chunk_size: int = 500, 
                chunk_overlap: int = 50, temperature: float = 0.7):
        """
        Initialize the Asynchronous Lyrics RAG system
        
        Args:
            pdf_path: Path to the PDF file containing lyrics
            openai_api_key: OpenAI API key (if not set in environment)
            model_name: Name of the OpenAI model to use
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            temperature: Temperature for the LLM (higher = more creative)
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
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.temperature = temperature
        
        # Create an event loop if not existing
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    async def initialize(self) -> None:
        """Asynchronously initialize the RAG system"""
        print(f"Initializing RAG system for {self.pdf_path}...")
        
        # Run extraction and setup in parallel
        await asyncio.gather(
            self._extract_lyrics_from_pdf(),
            self._setup_processing_pool()
        )
        
        # Create vector store after extraction is complete
        await self._create_vector_store()
        
        # Setup RAG chains after vector store is created
        await self._setup_rag_chains()
        
        print("Initialization complete!")
    
    async def _extract_lyrics_from_pdf(self) -> None:
        """Extract lyrics from the PDF, organizing by song and artist"""
        print(f"Extracting lyrics from {self.pdf_path}...")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        # Run PDF extraction in a separate thread to not block the event loop
        def extract_from_pdf():
            # Open the PDF
            doc = fitz.open(self.pdf_path)
            current_song = "Unknown Song"
            current_artist = "Unknown Artist"
            current_lyrics = []
            results = {}
            
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
                            results[current_song] = {
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
                results[current_song] = {
                    "artist": current_artist,
                    "lyrics": "\n".join(current_lyrics)
                }
            
            return results
        
        # Run the extraction in a thread pool
        self.lyrics_by_song = await self.loop.run_in_executor(None, extract_from_pdf)
        print(f"Extracted lyrics for {len(self.lyrics_by_song)} songs")
    
    async def _setup_processing_pool(self) -> None:
        """Set up the process pool for multiprocessing"""
        # Determine optimal number of workers (one per CPU core by default)
        cpu_count = multiprocessing.cpu_count()
        self.max_workers = max(1, cpu_count - 1)  # Leave one core free for system
        print(f"Setting up process pool with {self.max_workers} workers")
        
        # Initialize the process pool executor
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    async def _create_vector_store(self) -> None:
        """Create text chunks and embeddings for the lyrics"""
        print("Creating vector store for lyrics...")
        
        # Create a text splitter for chunking the lyrics
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Prepare texts with metadata
        texts = []
        metadatas = []
        
        # Process songs in parallel
        async def process_song(song, data):
            # Split lyrics into chunks
            song_chunks = text_splitter.split_text(data["lyrics"])
            song_metadata = [
                {
                    "song": song,
                    "artist": data["artist"],
                    "source": self.pdf_path
                }
                for _ in song_chunks
            ]
            return song_chunks, song_metadata
        
        # Process all songs in parallel
        tasks = [
            process_song(song, data) 
            for song, data in self.lyrics_by_song.items()
        ]
        results = await asyncio.gather(*tasks)
        
        # Combine results
        for chunks, metadata in results:
            texts.extend(chunks)
            metadatas.extend(metadata)
        
        self.lyrics_chunks = texts
        
        # Create embeddings and vector store (runs in thread pool automatically)
        def create_store():
            embeddings = OpenAIEmbeddings()
            return Chroma.from_texts(
                texts=texts,
                embedding=embeddings,
                metadatas=metadatas
            )
        
        self.vectorstore = await self.loop.run_in_executor(None, create_store)
        print(f"Created vector store with {len(texts)} chunks")
    
    async def _setup_rag_chains(self) -> None:
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
        
        # Set up the basic QA chain (wrapped in executor to avoid blocking)
        def setup_qa_chain():
            return RetrievalQA.from_chain_type(
                llm=ChatOpenAI(
                    temperature=self.temperature, 
                    model=self.model_name, 
                    max_tokens=512
                ),
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                chain_type_kwargs={"prompt": lyric_prompt}
            )
        
        self.qa_chain = await self.loop.run_in_executor(None, setup_qa_chain)
        
        # Set up the conversational chain with memory
        def setup_conversation_chain():
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            return ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(temperature=self.temperature, model=self.model_name),
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                memory=memory
            )
        
        self.conversation_chain = await self.loop.run_in_executor(None, setup_conversation_chain)
        
        print("RAG pipelines set up successfully")
    
    async def generate_lyrics(self, prompt: str) -> str:
        """
        Generate new lyrics based on the prompt and retrieved context
        
        Args:
            prompt: Instructions for generating the lyrics
                   (e.g., "Write a verse about love in the style of Taylor Swift")
        
        Returns:
            Generated lyrics
        """
        def invoke_chain():
            return self.qa_chain.invoke({"query": prompt})
        
        result = await self.loop.run_in_executor(None, invoke_chain)
        return result["result"]
    
    async def generate_multiple_lyrics(self, prompt: str, variations: int = 3) -> List[str]:
        """
        Generate multiple variations of lyrics based on the same prompt
        
        Args:
            prompt: Instructions for generating the lyrics
            variations: Number of different variations to generate
            
        Returns:
            List of generated lyrics
        """
        print(f"Generating {variations} different lyric variations...")
        
        # Create a list of prompts with variation instructions
        prompts = [
            f"{prompt} (Variation {i+1})" for i in range(variations)
        ]
        
        # Generate all variations in parallel
        tasks = [self.generate_lyrics(p) for p in prompts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def generate_song_components(self, base_prompt: str) -> Dict[str, str]:
        """
        Generate different components of a song in parallel
        
        Args:
            base_prompt: Base prompt for the song generation
            
        Returns:
            Dictionary with different song components
        """
        # Define the different components to generate
        components = {
            "verse1": f"{base_prompt} Write a first verse that sets the scene.",
            "chorus": f"{base_prompt} Write a catchy chorus that serves as the emotional core.",
            "verse2": f"{base_prompt} Write a second verse that develops the story.",
            "bridge": f"{base_prompt} Write a bridge that provides contrast and builds to the final chorus."
        }
        
        # Generate all components in parallel
        tasks = {
            component: self.generate_lyrics(prompt)
            for component, prompt in components.items()
        }
        
        # Wait for all tasks to complete
        results = {}
        for component, task in tasks.items():
            results[component] = await task
            
        return results
    
    async def chat(self, message: str) -> str:
        """
        Have a conversation about lyrics with memory of previous exchanges
        
        Args:
            message: User message about lyrics
            
        Returns:
            Response from the model
        """
        def invoke_chain():
            return self.conversation_chain.invoke({"question": message})
        
        result = await self.loop.run_in_executor(None, invoke_chain)
        return result["answer"]
    
    async def search_lyrics(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for lyrics similar to the query
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of matching lyrics with metadata
        """
        def do_search():
            results = self.vectorstore.similarity_search(query, k=k)
            formatted_results = []
            
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "song": doc.metadata.get("song", "Unknown"),
                    "artist": doc.metadata.get("artist", "Unknown")
                })
                
            return formatted_results
        
        return await self.loop.run_in_executor(None, do_search)
    
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
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self, 'process_pool'):
            self.process_pool.shutdown()
        print("Resources cleaned up")


async def process_batch_generation(lyrics_rag, prompts):
    """Process a batch of generation prompts"""
    tasks = [lyrics_rag.generate_lyrics(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return {prompt: result for prompt, result in zip(prompts, results)}


async def main_async():
    """Asynchronous main function"""
    # Get PDF path from command line argument
    if len(sys.argv) != 2:
        print("Usage: python lyrics_rag.py <path_to_lyrics_pdf>")
        return
    
    pdf_path = sys.argv[1]
    
    # Check if the API key is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY not found in environment variables")
        api_key = input("Please enter your OpenAI API key: ")
    else:
        api_key = None
    
    try:
        # Initialize the RAG system
        lyrics_rag = AsyncLyricsRAG(pdf_path, openai_api_key=api_key)
        await lyrics_rag.initialize()
        
        print("\nInteractive Lyrics Generator")
        print("============================")
        print("Options:")
        print("1. Generate lyrics with a prompt")
        print("2. Generate multiple variations of lyrics")
        print("3. Generate complete song components")
        print("4. Chat about lyrics")
        print("5. Search for similar lyrics")
        print("6. List all songs")
        print("7. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                prompt = input("\nEnter your generation prompt: ")
                print("\nGenerating lyrics...\n")
                lyrics = await lyrics_rag.generate_lyrics(prompt)
                print(lyrics)
                
            elif choice == "2":
                prompt = input("\nEnter your generation prompt: ")
                variations = input("Number of variations (default 3): ")
                variations = int(variations) if variations.isdigit() else 3
                
                print(f"\nGenerating {variations} lyrics variations...\n")
                lyrics_variations = await lyrics_rag.generate_multiple_lyrics(prompt, variations)
                
                for i, lyrics in enumerate(lyrics_variations, 1):
                    print(f"\n--- Variation {i} ---")
                    print(lyrics)
                    print("-" * 40)
            
            elif choice == "3":
                base_prompt = input("\nEnter your base song concept: ")
                print("\nGenerating complete song components in parallel...\n")
                
                components = await lyrics_rag.generate_song_components(base_prompt)
                
                print("--- Complete Song ---\n")
                print("VERSE 1:")
                print(components["verse1"])
                print("\nCHORUS:")
                print(components["chorus"])
                print("\nVERSE 2:")
                print(components["verse2"])
                print("\nBRIDGE:")
                print(components["bridge"])
                print("\nCHORUS:")
                print(components["chorus"])
                
            elif choice == "4":
                message = input("\nEnter your message: ")
                print("\nProcessing...\n")
                response = await lyrics_rag.chat(message)
                print(response)
                
            elif choice == "5":
                query = input("\nEnter your search query: ")
                k = input("Number of results (default 3): ")
                k = int(k) if k.isdigit() else 3
                
                print("\nSearching...\n")
                results = await lyrics_rag.search_lyrics(query, k)
                
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"Song: {result['song']} by {result['artist']}")
                    print(f"Lyrics: {result['content'][:200]}...")
                    print()
                    
            elif choice == "6":
                songs = lyrics_rag.list_songs()
                print("\nSongs in database:")
                for i, song_info in enumerate(songs, 1):
                    print(f"{i}. {song_info['song']} by {song_info['artist']}")
                    
            elif choice == "7":
                print("\nExiting. Thank you for using the Lyrics Generator!")
                await lyrics_rag.close()
                break
                
            else:
                print("Invalid choice. Please select 1-7.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Entry point for the script"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
