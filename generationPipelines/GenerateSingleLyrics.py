import asyncio
from lyricsGenerator import rerankerRAG


async def generate_single(data_path, **kwargs) :
    if kwargs["parse_function"] :

        # Initialize the system
        rag = rerankerRAG.AsyncLyricsRAG(data_path)
        await rag.initialize()
        
        # Generate lyrics
        lyrics = await rag.generate_lyrics(kwargs["user_input"])

        print("[INFO] ----> Generated Lyrics by the RAG Pipeline :- \n")
        print("==" * 100)
        print(lyrics)
        print("==" * 100)
        print("\n")
        
        # Clean up
        await rag.close()


# # Run the async function
# asyncio.run(generate_single())