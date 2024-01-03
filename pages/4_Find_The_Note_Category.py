import streamlit as st
import json
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

#use HammingDistance to find mismatches between preferred not and notes in list
#will work only if len(p) == len(q)
def HammingDistance(p, q):  # p and q are two sequences of the same length
    num_mismatches = 0
    k = len(p)  # == len(q)
    for i in range(0, k):
        if p[i] != q[i]:
            num_mismatches += 1
    return num_mismatches

##TO DO: Create function that does word suggestion, but a letter is missing or added (Levenshtein distance?)
### Technically could just use Levenshtein Distance for everying, just want to showcase other ways
def LevenshteinDistance(s1, s2):
    if len(s1) > len(s2): #ideally the first input would be > than the second, but if not, do this
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

#Main function to find category:
def find_category(note, cat_dict):

    cats_vals_list = list(cat_dict.values())
    cats_final_list = []
    note = note.lower()
    for lst in cats_vals_list:
        for x in lst:
            cats_final_list.append(x)

    if note in cats_final_list:
        #UPDATE: jasmine was considered in beverages category (where jasmine tea is), so make a separate thing saying it's in white flowers
        if note == 'jasmine':
            cate = 'white flowers'
            return cate

        #same thing as above for peach:
        if note == 'peach':
            cate = 'fruit/vegetable'
            return cate
        for key, value in cat_dict.items():
            for i in value: #the values are list
                if note in i: #if the note is in the list
                    cate = key #then the category is the key
        return cate

    else: #if the note isn't in the list, check if it was just a typo or if it doesn't really exist
        possible_replacements = []
        for n in cats_final_list:
            if len(n) == len(note):
                ham_dist = HammingDistance(note, n)
                if ham_dist == 1:
                    possible_replacements.append(n)
            else: #len(n) != len(note)
                lev_dist = LevenshteinDistance(n, note)
                if lev_dist <= 2: #let's look for 2 or less mistakes to make suggestions
                    possible_replacements.append(n)

        if not possible_replacements: #ie, if list is empty:
            return 'Note not in database. Please check spelling or input a new note'
        else:
            if len(possible_replacements) > 1:
                rep1 = ', '.join(possible_replacements[:-1])
                rep2 = possible_replacements[-1]
                return_statement = f'Not found. Did you mean {rep1}, or {rep2}?'
                return return_statement
            else:
                replacement = ', '.join(possible_replacements)
                return_statement = f'Not found. Did you mean {replacement}?'
                return return_statement


#open the fragrance json, assign to variable
with open('pages/recommended_fragrance_categories.json') as f:
    cats = json.load(f)

st.header("Don't Know What Category To Look For a Note In? Check Below!")
st.markdown('''
With the recommendation system ever-growing, with more and more fragrances and fragrance notes being added regularly, 
it is natural that it may be annoying to parse through each category's list to find the note you are looking for, 
especially if you are unsure of which category a fragrance note belongs to. 

Most of the time, it is relatively simple to understand which category a fragrance note belongs to. For example, 
orange scents would naturally be found in the "citrus" category. But what about a scent like milk? Would it fall under 
the sweet/gourmand category? The musk/animalic category? What if a note isn't even among the options (yet)? 

Whatever the situation, having to parse through all the categories to find your desired note can be daunting. Instead, 
use the tool below to find the category of your desired note, or if the note is present within the notes available so far!

You may be wondering, <span style='color:#FEFFBE;font-weight:bold'>"what if I don't know how to spell the note?"</span>

***If you misspell a note, no worries!*** If your spelling is close enough (but not exact), the output will give 
a "Not found" message, along with the suggested correct spelling for you to input! If you're wondering *how* this was implemented, 
this spelling-correction function is done through [Hamming Distance](https://en.wikipedia.org/wiki/Hamming_distance) and
[Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance). 

''', unsafe_allow_html = True)

st.subheader('Input the note here!')
note = st.text_input("Type the note here")

if st.button('Find the category'):
    cate = find_category(note, cats)
    if cate in cats.keys():
        st.markdown(f"""
        <span style='color:#A4E675;font-weight:bold;font-size: 125%'>{note.upper()} </span> 
        is in the <span style='color:#A4E675;font-weight:bold;font-size: 125%'>{cate.upper()} </span>category""",
                    unsafe_allow_html = True)
    else:
        st.markdown(f"<span style='color:#A4E675;font-weight:bold;font-size: 125%'>{cate.upper()}</span>",
                    unsafe_allow_html = True)


