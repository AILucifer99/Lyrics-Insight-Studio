import asyncio
from lyricsGenerator import rerankerRAG


async def generate_full_song_lyrics(data_path, lyrics_title, **kwargs) :
    if kwargs["parse_function"] :

        rag = rerankerRAG.AsyncLyricsRAG(data_path)
        await rag.initialize()
        
        # Generate all song components in parallel
        components = await rag.generate_song_components(
            lyrics_title
        )
        
        # Assemble the full song
        full_song = f"""
        VERSE 1:
        {components['verse1']}
        
        CHORUS:
        {components['chorus']}
        
        VERSE 2:
        {components['verse2']}
        
        BRIDGE:
        {components['bridge']}
        
        CHORUS:
        {components['chorus']}
        """
        
        print(full_song)
        await rag.close()


# asyncio.run(generate_full_song())