import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from st_files_connection import FilesConnection

#function to get al the possible notes
@st.cache_data#
def get_all_notes(df):
    og_notes = df['Notes_list']
    extracted_notes = df['extracted_list']

    all_notes_og = []
    all_notes_ex = []

    for og_lst in og_notes:  # for each list in the og notes column
        for og_note in og_lst:  # for each note in the list
            og_note = og_note.lstrip()
            if og_note not in all_notes_og:
                all_notes_og.append(og_note)

    for ex_lst in extracted_notes:
        for ex_note in ex_lst:
            ex_note = ex_note.lstrip()
            if ex_note not in all_notes_ex:
                all_notes_ex.append(ex_note)

    return all_notes_og, all_notes_ex

#Get a dictionary in the form {category: [fragrance notes]}
@st.cache_data#
def category_dict(all_notes_in_frag_df): #input is get_all_notes(df)[0]
    with open('pages/fragrance_categories.json') as frags:
        frag_categories = json.load(frags)

    new_dict = {}
    for k, v in frag_categories.items():
        new_list = []
        for note in all_notes_in_frag_df:
            if note in v:
                new_list.append(note)
        new_dict[k] = new_list

    return new_dict

#get average rating- will use to do final sorting of top 5 fragrances
#returned values may be 0 until more feedback is given
@st.cache_data#
def get_avg_rating(fragrance_of_interest):
    with open('pages/user_feedback.json') as uf:
        feed = json.load(uf)

    conn = st.connection('s3', type=FilesConnection)

    ##The below gives a pandas df
    df = conn.read("fragrancestreamlit/pages/user_feedback.json", input_format="json", ttl=600)
    uf_df = pd.DataFrame(df)
    ratings = 0.0
    if fragrance_of_interest in list(uf_df.columns):
        frag_col_list = [val for val in list(uf_df[fragrance_of_interest]) if isinstance(val, dict)]
        for dict_val in frag_col_list:
            rating = dict_val['rating']
            num_rating = float(rating)
            ratings += num_rating

        avg_ratings = ratings / len(frag_col_list)
        return avg_ratings
    else:
        return 0

    #give recommendation
#notes_preferences is a list of strings from the input from streamlit's multiselect
#Output will be fragrance names in a list, notes in a list, and cosine similarity score in a list
#may not need the category dict, will likely start off with just the notes before doing category + notes
@st.cache_data#
def give_recommendation(notes_preferences, category_dictionary, fragrance_df):
    # for use later, get cosine similarity between two lists of strings
    def cosine_sim(a, b):  # a and b are lists
        a_join = ' '.join(a)
        b_join = ' '.join(b)

        data = [a_join, b_join]
        #count_vectorizer = CountVectorizer()
        count_vectorizer = TfidfVectorizer()
        vector_matrix = count_vectorizer.fit_transform(data)

        cosine_similarity_matrix = cosine_similarity(vector_matrix)

        return cosine_similarity_matrix[0][1]  # similarity score

    #since I already have the note preferences through streamlit, I just need
    #to get the cosine similarities with all of the fragracnces, and output the top 5 along with their
    #similarity scores
    cos_sim_scores = []
    extracted_notes = fragrance_df['extracted_list'].to_list()
    new_extracted = []
    for notes in extracted_notes:
        new_notes = [n.lower().strip() for n in notes]
        new_extracted.append(new_notes)

    # implement cosine similarity, comparing each fragrance's notes list to the preference list
    for notes_list in new_extracted:
        cosine_sim_score = cosine_sim(notes_list, notes_preferences)
        cos_sim_scores.append(round(cosine_sim_score, 3))

    #make a new df column for cos sim
    fragrance_df['cosine_sim_score'] = cos_sim_scores

    #sort the values from highest score to lowest, return top 5
    sorted_df = fragrance_df.sort_values(by=['cosine_sim_score'], ascending=False)
    #get the fragrances with a score of over 0.15:
    sorted_df = sorted_df[sorted_df['cosine_sim_score'] > 0.15]

    ##TO DO: apply get_avg_rating, then sort by cosine sim and avg_rating (see Jupyter Notebook)
    avg_rating_list = [get_avg_rating(fragrance_name) for fragrance_name in sorted_df['Name']]
    sorted_df['Avg_Rating'] = avg_rating_list
    scores = sorted_df['cosine_sim_score'].to_list() #list of all of the cosine sim scores, sorted
    notes = sorted_df['extracted_notes'].to_list() #list of all of the notes, sorted
    sorted_df['full_name'] = sorted_df['Name'] + ' by ' + sorted_df['Brand']
    total_name = sorted_df['full_name'].to_list() #full name of the fragrance including brand, sorted


    #return top_5_frags, top_5_frags_notes, top_5_scores
    return total_name, notes, scores, avg_rating_list


def show_recs(fragrance, notes, cos_sim, avg_rating_list):
    st.markdown(f'***Fragrance Recommendation:*** {fragrance}')
    st.markdown(f'***Notes:*** {notes}')
    st.markdown(f'*Cosine similarity score:* {str(cos_sim)}')

    ## Increments the counter to get next rec
    st.session_state.counter += 1
    if st.session_state.counter >= len(fragrances):
        st.session_state.counter = 0

@st.cache_data#(allow_output_mutation=True)
def final_df():
    df = pd.read_csv('pages/full_perfume_data.csv')
    # fix the notes column setup so that there's no leading whitespace
    df = df.applymap(lambda x: x.lstrip() if isinstance(x, str) else x)

    df.dropna(inplace=True)
     #create a column that will be the notes as a list
    df['Notes_list'] = df['Notes'].apply(lambda x: x.split(','))
    #do the same for the "extracted" notes
    df['extracted_list'] = df['extracted_notes'].apply(lambda x: x.split(','))
    return df

@st.cache_data()
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
    background_position="% 10%",
    margin_top="",
    image_width="100%",
    image_height="40%",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
    )


def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )

add_logo('frag_logo.png')

#st.set_page_config(layout="wide")

project_url = 'https://github.com/nisha-kaushal/Fragrance_Analysis_and_Recommendations'
st.title('Fragrance Recommendations')
#st.write('by Nisha Kaushal')
st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>ABOUT THIS RECOMMENDATION SYSTEM</span>
''', unsafe_allow_html = True)
st.write('This web app is part of my [Fragrances Analysis and Recommendation](%s) project, in which I analyze the fragrance notes found in popular fragrances, and compare them with notes preferred by survey respondents' % project_url)
st.write('This recommendation system is an easy way for users to find fragrances that match their preferred note combinations.')
st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>HOW ARE THE RECOMMENDED FRAGRANCES CHOSEN?</span>
''', unsafe_allow_html = True)


st.markdown("""
This app utilizes [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity#:~:text=Cosine%20similarity%20then%20gives%20a,the%20field%20of%20data%20mining.)
to initially find the closest matching notes between the user's preferred notes, and the notes of each fragrance. ***Cosine Similarity scores 
closer to 1 are more likely to be a match.*** Then, using any user feedback rating given in the "Fragrance Feedback" page, 
the results are then sorted to have the highest ratings show first. This is particularly useful if multiple recommended fragrances 
have the same cosine similarity scores.  

<span style='color:#FEFFBE;font-weight:bold;font-style:italic; font-size: 125%'>Some Notes About The Recommendations:</span>
1. Some cosine similarity scores may be on the lower side, due to the amount of notes found in the suggested fragrances vs. the amount of the user's preferred notes. For example, if the inputted notes are Vanilla, Cinnamon, and Orange, you will find that Tom Ford's Tobacco Vanille (which has the notes Tobacco, Vanilla, and Cinnamon) ranks higher than Patchouli Intense Eau de Parfum by PARFUMS DE NICOLAI, which contains all of the inputted notes plus much more. This is because there is an overall higher match between the inputted list of notesand Tobacco Vanille's notes, which Patchouli Intense dilutes the orange, vanilla, and cinnamon notes with all of the other notes found in it. In addition, it is possible that not all notes chosen will be seen in the final recommendations, especially if several notes from different categories are 
chosen. <span style='color:#A4E675;font-weight:bold'>Essentially, lower cosine similarity scores mean that any matching notes may be diluted by other notes that are present in the fragrance.</span>

2. Most of the fragrances will have an average rating of **0**. ***This does not mean the fragrance is bad!***  All it means is that no one has given feedback on the fragrance. 

3. Because this app is a demo app, currently user feedback does not get recorded, thus the average rating does not get updated. Any non-zero average ratings that may occur have been given by Nisha herself. That being said, any non-zero average ratings are accurate to Nisha's preferences! 
""", unsafe_allow_html=True)
df = final_df()
get_all = get_all_notes(df)
cat_dict = category_dict(get_all[0])
#frag_note_list = pd.Series(list(cat_dict.values()))

st.header('Get Your Fragrance Recommendations: ')

select_cat = st.selectbox('Select a category', cat_dict.keys(), key = '1')

selected_notes = st.multiselect('Select note(s) from this category', cat_dict[select_cat], key = '2')

more_notes = st.radio('Would you like to add more notes from a different category?', ['No', 'Yes'], key = '3')

#create a list of categories already chosen so that they won't be shown again when user chooses to add another
#category
used_cats = [select_cat]

#set the color of the radio circles that will be used:

if more_notes == 'Yes':
    key_list = [key for key in list(cat_dict.keys()) if key not in used_cats]
    select_cat1 = st.selectbox('Select a category', key_list, key = '4')
    used_cats.append(select_cat1)
    selected_notes += st.multiselect('Select notes from this category', cat_dict[select_cat1], key = '5')

    third_cat = st.radio('Would you like to add more notes from a third category?', ['No', 'Yes'], key = '6')
    if third_cat == 'Yes':
        key_list = [key for key in list(cat_dict.keys()) if key not in used_cats]
        select_cat2 = st.selectbox('Select a category', key_list, key = '7')
        used_cats.append(select_cat2)
        selected_notes += st.multiselect('Select notes from this category', cat_dict[select_cat2], key = '8')

        fourth_cat = st.radio('Would you like to add more notes from a fourth category?', ['No', 'Yes'], key = '9')

        if fourth_cat == 'Yes':
            key_list = [key for key in list(cat_dict.keys()) if key not in used_cats]
            select_cat3 = st.selectbox('Select another category', key_list, key = '10')
            used_cats.append(select_cat3)
            selected_notes += st.multiselect('Select notes from this category', cat_dict[select_cat3], key = '11')

            fifth_cat = st.radio('You can add notes from one more category, would you like to?', ['No', 'Yes'], key = '12')

            if fifth_cat == 'Yes':
                key_list = [key for key in list(cat_dict.keys()) if key not in used_cats]
                select_cat4 = st.selectbox('Select the final category', key_list, key='13')
                selected_notes += st.multiselect('Select notes from this category', cat_dict[select_cat4], key='14')




if st.button('Recommend'):
    n = 5
    fragrances, notes_list, cosine_sims, avg_ratings = give_recommendation(selected_notes, cat_dict, df)
    try:
        for i in range(n):
            frag_no = str(i + 1)
            frag_note_list = notes_list[i]
            frag = fragrances[i]
            cs = str(cosine_sims[i])
            avg = str(avg_ratings[i])
            #st.subheader(f'Fragrance #{frag_no}: {frag}')
            st.markdown(f"<span style='color:#62BD91;font-weight:bold;font-size:200%'>Fragrance #{frag_no}: {frag} </span>", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 125%'>Fragrance Notes: </span> <span style = 'font-style:italic; font-size:125%'>{frag_note_list} </span>", unsafe_allow_html = True)
            st.markdown(f"<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 125%'>Cosine Similarity Score: </span> <span style = 'font-stye:italic; font-size:125%'>{cs} </span>", unsafe_allow_html = True)
            st.markdown(f"""<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 125%'>Average Rating: </span> <span style = 'font-stye:italic; font-size:125%'>{avg} </span>""", unsafe_allow_html = True)

    except: #in case there is less than 5 recommendations:
        st.markdown('***There are no more recommendations to show***')




