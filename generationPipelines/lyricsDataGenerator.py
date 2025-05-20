import os
import csv
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch


def create_lyrics_pdf(lyrics_data, output_file):
    """
    Creates a PDF file from the lyrics data.
    
    Args:
        lyrics_data (list): List of tuples containing (song_title, artist, lyrics)
        output_file (str): Path to the output PDF file
    """
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'SongTitle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    artist_style = ParagraphStyle(
        'Artist',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    lyrics_style = ParagraphStyle(
        'Lyrics',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=24
    )
    
    # Create the PDF content
    story = []
    
    # Add a title page
    title = Paragraph("Collection of Song Lyrics", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 2*inch))
    info = Paragraph(f"Containing lyrics from {len(lyrics_data)} songs", styles['Normal'])
    story.append(info)
    story.append(Spacer(1, 0.5*inch))
    date = Paragraph(f"Generated on {import_date()}", styles['Normal'])
    story.append(date)
    story.append(Spacer(1, 2*inch))
    
    # Add a page break
    story.append(Paragraph("<br clear=all style='page-break-before:always'/>", styles['Normal']))
    
    # Add each song
    for song_title, artist, lyrics in lyrics_data:
        # Format song title
        p_title = Paragraph(song_title, title_style)
        story.append(p_title)
        
        # Format artist
        p_artist = Paragraph(f"by {artist}", artist_style)
        story.append(p_artist)
        
        # Format lyrics - replace newlines with <br/> tags for proper display
        formatted_lyrics = lyrics.replace('\n', '<br/>')
        p_lyrics = Paragraph(formatted_lyrics, lyrics_style)
        story.append(p_lyrics)
        
        # Add a page break between songs
        story.append(Paragraph("<br clear=all style='page-break-before:always'/>", styles['Normal']))
    
    # Build the PDF
    doc.build(story)


def import_date():
    """Returns the current date as a string."""
    from datetime import datetime
    return datetime.now().strftime("%B %d, %Y")


def combine_lyrics_from_csvs(input_dir, output_file):
    """
    Reads all CSV files in the specified directory, extracts lyrics,
    and combines them into a single PDF file.
    
    Args:
        input_dir (str): Directory containing CSV files
        output_file (str): Path to the output PDF file
    """
    lyrics_data = []  # Will store tuples of (song_title, artist, lyrics)
    processed_files = 0
    
    # Ensure input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
    
    # Process all CSV files in the directory
    for file_path in Path(input_dir).glob('*.csv'):
        try:
            print(f"Processing {file_path}...")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as csv_file:
                # Use csv.DictReader to handle CSV files with headers
                reader = csv.DictReader(csv_file)
                
                # Try to identify the columns
                lyrics_column = None
                song_column = None
                artist_column = None
                
                for column in reader.fieldnames:
                    col_lower = column.lower()
                    if 'lyric' in col_lower:
                        lyrics_column = column
                    elif 'song' in col_lower or 'title' in col_lower or 'name' in col_lower:
                        song_column = column
                    elif 'artist' in col_lower:
                        artist_column = column
                
                if not lyrics_column:
                    print(f"Warning: Could not identify lyrics column in {file_path}. Available columns: {reader.fieldnames}")
                    print("Skipping this file. Please check the file format.")
                    continue
                
                # Extract lyrics from the identified column
                for row in reader:
                    if lyrics_column in row and row[lyrics_column]:
                        song_title = row.get(song_column, "Unknown Song") if song_column else "Unknown Song"
                        artist = row.get(artist_column, "Unknown Artist") if artist_column else "Unknown Artist"
                        lyrics = row[lyrics_column]
                        lyrics_data.append((song_title, artist, lyrics))
            
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Create PDF with all lyrics
    if lyrics_data:
        try:
            create_lyrics_pdf(lyrics_data, output_file)
            print(f"Successfully created {output_file} with lyrics from {processed_files} files.")
            print(f"Total songs: {len(lyrics_data)}")
        except Exception as e:
            print(f"Error creating PDF file: {e}")
    else:
        print("No lyrics found in the CSV files.")


if __name__ == "__main__":

    # python lyrics_combiner.py ./archive/Lyrics-Data ./all_lyrics.pdf
    if len(sys.argv) != 3:
        print("Usage: python lyrics_combiner.py <input_directory> <output_file>")
        print("Example: python lyrics_combiner.py ./csv_files ./all_lyrics.pdf")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    # Ensure output file has .pdf extension
    if not output_file.lower().endswith('.pdf'):
        output_file += '.pdf'
    
    combine_lyrics_from_csvs(input_dir, output_file)