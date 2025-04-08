import pandas as pd
from bs4 import BeautifulSoup
import os
import re

FOLDER_NAME = "htmfiles"

def process_data():
    data = []
    columns = ["Paper Title", "Term Type", "Term", "Surrounding Sentence", "Parent Category"]

    for file_name in os.listdir(FOLDER_NAME):
        file_path = os.path.join(FOLDER_NAME , file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        paper_title = soup.find('title').text

        # for span in soup.find_all("span"):
        #     category = span.get("data-category")
        #     subcategory = span.get("data-subcategory")

        #     paragraph = span.parent.text;
        #     text = span.text

        #     paragraph = paragraph[:].replace(text, f'**{text}**')

        #     if category:
        #         data.append([paper_title, 'Category', category, paragraph, "None"])
        #     if subcategory:
        #         data.append([paper_title, 'Subcategory', subcategory, paragraph, category])

        for paragraph in soup.find_all('p'):
            content = str(paragraph)[3:-4]
            sentences = re.findall(r"\S[^\.\?!]+[\.\?!]", content.replace('\n', ''))
            for sentence in sentences:
                sent_obj = BeautifulSoup(f'<div><p>{sentence}</p></div>', 'html.parser')
                for span in sent_obj.find_all("span"):
                    category = span.get("data-category")
                    subcategory = span.get("data-subcategory")


                    
                    # span.string = f'**{span.text}**';
            
                    text = span.parent.text

                    if category:
                        data.append([paper_title, 'Category', category, text, "None"])
                    if subcategory:
                        data.append([paper_title, 'Subcategory', subcategory, text, category])

        
        page_text = soup.find("body").get_text()

        for sentence in re.findall(r"\S[^\.\?!]+[\.\?!]", page_text.replace('\n', '')):
            for word in re.findall(r"[A-zÀ-ú\-\']+", sentence):
                sentence_tmp = sentence.replace(word, f'**{word}**')
                data.append([paper_title, 'General', word, sentence_tmp, "None"])
        
    df = pd.DataFrame(data, columns=columns)
    return df

7