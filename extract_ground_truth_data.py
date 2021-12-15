import pandas as pd
import numpy as np
import os
import re
import json
import copy
from functions import extract_text_from_transkribus

folder_names = [
                "transkribus_data/ground_truth/Braian_Pages/Braian_Pages/page/",
                "transkribus_data/ground_truth/Aitor_Pages_transkribus_/Aitor_Pages_transkribus/page/",
                "transkribus_data/ground_truth/img_ML/img_ML/page/",
               ]

# discard pages > 335 because they are indexes
MAX_PAGE_NO = 335

if __name__ == "__main__":
    test_data = {}
    for folder in folder_names:
        extracted_data = extract_text_from_transkribus(folder)
        pages = list(extracted_data.keys())
        for page_no in pages:
            if page_no > MAX_PAGE_NO:
                extracted_data.pop(page_no)
        test_data.update(extracted_data)

    ## Filter dataset to get only detected text which contains a surname
    surname_regex = r'^(?:[A-ZÄÖÕÜ][a-zäöõü.]*(?:\s|\+)){1,}([A-ZÄÖÜ][a-zäöü]{1,})(?:\sll|\slaps|\sL|\sT|\sLesk)?$'
    p = re.compile(surname_regex)

    count_gt_surnames = 0
    gt_surnames = {}
    for page_no, page_data in test_data.items():
    #     print(page_no)
        only_detected_surnames = []
        for text in page_data["detected_text"]:
            content = text["content"]
            name_match = p.match(content)
            if name_match:
                surname = name_match.group(1)            
                if surname == "Lesk":
                    surname = content[:content.rfind("Lesk")-1]
                    surname = surname[surname.rfind(" ")+1:]
                print(f"page: {page_no}: {content}->{surname}")   
                text["extracted_surname"] = surname            
                only_detected_surnames.append(copy.deepcopy(text))
                count_gt_surnames += 1
        if only_detected_surnames:
            processed_page = copy.deepcopy(page_data)
            processed_page["detected_text"] = only_detected_surnames
            processed_page["count_surnames"] = len(only_detected_surnames)
            gt_surnames[page_no] = processed_page

    with open("databases/ground_truth_ALL_pages.json", "w") as f:
        json.dump(gt_surnames, f)