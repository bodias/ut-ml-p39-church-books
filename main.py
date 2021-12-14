import click
from functions import extract_text_from_transkribus, load_surnames_db, surnames_search, export_results

@click.command()
@click.option("--transkribus-folder", help="Folder containing .XML files exported from Transkribus")
@click.option("--surnames-db", help=".txt file containing list of surnames")
@click.option("--min-edit-distance", default=1, help="Minimum edit distance to consider a match")
@click.option("--min-word-size", default=3, help="Minimum word size to consider a valid word")
@click.option("--export-file", default='results.json', help=".json file with results")
def process_folder(transkribus_folder: str, surnames_db: str, export_file:str, min_edit_distance:int , min_word_size:int):
    extracted_text = extract_text_from_transkribus(transkribus_folder)
    surnames = load_surnames_db(surnames_db) 

    if extracted_text and surnames:        
        surnames_list = surnames_search(extracted_text, surnames)
        export_results(surnames_list, export_file)

if __name__ == "__main__":
    process_folder()
