from generationPipelines import (
    GenerateSingleLyrics, 
    GenerateCompleteSongStructure, 
    GenerateMultipleVariations
)

import asyncio


def generationPipeline(data_path, user_input, **kwargs) :
    if kwargs["parse_function"] :
        if kwargs["generation_pipeline"] == "SingleSongLyrics" :
            print("[INFO] ----> Running the SingleSongLyrics Pipeline....\n")
            asyncio.run(
                GenerateSingleLyrics.generate_single(
                    data_path=data_path, 
                    user_input=user_input, 
                    parse_function=True,
                )
            )
            print("[INFO] ----> Pipeline execution completed successfully.....\n")

        elif kwargs["generation_pipeline"] == "MultipleLyricsVariation" :
            print("[INFO] ----> Running the MultipleLyricsVariation Pipeline....\n")
            asyncio.run(
                GenerateMultipleVariations.generate_variations(
                    data_path=data_path, 
                    song_idea=user_input,
                    parse_function=True,
                    num_variations=2,
                )
            )
            print("[INFO] ----> Pipeline execution completed successfully.....\n")

        elif kwargs["generation_pipeline"] == "CompleteSongStructure" :
            print("[INFO] ----> Running the CompleteSongStructure Pipeline....\n")
            asyncio.run(
                GenerateCompleteSongStructure.generate_full_song_lyrics(
                    data_path=data_path, 
                    lyrics_title=user_input, 
                    parse_function=True,
                )
            )
            print("[INFO] ----> Pipeline execution completed successfully.....\n")


if __name__ == "__main__" :
    data_path = "Data\\Combined-Lyrics.pdf"
    user_query = "A song about lost love found in future like Coldplay."
    pipeline = "MultipleLyricsVariation"

    generationPipeline(
        data_path=data_path, 
        user_input=user_query, 
        generation_pipeline=pipeline, 
        parse_function=True,
    )
