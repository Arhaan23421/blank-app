import pandas as pd
from bs4 import BeautifulSoup
import os
import re
from unidecode import unidecode

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

def document_search(search_term, document_title):
    '''
    Take in a search term which can be a word/substring found in the text or
    a category name. Return a dataframe of results with three columns:
        'Term'
        'Surrounding Sentence'
        'Paper Title'
    Where surrounding sentence contains the sentence which the excerpt was found in.
    '''
    data = []
    columns = ["Term", "Surrounding Sentence", "Paper Title"]

    for file_name in os.listdir(FOLDER_NAME):
        file_path = os.path.join(FOLDER_NAME, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        paper_title = soup.find('title').text
        if document_title == 'Cumulative' or document_title == paper_title:
            # TODO: find categorized spans and include them in results
            for span in soup.find_all("span"):
                category = span.get("data-cat-0")
                subcategory = span.get("data-cat-1")
                ssubcategory = span.get("data-cat-2")
                sssubcategory = span.get("data-cat-3")
                # changed all the stuff above based on the new format

                if search_term in [category, subcategory, ssubcategory, sssubcategory]:
                    for match in re.finditer(unidecode(re.escape(span.text)).lower(), unidecode(span.parent.text).lower()):
                        context = find_context(span.parent.text, match)
                        context = context.replace('\n', ' ')
                        data.append([span.text, context, paper_title])

            # Search for the term in the body text
            page_text = soup.find("body").get_text()
            for match in re.finditer(unidecode(re.escape(search_term)).lower(), unidecode(page_text).lower()):
                context = find_context(page_text, match)
                context = context.replace('\n', ' ')
                data.append([search_term, context, paper_title])

    df = pd.DataFrame(data, columns=columns)
    return df.drop_duplicates()

def find_context(page_text, match):
    context_start = match.start()
    for _ in range(11):
        if ' ' not in page_text[:context_start]:
            context_start = 0
            break
        context_start = page_text[:context_start].rfind(' ')
    context_end = match.end()
    for _ in range(10):
        if ' ' not in page_text[context_end+1:]:
            context_end = len(page_text)
            break
        context_end = context_end + 1 + page_text[context_end+1:].find(' ')
    context = page_text[context_start:context_end]
    return context
