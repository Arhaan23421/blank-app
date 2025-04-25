import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from data_processing import process_data
from streamlit_agraph import agraph, Node, Edge, Config
from unidecode import unidecode
import re
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

    # category_counts = data[data["Term Type"] == "Category"].groupby("Term").size().to_dict()
    # subcategory_counts = data[data["Term Type"] == "Subcategory"].groupby("Term").size().to_dict()
    # subcategory_parents = data[data["Term Type"] == "Subcategory"].drop_duplicates(subset=['Term']).set_index('Term').to_dict()['Parent Category']

    category_level_counts = []
    for i in range(4):
        category_counts = data[data[f'Cat-{i}'].notna()].groupby(f"Cat-{i}").size().to_dict()
        category_level_counts.append(category_counts)

    nodes = []
    edges = []

    def scale_function(frequency):
        min_freq = 1
        max_freq = max(category_counts.values())
        min_size = 15
        max_size = 25
        freq_percent = (frequency - min_freq) / (max_freq - min_freq)
        size = freq_percent * (max_size - min_size) + min_size
        return size

    def scale_font_function(frequency):
        min_freq = 1
        max_freq = max(category_counts.values())
        min_size = 20
        max_size = 25
        freq_percent = (frequency - min_freq) / (max_freq - min_freq)
        size = freq_percent * (max_size - min_size) + min_size
        return size

    colors = ["#4281F5","#F5B642","#42F54B","#F5424E"]

    for cat_level in range(4):
        for category, frequency in category_level_counts[cat_level].items():
            nodes.append( Node(
                            id=f'{category}', 
                            label=category.split(':')[-1], 
                            color = colors[cat_level],
                            size=scale_function(frequency), 
                            shape="dot",
                            font={'color': '#000000', 'size': scale_font_function(frequency)},
                            ) 
                        )

    for cat_level in range(4):
        for category, frequency in category_level_counts[cat_level].items():
            if ':' in category:
                edges.append( Edge(source=category, 
                                target=category[:category.rfind(':')], 
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
    def matcher(row):
        if unidecode(row["Term"]).lower() == unidecode(search_term).lower():
            return True
        for i in range(4):
            if (unidecode(row[f"Cat-{i}"] or '')).split(':')[-1].lower() == unidecode(search_term).lower():
                return True
        return False
    return matcher

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
        sentences = rows[['Term', 'Surrounding Sentence']]
        with st.expander("Search results:", expanded=True):
            make_search_results(search_term, sentences, occurences)


def make_search_results(search_term, results, occurences):

    def bold(row):
        term = row['Term']
        sent = row['Surrounding Sentence']
        return re.sub(rf'\b{term}\b', f'**{term}**', sent)

    results = results.apply(bold, axis=1)

    search_results_container = st.container()
    search_results_container.write(f'The term "{search_term}" occured {occurences} time(s)')
    # results = results.map(lambda x: x.replace(search_term, f'**{search_term}**'))
    search_results_container.table(results.reset_index())

def make_individual_statistics(data):
    for paper_title in data['Paper Title'].unique():
        df_temp = data[data['Paper Title'] == paper_title]
        filename = df_temp["File Name"].iloc[0]

        get_last = lambda s: s.split(':')[-1]

        category_levels = []
        for i in range(4):
            category_levels.append(df_temp[df_temp[f'Cat-{i}'].notna()][f'Cat-{i}'])


        with st.expander(paper_title):
            stats_container = st.container()
        
        if stats_container.button("Source Document", key=paper_title):
            document_view(paper_title, filename)
    

        display_file_statistics(paper_title, {
            'Cat-0': Counter(category_levels[0]),
            'Cat-1': Counter(category_levels[1]),
            'Cat-2': Counter(category_levels[2]),
            'Cat-3': Counter(category_levels[3]),
        }, stats_container)

@st.dialog("Source Document", width="large")
def document_view(document, filename):
    with open(filename) as file:
        body = file.read()
        st.html(body)
    

def make_cumulative_statistics(data):

    category_levels = []
    for i in range(4):
        category_levels.append(data[data[f'Cat-{i}'].notna()][f'Cat-{i}'])

    with st.expander('Cumulative', expanded=True):
        stats_container = st.container()

    display_file_statistics('Cumulative', {
            'Cat-0': Counter(category_levels[0]),
            'Cat-1': Counter(category_levels[1]),
            'Cat-2': Counter(category_levels[2]),
            'Cat-3': Counter(category_levels[3]),
    }, stats_container)

    make_graph(data, stats_container)

def display_file_statistics(header, data, stats_container):
    st.divider()
    #   stats_container.header(header)

    cols = stats_container.columns(len(data))

    for i, (name, counts) in enumerate(data.items()):
        counts = {k.split(':')[-1]: v for k, v in counts.items()}
        df = pd.DataFrame(counts.items(), columns=[name, 'Count']).sort_values(by="Count", ascending=False)
        cols[i].dataframe(df)

    # Plot the bar graph hardcoded for categories
    category_df = pd.DataFrame(data['Cat-1'].items(), columns=['Cat-1', 'Count']).sort_values(by="Count", ascending=False)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.barh(category_df["Cat-1"].map(lambda s: s.split(':')[-1]), category_df["Count"], color="skyblue")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Cat-1")
    ax.set_title("Occurrences of Each Data-Category in the Text")
    ax.invert_yaxis()
    stats_container.pyplot(fig)

main()