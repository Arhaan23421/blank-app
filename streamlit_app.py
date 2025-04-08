import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from data_processing import process_data
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_extras. stylable_container import stylable_container
from unidecode import unidecode
#  background-image: url("https://static.vecteezy.com/system/resources/previews/024/399/235/large_2x/abstract-futuristic-wave-background-illustration-ai-generative-free-photo.jpg");
def main():
    st.markdown(
'''
<style>
strong {
    font-size: 150%;
}
</style>
''', 
    unsafe_allow_html=True)

    data = process_data()
    make_title()
    make_search_bar(data)
    make_individual_statistics(data)
    make_cumulative_statistics(data)
    

def make_title():
    st.title("António Vieira")
    st.write(
        " Here is information on themes and ideas in Antonio vieira's work [ I will add more deesciption once more works are in]"
    )
#  need to change the font color of title to black here
def make_graph(data, container):

    category_counts = data[data["Term Type"] == "Category"].groupby("Term").size().to_dict()
    subcategory_counts = data[data["Term Type"] == "Subcategory"].groupby("Term").size().to_dict()
    subcategory_parents = data[data["Term Type"] == "Subcategory"].drop_duplicates(subset=['Term']).set_index('Term').to_dict()['Parent Category']

    nodes = []
    edges = []

    def scale_function(frequency):
        min_freq = 1
        max_freq = max(category_counts.values())
        min_size = 10
        max_size = 30
        freq_percent = (frequency - min_freq) / (max_freq - min_freq)
        size = freq_percent * (max_size - min_size) + min_size
        return size

    def scale_font_function(frequency):
        min_freq = 1
        max_freq = max(category_counts.values())
        min_size = 10
        max_size = 30
        freq_percent = (frequency - min_freq) / (max_freq - min_freq)
        size = freq_percent * (max_size - min_size) + min_size
        return size

    for category, frequency in category_counts.items():
        if category.lower() == 'nature':
            nodes.append( Node(
                            id=category, 
                            label=category, 
                            color = "#00FF00",
                            size=scale_function(frequency), 
                            shape="dot",
                            font={'color': '#000000', 'size': scale_font_function(frequency)},
                            ) 
                        )
    for subcategory, frequency in subcategory_counts.items():
        if subcategory_parents[subcategory].lower() == 'nature':
            nodes.append( Node(
                            id=subcategory, 
                            label=subcategory, 
                            size=scale_function(frequency), 
                            shape="dot",
                            font={'color': '#000000', 'size': scale_font_function(frequency)},
                            ) 
                        )

    for subcategory, category in subcategory_parents.items():
        if category.lower() == 'nature':
            edges.append( Edge(source=subcategory, 
                            target=category, 
                            ) 
                        ) 

    config = Config(width=700,
                    height=400,
                    directed=True, 
                    physics=True, 
                    hierarchical=False,
                    interaction={'zoomView': False}
                    )


    with container:
        agraph(nodes=nodes, edges=edges, config=config)
    
def match_term(search_term):
    return lambda row: unidecode(row["Term"]).lower() == unidecode(search_term).lower()

def make_search_bar(data):

    paper_titles = list(data['Paper Title'].unique())
    paper_titles.append("Cumulative")
    selection = st.selectbox("Select the paper you want to search", paper_titles)
    search_term = st.text_input("Enter term you want to search")

    if search_term:
        if selection == 'Cumulative':
            # Search by 'Term' only, NOT by checking sentence text
            rows = data[data.apply(match_term(search_term), axis=1)]
        else:
            paper_terms = data[data['Paper Title'] == selection]
            rows = paper_terms[paper_terms.apply(match_term(search_term), axis=1)]
        
        occurences = len(rows)
        sentences = rows['Surrounding Sentence']
        with st.expander("Search results:", expanded=True):
            make_search_results(search_term, sentences, occurences)


def make_search_results(search_term, results, occurences):
    search_results_container = st.container()
    search_results_container.write(f'The term "{search_term}" occured {occurences} time(s)')
    # results = results.map(lambda x: x.replace(search_term, f'**{search_term}**'))
    search_results_container.table(results.reset_index()["Surrounding Sentence"])

def make_individual_statistics(data):
    for paper_title in data['Paper Title'].unique():
        df_temp = data[data['Paper Title'] == paper_title]

        categories = df_temp[df_temp['Term Type'] == 'Category']['Term']
        subcategories = df_temp[df_temp['Term Type'] == 'Subcategory']['Term']


        with st.expander(paper_title):
            stats_container = st.container()

        display_file_statistics(paper_title, {
            'Category': Counter(categories),
            'Subcategory': Counter(subcategories)
        }, stats_container)

def make_cumulative_statistics(data):
    categories = data[data['Term Type'] == 'Category']['Term']
    subcategories = data[data['Term Type'] == 'Subcategory']['Term']

    with st.expander('Cumulative', expanded=True):
        stats_container = st.container()

    display_file_statistics('Cumulative', {
        'Category': Counter(categories),
        'Subcategory': Counter(subcategories),
    }, stats_container)

    make_graph(data, stats_container)

def display_file_statistics(header, data, stats_container):
    st.divider()
    #   stats_container.header(header)

    cols = stats_container.columns(len(data))

    for i, (name, counts) in enumerate(data.items()):
        df = pd.DataFrame(counts.items(), columns=[name, 'Count']).sort_values(by="Count", ascending=False)
        cols[i].dataframe(df)

    # Plot the bar graph hardcoded for categories
    category_df = pd.DataFrame(data['Category'].items(), columns=['Category', 'Count']).sort_values(by="Count", ascending=False)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.barh(category_df["Category"], category_df["Count"], color="skyblue")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Category")
    ax.set_title("Occurrences of Each Data-Category in the Text")
    ax.invert_yaxis()
    stats_container.pyplot(fig)

main()