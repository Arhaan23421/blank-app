import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from data_processing import process_data, document_search
from streamlit_agraph import agraph, Node, Edge, Config
from unidecode import unidecode
import re 
#  background-image: url("https://static.vecteezy.com/system/resources/previews/024/399/235/large_2x/abstract-futuristic-wave-background-illustration-ai-generative-free-photo.jpg");
def main():
    st.set_page_config(layout="wide")

    st.html(
'''
<style>
strong {
    font-size: 150%;
}

[class*="st-key-graphcontainer"] {
    color: red;
    width: 500px;
    height: 400px;
}
</style>
''')

    data = process_data()

    make_title()

    tabs = st.tabs(['Home', 'Text', 'Graph', 'Table'])

    with tabs[0]: # Home
        make_search_bar(data)
    with tabs[1]: # Text
        make_text_buttons(data)
    with tabs[2]: # Graph
        make_graph(data)
    with tabs[3]: # Table
        make_individual_statistics(data)
    

def make_title():
    st.title("António Vieira: Opera Omnia")

def make_graph(data):
    category_level_counts = []
    for i in range(4):
        category_counts = data[data[f'Cat-{i}'].notna()].groupby(f"Cat-{i}").size().to_dict()
        category_level_counts.append(category_counts)

    nodes = []
    nodes_no_red = []
    nodes_only_top = []
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
    sizes = [0, 40, 25, 15]
    text_sizes = [0, 40, 30, 30]
    edge_length = 10

    for cat_level in range(1, 4):
        for category, frequency in category_level_counts[cat_level].items():
            nodes.append( Node(
                            id=f'{category}', 
                            label=category.split(':')[-1], 
                            color = colors[cat_level],
                            size=sizes[cat_level], 
                            shape="dot",
                            font={'color': '#000000', 'size': text_sizes[cat_level]},
                            ) 
                        )
            if cat_level < 3:
                nodes_no_red.append( Node(
                            id=f'{category}', 
                            label=category.split(':')[-1], 
                            color = colors[cat_level],
                            size=sizes[cat_level], 
                            shape="dot",
                            font={'color': '#000000', 'size': text_sizes[cat_level]},
                            ) 
                        )
            if cat_level < 2:
                nodes_only_top.append( Node(
                            id=f'{category}', 
                            label=category.split(':')[-1], 
                            color = colors[cat_level],
                            size=sizes[cat_level], 
                            shape="dot",
                            font={'color': '#000000', 'size': text_sizes[cat_level]},
                            ) 
                        )

    for cat_level in range(1, 4):
        for category, frequency in category_level_counts[cat_level].items():
            if ':' in category:
                edges.append( Edge(
                                source=category, 
                                target=category[:category.rfind(':')],
                                length=edge_length
                                ) 
                            )

    config = Config(width="100%",
                    height=500,
                    directed=True, 
                    physics=True, 
                    hierarchical=False,
                    # interaction={'zoomView': False},
                    solver="hierarchicalRepulsion",
                    avoidOverlap=1
                    )


    # with container:
    view_selection = st.radio(
        "Display Levels",
        ["All", "Top two", "Only Top"])
    with st.container(key='graphcontainer', border=True):
        if view_selection == 'All':
            agraph(nodes=nodes, edges=edges, config=config)
        elif view_selection == 'Top two':
            agraph(nodes=nodes_no_red, edges=edges, config=config)
        else:
            agraph(nodes=nodes_only_top, edges=edges, config=config)
    

def make_search_bar(data):

    paper_titles = list(data['Paper Title'].unique())
    paper_titles.insert(0, "Cumulative")
    selection = st.selectbox("Select text", paper_titles)
    search_term = st.text_input("Search Term")

    if search_term:
        rows = document_search(search_term, selection)
        # if selection == 'Cumulative':
        #     # Search by 'Term' only, NOT by checking sentence text
        #     rows = data[data.apply(match_term(search_term), axis=1)]
        # else:
        #     paper_terms = data[data['Paper Title'] == selection]
        #     rows = paper_terms[paper_terms.apply(match_term(search_term), axis=1)]
        
        occurences = len(rows)
        if occurences:
            # sentences = rows[['Term', 'Surrounding Sentence', 'Paper Title']]
            with st.expander("Search results:", expanded=True):
                make_search_results(search_term, rows, occurences)
        else:
            st.text('No results found')


def make_search_results(search_term, results, occurences):

    def bold(row):
        term = row['Term']
        sent = row['Surrounding Sentence']
        new_context = ''
        prev_index = 0
        for match in re.finditer(unidecode(re.escape(term)).lower(), unidecode(sent).lower()):
            new_context += sent[prev_index:match.start()]
            new_context += f'<b>{sent[match.start():match.end()]}</b>'
            prev_index = match.end()
        new_context += sent[prev_index:]
        return new_context

    results['Sentence'] = results.apply(bold, axis=1)

    search_results_container = st.container()
    search_results_container.write(f'The term "{search_term}" occured {occurences} time(s)')
    html_table = '''| | Sentence | Source |
| --- | --- | --- |'''

    i = 1
    for _, data in results.iterrows():
        html_table += f'\n| {i} | {data["Sentence"]} | {data["Paper Title"]} |'
        i += 1


    st.markdown(html_table, unsafe_allow_html=True)

def make_text_buttons(data):
    for paper_title in data['Paper Title'].unique():
        df_temp = data[data['Paper Title'] == paper_title]
        filename = df_temp["File Name"].iloc[0]
        
        if st.button(paper_title, key=paper_title):
            document_view(paper_title, filename)

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
    # category_df = pd.DataFrame(data['Cat-1'].items(), columns=['Cat-1', 'Count']).sort_values(by="Count", ascending=False)
    # fig = plt.figure(figsize=(10, 6))
    # ax = fig.add_subplot(111)
    # ax.barh(category_df["Cat-1"].map(lambda s: s.split(':')[-1]), category_df["Count"], color="skyblue")
    # ax.set_xlabel("Frequency")
    # ax.set_ylabel("Cat-1")
    # ax.set_title("Occurrences of Each Data-Category in the Text")
    # ax.invert_yaxis()
    # stats_container.pyplot(fig)

main()
