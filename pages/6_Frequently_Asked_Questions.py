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

add_logo("frag_logo.png")


st.header('FREQUENTLY ASKED QUESTIONS')
st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Have questions? Check below to see if they were answered!</span>
''', unsafe_allow_html = True)
st.markdown("""
**1.** <span style='color:#A4E675;font-weight:bold'>I am looking for a specific fragrance note, but can't find it in the list of inputs. Why?</span>

*The fragrance notes given are based on whatever notes are present among the fragrances
in the dataset used to create the recommender system. As more fragrances are added,
more fragrance notes will be available as well!*

**2.** <span style='color:#A4E675;font-weight:bold'>I've tried one of the recommended fragrances before, and do not think it 
accurately represents the list of notes given. Is there any way this can be a note 
given for future users?</span>

*This recommendation system is currently in its early stages, and as of now there is no 
functionality for this. That being said, a functionality like this will likely be added 
to create a more robust system, so check back periodically!* **RESOLVED**

***NOTE THAT THE ABOVE HAS BEEN IMPLEMENTED VIA THE "FRAGRANCE FEEDBACK" SECTION. However, because
this app is currently in its demo stage, the feedback will not reflect in the recommendations.
Any "average rating" that is non-zero in the suggested fragrances are based on Nisha's own experience
with the fragrance***

**3.** <span style='color:#A4E675;font-weight:bold'>What is the point of the generated username in the "Fragrance Feedback" section?</span>

*The answer to this is two-fold. First, organization. Using your generated username allows for all 
of your feedbacks to be together in our data (if you give feedback for more than one fragrance). In the future, 
I plan on implementing a functionality in which the user could pull their previous feedbacks given. The generated
username will make it easier to do so, as long as you remember! Secondly, it makes it easier on the user, in that they do 
not have to remember another password. Because this app does not take in any personal information, the need for 
a "log-in" option has currently been deemed unnecessary.*

**4.** <span style='color:#A4E675;font-weight:bold'>How are the usernames generated?</span>

*The usernames are completely random! Essentially, we take a random verb from a long list of verbs, tack on 
a random noun from a large list of nouns, and finally tack on a random number between 0 and 100,000. This allows for 
a spectacular amount of unique usernames!*
""", unsafe_allow_html=True)
