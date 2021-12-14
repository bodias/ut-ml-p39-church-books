from bs4 import BeautifulSoup
import lxml
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import os
import re
from Levenshtein import distance as editdistance
from tqdm import tqdm
import json
import logging

logging.basicConfig(level=logging.INFO)

def extract_text_from_transkribus(folder_name:str) -> list :
    """Given a folder with XML extracted from transkribus, return all detected text"""
    
    extracted_data = []
    xml_files = [file for file in os.listdir(folder_name) if file[-4:]==".xml"]

    if not xml_files:
        logging.error(f"Transkribus folder {folder_name} does not contain any .xml files")
        return []
    
    page_regex = r'[a-z0-9]*_[0-9]*_[0-9]*_([0-9]*)_m.xml'
    p = re.compile(page_regex)

    for xml_filename in xml_files:
        detected_text = []
        page_search = p.search(xml_filename)
        if page_search:
            page_no = int(page_search.group(1))

        with open(os.path.join(folder_name, xml_filename), "r") as xml_file:
            xml_content = xml_file.read()

        soup = BeautifulSoup(xml_content, "lxml")
        text_lines = soup.find_all("textline")
        for data in text_lines:
            polygon = []
            polygon_text = data.find('coords').get('points')        
            coord = polygon_text.split(" ")
            for xy in coord:
                point = xy.split(",")
                polygon.append((int(point[0]), int(point[1])))
            content = data.find('unicode').get_text()
            detected_text.append({'polygon': polygon, 'content': content})

        extracted_data.append({"source_file": xml_filename,
                               "page_no": page_no,
                               "detected_text": detected_text})
    return extracted_data

def load_surnames_db(file: str) -> list:
    if not os.path.exists(file):
        logging.error(f"Surnames database not found! check surnames database path ({file})")
        return []

    with open(file, 'r') as f:
        surnames_db = f.readlines()
    surnames_db = [surnames.replace("\n", "") for surnames in surnames_db]
            
    return surnames_db

def export_results(results:list, file:str):
    if not results:
        logging.warning("List of detected surnames is empty, nothing to export.")
        return

    with open(file, "w") as f:
        json.dump(results, f)
    print(f"Results exported to {file}")

def surnames_search(extracted_data: list, surnames_db: list, min_edit_distance = 1, min_word_size = 3):
    similarity_list = []
    for page in tqdm(extracted_data):
        all_detected_text = [text['content'] for text in page['detected_text']]
        for word in all_detected_text:
            if len(word) >= min_word_size:
                surname_matches = []
                for surname in surnames_db:                    
                    dist = editdistance(word, surname)
                    if dist <= min_edit_distance:
                        surname_matches.append({"surname": surname, "lev_distance": dist})
                if surname_matches:
                    similarity_list.append({'page_no': page['page_no'],
                                            'detected_surname': word,
                                            'matches': surname_matches})
                        
    logging.info(f"{len(similarity_list)} possible surnames found!")

    return similarity_list