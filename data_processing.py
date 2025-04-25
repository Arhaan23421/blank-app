import pandas as pd
from bs4 import BeautifulSoup
import os
import re

FOLDER_NAME = "htmfiles"

def process_data():
    data = []
    columns = ["File Name", "Paper Title", "Term", "Cat-0", "Cat-1", "Cat-2", "Cat-3", "Surrounding Sentence"]

    for file_name in os.listdir(FOLDER_NAME):
        file_path = os.path.join(FOLDER_NAME , file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        paper_title = soup.find('title').text

        for paragraph in soup.find_all('p'):
            content = str(paragraph)[3:-4]
            sentences = re.findall(r"\S[^\.\?!]+[\.\?!]", content.replace('\n', ''))
            for sentence in sentences:
                sent_obj = BeautifulSoup(f'<div><p>{sentence}</p></div>', 'html.parser')
                for span in sent_obj.find_all("span"):
                    category = span.get("data-cat-0")
                    subcategory = span.get("data-cat-1")
                    ssubcategory = span.get("data-cat-2")
                    sssubcategory = span.get("data-cat-3")
                    # changed all the stuff above based on the new format

                    if category:
                        category = category.lower()
                    if subcategory:
                        subcategory = category + ':' + subcategory.lower()
                    if ssubcategory:
                        ssubcategory = subcategory + ':' + ssubcategory.lower()
                    if sssubcategory:
                        sssubcategory = ssubcategory + ':' + sssubcategory.lower()


                    
                    # span.string = f'**{span.text}**';
            
                    surrounding_sentence = span.parent.text

                    data.append([file_path, paper_title, span.text.lower(), category, subcategory, ssubcategory, sssubcategory, surrounding_sentence])


        page_text = soup.find("body").get_text()
        for sentence in re.findall(r"\S[^\.\?!]+[\.\?!]", page_text.replace('\n', '')):
            for word in re.findall(r"[A-zÀ-ú\-\']+", sentence):
                data.append([file_path, paper_title, word.lower(), None, None, None, None, sentence])
        
    df = pd.DataFrame(data, columns=columns)
    return df

7