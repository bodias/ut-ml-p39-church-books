import click
from functions import extract_text_from_transkribus, load_surnames_db, surnames_db_search, surnames_regex_search, export_results

@click.command()
@click.option("--transkribus-folder", help="Folder containing .XML files exported from Transkribus")
@click.option("--surnames-db", default='databases/final_database_estonian_surnames.txt', help=".txt file containing list of surnames")
@click.option("--min-edit-distance", default=1, help="Minimum edit distance to consider a match")
@click.option("--min-word-size", default=3, help="Minimum word size to consider a valid word")
@click.option("--export-file", default='results.json', help=".json file with results")
def process_folder(transkribus_folder: str, surnames_db: str, export_file:str, min_edit_distance:int , min_word_size:int):
    extracted_text = extract_text_from_transkribus(transkribus_folder)
    surnames = load_surnames_db(surnames_db) 

    if extracted_text and surnames:        
        surnames_list_db = surnames_db_search(extracted_text, surnames)
        surnames_list_regex = surnames_regex_search(extracted_text, surnames)
        surnames_list = {"db_match": surnames_list_db,
                         "regex_match": surnames_list_regex}
        export_results(surnames_list, export_file)

if __name__ == "__main__":
    process_folder()
