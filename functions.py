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
    
    extracted_data = {}
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
        else:
            try:
                page_no = int(xml_filename[:-4])
            except:
                logging.error(f"Couldn't retrieve page no from xml_filename {xml_filename}")

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
            # Get only text from element "TextEquiv". avoid "Word" Tag
            for ch in data.children:
                if ch.name == "textequiv":
                    content = ch.find('unicode').get_text()
            detected_text.append({'polygon': polygon, 'content': content})
        extracted_data[page_no] = {"source_file": xml_filename,
                                   "page_no": page_no,
                                   "detected_text": detected_text}
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

def surnames_db_search(extracted_data: list, surnames_db: list, min_edit_distance = 1, min_word_size = 3):
    similarity_list = {}
    for page_no, page_data in tqdm(extracted_data.items()):
        all_detected_text = [text['content'] for text in page_data['detected_text']]
        for word in all_detected_text:
            if len(word) >= min_word_size:
                surname_matches = []
                for surname in surnames_db:                    
                    dist = editdistance(word, surname)
                    if dist <= min_edit_distance:
                        surname_matches.append({"surname": surname, "lev_distance": dist})
                if surname_matches:
                    if page_no not in similarity_list.keys():
                        similarity_list[page_no] = []
                    similarity_list[page_no].append({'page_no': page_no,
                                                     'extracted_surname': word,
                                                     'matches': surname_matches})

    return similarity_list

def surnames_regex_search(extracted_data: list, min_word_size = 3):
    surname_regex = r'^(?:[A-ZÄÖÕÜ][a-zäöõü.]*(?:\s|\+)){1,}([A-ZÄÖÜ][a-zäöü]{1,})(?:\sll|\slaps|\sL|\sT|\sLesk)?$'
    p = re.compile(surname_regex)
    
    extracted_surnames = {}
    for page_no, page_data in tqdm(extracted_data.items()):
        for text in page_data["detected_text"]:
            content = text["content"]
            name_match = p.match(content)
            if name_match:
                surname = name_match.group(1)            
                if surname == "Lesk":
                    surname = content[:content.rfind("Lesk")-1]
                    surname = surname[surname.rfind(" ")+1:]
                # print(f"page: {page_no}: {content}->{surname}")                   
                if len(surname) > min_word_size:
                    if page_no not in extracted_surnames.keys():
                        extracted_surnames[page_no] = []
                    
                    extracted_surnames[page_no].append({'page_no': page_no,
                                                        'extracted_surname': surname,
                                                        'matches': [{"surname": content, "lev_distance": 0}]})
    
    return extracted_surnames

def get_metrics(predicted_data, gt_data, verbose=False):
    all_surnames = [word["extracted_surname"] for pages in gt_data.values() for word in pages["detected_text"]]
    counters = {"combined_matches": 0}
    count_gt_surnames = len(all_surnames)
    
    for method, extracted_data in predicted_data.items():
        counters[method] = 0
        for page_no, detected_surnames in extracted_data.items():
            if verbose:
                print(f"page no: {page_no}")
            for detected_surname in detected_surnames:
                for true_surname in gt_data[page_no]["detected_text"]:
                    if detected_surname['extracted_surname']==true_surname["extracted_surname"]:
                        counters["combined_matches"] += 1
                        counters[method] += 1
                        if verbose:
                            print(f"{detected_surname['extracted_surname']}=={true_surname['extracted_surname']}")
                    
    accuracy = {k: v/len(all_surnames) for k,v in counters.items()} 
    return counters, accuracy    