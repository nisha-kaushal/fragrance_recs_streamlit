import streamlit as st
import base64

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

# css='''
# [data-testid="stSidebarNav"] {
#     position:absolute;
#     bottom: 0;
# }
# '''

# st.markdown("""
#     <style>
#       section[data-testid="stSidebar"] {
#         top: 50%;
#         height: 80% !important;
#       }
#     </style>""", unsafe_allow_html=True)
# st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

add_logo("frag_logo.png")

st.title('THE FRAGRANCE PREFERENCES PROJECT')
st.markdown('By Nisha Kaushal')
st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>ABOUT THIS PROJECT</span>
''', unsafe_allow_html = True)
st.markdown('''
<span style='color:#7F9183;font-weight:bold;font-style:italic; font-size: 175%'>“Perfume is the art that makes memory speak.” </span> 
<span style='color:#7F9183;font-weight:bold;font-style:italic'>-Francis Kurkdjian </span>

''', unsafe_allow_html = True)

st.markdown("""
With thousands of fragrances on the market, consumers have developed their own, highly-personalized preferences in terms
of fragrance notes that they prefer. For some, the sheer amount of fragrances on the market may be overwhelming, and 
finding a fragrance that fits a particular scent profile can be daunting. With this project, I analyzed the scent note 
composition of fragrances, analyzed the scent preferences of survey respondents (more about that below), and create 
a recommendation system that allows users to input the fragrance notes they desire, outputting 5 fragrances that may 
interest the user based on the input. 
""")

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>DATA SOURCES</span>
''', unsafe_allow_html = True)
st.markdown("""
Part of the fragrance dataset used was found on Kaggle, [here](https://www.kaggle.com/datasets/nandini1999/perfume-recommendation-dataset).
Because the original dataset did not include many fragrances, I attempted to webscrape the data from the popular online fragrance database, [Fragrantica](https://www.fragrantica.com/). 
However, Fragrantica has limitations in the amount of times one can gather data from the website, so I had to result to hard-coding many of the data points.
This dataset was used for analysis of overall fragrance notes distribution amongst the fragrances, and to provide potential 
recommendations for the recommendation system. New fragrances will be added periodically!

The survey was conducted through Google Forms, [here](https://docs.google.com/forms/d/e/1FAIpQLScGjr5oM_CzUVDHIQ3sr-TISh51U84lXy1rsC9utzrQgFmzBg/viewform).
The survey is still active, and the project will be updated periodically based on new data collected through new responses. 
""")

st.markdown("""
<span style='color:#FEFFBE;font-weight:bold;font-style:italic; font-size: 115%'>The project was originally conducted through Jupyter Notebooks. To see the original notebooks (with code), check out the below:</span>

[Dataset Analysis and Survey Analysis](https://nbviewer.org/github/nisha-kaushal/Fragrance_Analysis_and_Recommendations/blob/main/Fragrance_Deep_Dive_Part_1.ipynb)

[Recommendation System](https://nbviewer.org/github/nisha-kaushal/Fragrance_Analysis_and_Recommendations/blob/main/Deep_Dive_Part_2_Fragrance_Recommendation_System.ipynb)

""", unsafe_allow_html = True)

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>PROJECT CONTENTS</span>
''', unsafe_allow_html = True)
st.markdown("""
This project contains 5 parts: 

**1)** <span style='color:#A4E675;font-weight:bold'>Fragrance and Survey Analysis</span>: An analysis report, analyzing 
a dataset containing fragrances (perfumes, body mists, colognes, etc), and a dataset containing survey data from fragrance users

**2)** <span style='color:#A4E675;font-weight:bold'>Recommendation System</span>: Recommendation system that takes in fragrance notes that user 
is looking for, and outputs 5 fragrances that are the most likely to fit the user's needs. Recommendations are based on cosine similarity and user feedback

**3)** <span style='color:#A4E675;font-weight:bold'>Find the Note Category</span>: The above recommendation system categorizes the notes, and 
some notes are not as obvious to place in a category. This section allows for users to find the category for a specific note

**4)** <span style='color:#A4E675;font-weight:bold'>Fragrance Feedback</span>: Allows user to give reviews on fragrances they have tried previously. The 
feedback will then be used in the recommendation system's recommendations

**5)** <span style='color:#A4E675;font-weight:bold'>Frequently Asked Questions</span>: Contains possible questions user may have, with answers


""", unsafe_allow_html = True)
