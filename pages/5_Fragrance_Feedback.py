import streamlit as st
import json
import pandas
import random
import base64
import boto3
from st_files_connection import FilesConnection

def generate_username(list_of_verbs, list_of_nouns, num_max = 100000):
    len_verbs = len(list_of_verbs)
    verb_index_list = [v for v in range(len_verbs)]
    len_nouns = len(list_of_nouns)
    noun_index_list = [j for j in range(len_nouns)]

    rand_verb_idx = random.choice(verb_index_list)
    verb = list_of_verbs[rand_verb_idx]
    rand_noun_idx = random.choice(noun_index_list)
    noun = list_of_nouns[rand_noun_idx]
    random_num = random.randint(0, num_max)
    num_str = str(random_num)
    username = verb + noun + num_str

    return username


def users_set(user_feedback_dict):
    r = list(user_feedback_dict.values())
    r_list = []
    for di in r:  # for each dict in the values list
        for ke in di.keys():
            r_list.append(ke)

    r_set = set(r_list)
    return r_set

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

add_logo("frag_logo.png")


##open the files needed, store contents into variabes:
#list of verbs
with open('pages/common_verbs.txt', 'r') as verbs:
    verbs = verbs.read()
    verbs_list = verbs.split('\n')
#list of nouns
with open('pages/most_common_nouns.txt', "r") as nouns:
    nouns = nouns.read()
    nouns_list = nouns.split('\n')

#dictionary of brands (keys) and their fragrances (values)
with open('pages/brands_names.json') as f:
    brands_names = json.load(f)

brands_list = list(brands_names.keys())

#open the user feedback file
with open('pages/user_feedback.json') as uf:
    user_feedback = json.load(uf)

conn = st.connection('s3', type=FilesConnection)

##The below gives a pandas df
df = conn.read("fragrancestreamlit/pages/user_feedback.json", input_format="json", ttl=600)
user_feedback = df
#user_feedback = df
s3 = boto3.client('s3')
bucket_name = 'fragrancestreamlit'
s3_file_name = 'pages/user_feedback.json'

#st.markdown("""App by Nisha Kaushal""")
st.header('WE WANT TO HEAR FROM YOU!')

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Have you tried any of the fragrances? Give your feedback below!</span>
''', unsafe_allow_html = True)
st.markdown("""
Your feedback can help improve our recommendation system!
""")

#TO DO: Generate a unique username for the
previous_user = st.radio('Have you given feedback before?', ['Yes', 'No'], key = '43424')

if previous_user == 'Yes':
    users_list = users_set(user_feedback)
    user = st.text_input("""Please input your unique username here 
    (if you do not remember, please select "No" to generate a new name)""")
    if user: #if the user input something (ie string not empty)
        #check to see if the input is in the user list
        if user not in users_list:
            st.markdown('''USER NOT FOUND. PLEASE INPUT USERNAME. OR SELECT "No" TO 
            GENERATE NEW USERNAME''')

        else: #Take in feedback, add it to the user_feedback file
            brand = st.selectbox('Choose a brand', brands_list, key = '93483')
            if brand: #if a brand is inputted
                fragrance = st.selectbox('Choose a fragrance', brands_names[brand], key = '3002')

                if fragrance: #if a fragrance was chosen
                    fb = st.text_area(f"""
                    Input your feedback for {fragrance}""")
                    if fb:
                        rating = st.slider('Give the fragrance a rating', 1, 5)
                        if rating:
                            new_update = {user: {'rating': rating, 'feedback': fb}}
                            if st.button('Give feedback'):
                                st.markdown('Thank you for the feedback!')
                                #st.markdown("""Thank you for the feedback!""")

                                # now append the new stuff to the orginal user_feedback dictionary


                                if fragrance in list(user_feedback.keys()):
                                    user_feedback[fragrance].update(new_update)
                                else:
                                    user_feedback[fragrance] = new_update
                                ##TO DO: update user_feedback file
                                with open('pages/user_feedback.json', 'w') as new:
                                    json.dump(user_feedback, new)

                                with open('pages/user_feedback.json', 'rb') as rb:
                                    s3.upload_fileobj(rb, bucket_name, 'pages/user_feedback.json')

else: #We have a new user!
    user = generate_username(verbs_list, nouns_list)
    st.markdown(f"""
    If you would like to give feedback for other fragrances in the future, please take note of unique username:
    <span style='color:#7F9183;font-weight:bold;font-style:italic; font-size: 125%'>{user.upper()}</span>
    """, unsafe_allow_html=True)
    #Let user pick the brand
    brand = st.selectbox('Choose a brand', brands_list, key = '75')
    if brand:
        fragrance = st.selectbox('Choose a fragrance', brands_names[brand], key = '20')
        if fragrance:
            fb = st.text_area(f"""
                Input your feedback for {fragrance}. Press Enter/Return once complete""")
            if fb:
                rating = st.slider('Give the fragrance a rating', 1.0, 5.0, step = 0.5)
                if rating:
                    new_update = {user: {'rating': rating, 'feedback': fb}}
                    if st.button('Give feedback'):
                        st.markdown('Thank you for the feedback!')

                        # now append the new stuff to the orginal user_feedback dictionary

                        if fragrance in list(user_feedback.keys()):
                            user_feedback[fragrance].update(new_update)
                        else:
                            user_feedback[fragrance] = new_update

                        ##TO DO: update user_feedback file
                        with open('pages/user_feedback.json', 'w') as new:
                            json.dump(user_feedback, new)
                            
                        with open('pages/user_feedback.json', 'rb') as rb2:
                            s3.upload_fileobj(rb2, bucket_name, 'pages/user_feedback.json')


