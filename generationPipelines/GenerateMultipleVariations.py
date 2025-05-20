import asyncio
from lyricsGenerator import rerankerRAG


async def generate_variations(data_path, song_idea, **kwargs) :
    if kwargs["parse_function"] :

        rag = rerankerRAG.AsyncLyricsRAG(data_path)
        await rag.initialize()
        
        # Generate 3 different variations
        variations = await rag.generate_multiple_lyrics(
            song_idea, 
            variations=kwargs["num_variations"]
        )
        
        for i, lyrics in enumerate(variations, 1):
            print(f"--- Variation {i} ---")
            print(lyrics)
        
        await rag.close()


# asyncio.run(generate_variations())