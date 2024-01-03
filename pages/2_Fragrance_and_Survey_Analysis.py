import streamlit as st
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import altair as alt
import base64
# from About import add_logo #to add the logo at the top of the sidebar
# from About import build_markup_for_logo

@st.cache_data#(allow_output_mutation=True)
def df_edits(df):
    df.dropna(inplace = True)
    df['Notes_list'] = df['Notes'].apply(lambda x: x.split(','))
    df['Extracted_list'] = df['extracted_notes'].apply(lambda x: x.split(','))
    df['notes_length'] = df['Notes_list'].apply(lambda x: len(x))
    df['extracted_length'] = df['Extracted_list'].apply(lambda x: len(x))

    return df


@st.cache_data#(allow_output_mutation=True)
def grouped_df(df):
    df_edited = df_edits(df)
    grouped = df_edited.groupby('Brand').size()
    grouped_df = grouped.to_frame('Amount of Fragrances').reset_index().sort_values(by='Amount of Fragrances',
                                                                                    ascending=False)
    return grouped_df

@st.cache_data#(allow_output_mutation=True)
def get_cos_sims(df, col1, col2):
    cos_sims = []
    for i in range(len(df)):
        #create a corpus of the values from the two columns at row i:
        corpus = [df[col1].loc[i], df[col2].loc[i]]
        tfidf = TfidfVectorizer()
        tfidf_mat = tfidf.fit_transform(corpus)
        cos_sim = cosine_similarity(tfidf_mat, tfidf_mat)
        cos_sims.append(cos_sim[0][1])
    return cos_sims

@st.cache_data#(allow_output_mutation=True)
def survey_pref_df(survey_df):
    def fragrance_brand_list(list_str):
        split_str = list_str.split(', ')
        return split_str

    survey_df['frag_brand_list'] = survey_df['(Optional) Which fragrance brand(s) have you used, or which brand(s) have you considered trying? If the brand is not mentioned, please input into the "Other" selection. Selections are in alphabetical order for your convenience :)'].apply(fragrance_brand_list)

    empt_dict = dict()
    for fl in survey_df['frag_brand_list']:
        for fl_list_elem in fl:
            if fl_list_elem not in empt_dict.keys():
                empt_dict[fl_list_elem] = 1

            else:
                empt_dict[fl_list_elem] += 1

    surv_pref_ser = pd.Series(empt_dict, name='Counts')

    surv_pref_df = surv_pref_ser.to_frame().reset_index()

    surv_pref_df.rename(columns={"index": "Brand Name"}, inplace=True)

    return surv_pref_df


@st.cache_data#(allow_output_mutation=True)
def surv_df():
    survey_data = pd.read_csv('pages/fragrance_survey_data.csv')
    survey_data.fillna('none', inplace=True)
    return survey_data

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

df = pd.read_csv("pages/full_perfume_data.csv")
df_edited = df_edits(df)

grouped_df = grouped_df(df_edited)
st.header('BRANDS VS. CONSUMERS: Do fragrance brands give the consumers what they want?')

st.markdown('''
This project was originally created through Jupyter Notebooks. To view the original analysis content (including code), 
check out the Jupyter Notebook [here](https://nbviewer.org/github/nisha-kaushal/Fragrance_Analysis_and_Recommendations/blob/main/Fragrance_Deep_Dive_Part_1.ipynb).

''')

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Background</span>
''', unsafe_allow_html = True)

st.markdown("""
The art of perfumery has been prevalent for thousands of years, all the way back to the ancient 
civilizations of Mesopotamia and Indus Valley. Within the past few hundred years, perfumes have become 
a commonly sought-after product, because of the unique scents that brands have blended together. This has led
to consumers building their own scent preferences, with some even having their own 'signature scent.' While 
consumers have acquired their own scent style, it can bring up the question- How well do brands know their customer 
base, and do they add the notes that are the most sought-after into their fragrances regularly?

Through the analysis below, I will explore the brands and their fragrances, and compare the results with 
the survey data. 
""")

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Dataset Description</span>
''', unsafe_allow_html = True)
st.markdown('''
<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 130%'>Fragrance Dataset</span>

The original dataset can be found [here](https://www.kaggle.com/datasets/nandini1999/perfume-recommendation-dataset). It
is of the shape (2191, 5), with "Name," "Brand," "Description," "Notes," and "Image URL" as the features. As a fragrance hobbyist, 
I found that there were only a handful of fragrances that I have heard of. Because of this, I decided to add more fragrances to the dataset myself. 
I initially attempted to do this by webscraping from the popular website, [Fragrantica](https://www.fragrantica.com). I found that 
Fragrantica has limitations to web scraping however, leading me to hard-code new fragrances into the dataset. The final 
data used for the initial analysis has the shape (2215, 5). 

As this project grows, more fragrances will be added, growing the dataset!

<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 130%'>Survey Data</span>

The survey is still open, and can be found [here](https://docs.google.com/forms/d/e/1FAIpQLScGjr5oM_CzUVDHIQ3sr-TISh51U84lXy1rsC9utzrQgFmzBg/viewform). It was advertised on social media platforms, including Facebook, Instagram, and Reddit, with no incentive. 
As of the initial project, this survey has <span style='color:#FEFFBE;font-weight:bold'>70 participants</span>. Because the survey is still open, I expect this number to increase, and the 
analysis will be updated accordingly! 

The survey contains the following questions: 

* <span style='color:#A4E675;font-weight:bold'>"What country do you reside in?"</span> (Required Question)
* <span style='color:#A4E675;font-weight:bold'>"Which fragrance notes do you like?"</span> (Required Question) 
    * This question is in the form of checkboxes, where the participants could choose as many fragrance notes from the top 60 notes found in the sample of the 2000+ fragrances found in the original dataset used in the beginning of this project. 
    * Participants also had an available "Other" box, where they could input their own preferred note, if it did not appear in the 60 notes given
    * This question was given with the assumption that these are what the participants want to smell like if they were given a fragrance
    with the advertised note
* <span style='color:#A4E675;font-weight:bold'>"Which fragrance brand(s) have you used, or which brand(s) have you considered trying? If the brand is not mentioned, please input into the "Other" selection."</span> (Optional Question)
    * The participants were given a checkbox-list of 40 popular fragrance brands, and were allowed to choose as many as they found applicable to the question
    * Like the previous question, they were able to input their own choice through the "Other:" option
* <span style='color:#A4E675;font-weight:bold'>"What is your favorite/go-to fragrance?"</span> (Optional Question)
    * Participants were given the opportunity to input their own choices, with the brand name having its own input section, and the fragrance name having a separate input section

''', unsafe_allow_html = True)

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Dataset Analysis</span>
''', unsafe_allow_html = True)

st.markdown('''
When first looking at the data, I noticed that there were multiple fragrances for many of the brands. 
Let's look at how many fragrances there are per brand (use the slider below the chart to pick how many of 
the "top" brands you want to see!)
''')
## Check out the distribution of brands represented in the dataset
# grouped = df_edited.groupby('Brand').size()
# grouped_df = grouped.to_frame('Amount of Fragrances').reset_index().sort_values(by = 'Amount of Fragrances',
#                                                                                ascending = False)
chart_placeholder = st.empty()
amount = st.slider('How many fragrances to display?', 10, 100, value = 55, step = 5)
if amount <= 65:
    height = 700
elif amount > 65 and amount <= 80:
    height = 900
else:
    height = 1300
c1 = alt.Chart(grouped_df.head(amount)).mark_bar(color = 'indianred').encode(
    x= alt.X('Amount of Fragrances:Q', title = 'Count of Fragrances in Brand'),
    y= alt.Y("Brand:N", title = 'Brand Name', sort = '-x'), tooltip = "Amount of Fragrances:Q",
    color = alt.Color('Amount of Fragrances', scale=alt.Scale(scheme = 'viridis'), legend = None)
).properties(width = 500, height=height, title = f'Fragrance Counts per Brand (Top {str(amount)})')#.interactive()

chart_placeholder.altair_chart(c1, use_container_width=True)

st.markdown('''
Looking through the top 100 brands, it looks like the majority of the fragrance brands are by high-end brands in the fashion 
industry (like Tom Ford), or perfumery houses that have gained recognition over time for their exceptional quality, like 
Parfums De Nicolai and Nishane. There are also niche perfume houses, or perfume houses that are considered "niche", or produce their 
products in a smaller scale, like Zoologist or Imaginary Authors. Overall, the perfumes represented in the dataset are those that can be seen as 
**expensive** or **exclusive**. 

Now that we have an understanding of what brands are represented, we may wonder, which fragrance notes are significantly represented in the 
data? Below are the top 50 notes found among all of the fragrances: 

''')

each_note_count = {}
for note_list in df_edited['Notes_list']:
    for note in note_list:
        note = note.lower().lstrip()
        if note not in each_note_count.keys():
            each_note_count[note] = 1
        else:
            each_note_count[note] += 1

total_notes_counts = pd.Series(each_note_count, name = 'Counts').sort_values(ascending = False)
total_notes_counts = total_notes_counts.to_frame()
total_notes_counts.reset_index(inplace = True)
total_notes_counts.rename(columns = {'index': 'Note'}, inplace = True)

TOP_N = 50
notes_chart = alt.Chart(total_notes_counts.head(TOP_N)).mark_bar().encode(
    x = 'Counts:Q',
    y = alt.Y('Note:N', sort = '-x'),
    color = alt.Color('Counts:Q', scale=alt.Scale(scheme = 'viridis'), legend = None),
    tooltip = 'Counts:Q').properties(
    width = 500, height = 700, title = 'Top {} Notes Used in Fragrances'.format(str(TOP_N)))
st.altair_chart(notes_chart, use_container_width=True)

#dataset has 2191 entries as of rn
st.markdown('''As we can see, the top 6 notes most used are <span style='color:#FEFFBE;font-weight:bold;font-style:italic'>musk, vanilla, patchouli, sandalwood, bergamot, 
            and amber</span>. As of writing this, each of these notes are present in <span style='color:#FEFFBE;font-weight:bold'>22-26%</span> of the fragrances in our dataset. These notes 
            tend to be the common notes used in the base notes of fragrances, meaning the notes that will last the most on the skin and will be the scents that 
            prevail as the fragrance is worn throughout the day. While the other notes can surely be used as 
            base notes, many of them are widely seen as top notes,the notes that are first recognized when a fragrance 
            is applied. Top notes are widely known to be what makes a particular fragrance product unique.
            ''', unsafe_allow_html=True)
st.markdown(''' 
Now, we can ask the question "How well do the brands know their consumers and their preferences?" To get an idea of this, I conducted a survey to collect 
data on consumer brand and scent note preferences. We will take a look into this data in the next section. 
''', unsafe_allow_html=True)

st.markdown('''
<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Survey Analysis</span>
''', unsafe_allow_html = True)
st.markdown('''
<span style='color:#A4E675;font-weight:bold;font-style:italic'>As mentioned, the survey is still open! If you would like to participate, you can find 
it [here](https://docs.google.com/forms/d/e/1FAIpQLScGjr5oM_CzUVDHIQ3sr-TISh51U84lXy1rsC9utzrQgFmzBg/viewform) </span>. The more data, the better!
''', unsafe_allow_html = True)

survey_data = surv_df()

participant_countries = survey_data['Which country do you reside in? (Please use any common abbreviations if applicable, like "USA" for the "United States of America," "UK" for "United Kingdom", "UAE" for "United Arab Emirates", etc). '].unique()
participant_countries = list(participant_countries)

participants = []
for p in participant_countries:
    if p == 'USA' or p == 'Usa':
        participants.append('US')
    else:
        participants.append(p)
participants = set(participants) #gets the unique values only from the list
participants = list(participants) #convert back to a list, will now only have one of each value

part_str = ', '.join(participants[:-1])
part_str = part_str + f', and {participants[-1]}'
st.markdown(f'''
The participants of this survey are from: <span style='color:#FEFFBE;font-weight:bold;font-style:italic'>{part_str}</span>.
''', unsafe_allow_html=True)


st.markdown("""Let's start off by looking at the brands the survey participants have either used, 
or considered using: """)

surv_brand_prefs = survey_pref_df(survey_data)
cp2 = st.empty()
amount2 = st.slider('How many brands to display?', 20, 50, value = 20, step = 5)
c2 = alt.Chart(surv_brand_prefs.head(amount2)).mark_bar().encode(x = 'Counts:Q', y = alt.Y('Brand Name:N', sort = '-x'),
    color = alt.Color('Counts:Q', scale=alt.Scale(scheme = 'viridis'), legend = None),
    tooltip = 'Counts:Q').properties(title = 'Brands Most Used or Considered to Use by Survey Participants')

cp2.altair_chart(c2, use_container_width=True)

st.markdown('''
As we can see, Bath & Body Works is very popular! Out of the 70 survey participants, 33 have reported to using the brand (that's <span style='color:#FEFFBE;font-weight:bold'>47.14%</span> of all participants!). 
It is a staple brand for those young and old, with a lower price point and higher accessibility than most of the other brands on the list. In fact, in 2022,
[Bath & Body Works accumulated \\$7.56 billion USD in sales in 2022](https://www.statista.com/statistics/255838/net-sales-of-bath-und-body-works-worldwide/). This is across their online sales, 
and their sales from their [1800 US and Canada stores, and 425 international stores](https://careers.bathandbodyworks.com/en/about-us/). Among the top 20 brands, 
Bath & Body Works is the one "budget" brand, with most of their fragrances costing under \\$50 USD, whereas the majority of the rest are designer brands, like Gucci and Tom Ford, which can
cost at least \\$50 for smaller-sized bottles, and hundreds of dollars for full size. There are also a couple Middle Easter/Middle Eastern-inspired brands like Kayali and Al Rehab, 
which can be within budget for those looking to spend less for unique fragrances, with Al Rehab having prices as low as \\$9 and Kayali's travel size. 
fragrances at \\$25-27. There is also one celebrity brand placed 6th, "Ariana Grande." With Ariana Grande being named the ["first pop diva of the streaming generation"](https://www.bloomberg.com/graphics/pop-star-ranking/2020-december/ariana-grande-is-the-biggest-pop-star-in-the-world.html) by *Bloomberg*, 
it is not surprising that her fragrances have become almost as popular as she is. 


''', unsafe_allow_html=True)

st.markdown("""Now that we have an idea of the types of brands that the participants are 
 interested in, we can take a look into the specific scent notes that they enjoy, and compare them to the notes that are most 
 common among the fragrances in our original dataset.""")
survey_data['liked_notes'] = survey_data['Which fragrance notes do you like?'].apply(lambda x: x.split(','))
survey_note_count = {}
for note_list in survey_data['liked_notes']:
    for note in note_list:
        note = note.lower().lstrip()
        if note not in survey_note_count.keys():
            survey_note_count[note] = 1
        else:
            survey_note_count[note] += 1

survey_notes_counts = pd.Series(survey_note_count, name='Counts').sort_values(ascending=False)
survey_notes_counts = survey_notes_counts.to_frame()
survey_notes_counts.reset_index(inplace=True)
survey_notes_counts.rename(columns={'index': 'Note'}, inplace=True)

survey_notes_counts['Percentage of Responses'] = survey_notes_counts['Counts'].apply(lambda x: round((x / len(survey_data)) * 100), 3)


#st.subheader('Participant Data vs. Dataset Data')
st.markdown('''<span style='color:#2E7F64;font-weight:bold;font-style:italic; font-size: 130%'>Dataset Data vs. Participant Data</span>''', unsafe_allow_html=True)

interests  = {}
for val in survey_data['(Optional) Which fragrance brand(s) have you used, or which brand(s) have you considered trying? If the brand is not mentioned, please input into the "Other" selection. Selections are in alphabetical order for your convenience :)']:
    val = str(val)
    val = val.split(', ')
    for brand in val:
        if brand not in interests:
            interests[brand] = 1
        else:
            interests[brand] += 1

#Get the mean of the Counts column:
mean_counts = round(survey_notes_counts['Counts'].mean(), 3)
standard_dev = round(survey_notes_counts['Counts'].std(), 3)
over_33_percent = survey_notes_counts[survey_notes_counts['Percentage of Responses'] >= 33]
og_top_n = total_notes_counts.head(len(over_33_percent))

#I will add in a "percentage" column into this one too
og_top_n['Percentage of Fragrances'] = og_top_n['Counts'].apply(lambda x: round((x / len(df_edited)) * 100), 3)

og_n_chart = alt.Chart(og_top_n).mark_bar().encode(
    x = 'Percentage of Fragrances:Q',
    y = alt.Y('Note:N', sort = '-x'),
    color = alt.Color('Percentage of Fragrances:Q', scale=alt.Scale(scheme = 'viridis'), legend = None),
    tooltip = 'Percentage of Fragrances:Q').properties(
    width = 360, height = 500, title = 'Most-Used Notes in Sampled Fragrances')

survey_chart = alt.Chart(over_33_percent).mark_bar().encode(
    x = 'Percentage of Responses:Q',
    y = alt.Y('Note:N', sort = '-x'),
    color = alt.Color('Percentage of Responses:Q', scale=alt.Scale(scheme = 'viridis'), legend = None),
    tooltip = 'Percentage of Responses:Q').properties(
    width = 360, height = 500, title = 'Preferred Fragrance Notes')

fin_chart = alt.hconcat(og_n_chart, survey_chart)
st.altair_chart(fin_chart, use_container_width=True)

st.markdown('''
The above shows the top 17 most frequently used notes in the original dataset, and the top 17 most-preferred
notes indicated by the survey participants. At first glance, we can see that there are only 5 fragrance matches between 
the two sets. Interestingly, musk, the top scent found among the fragrances in our original dataset, is only 
rated at the 9th position in the preferred notes. The popularity of musk's usage is largely due to its lasting power on the skin, 
as well as its ability to blend well with other notes, making it a great fit to be used as a base note in non-linear fragrances (we'll talk about those in a bit). 

Another interesting breakdown is in the <span style='color:#FEFFBE;font-weight:bold'>categories</span> that the notes are from. In the top-used notes from the fragrances in our 
dataset, the overwhelming majority are from more <span style='color:#FEFFBE;font-weight:bold'>natural</span> scent categories, like wood/moss (patchouli, sandalwood, vetiver, cedar), 
floral (rose, lavendar), and spice (vanilla, saffron, tonka bean, cardamom). On the other hand, our participants' top preferred notes are much more 
<span style='color:#FEFFBE;font-weight:bold'>edible/fruity</span> oriented, with 11 of the 17 notes coming from the vegetable/fruits category (coconut, pear, apple, peach), the citrus category (mandarin, lemon, orange), the spice category 
(vanilla, coffee, cinnamon), and the sweet/gourmand category (honey). 

''', unsafe_allow_html=True)

st.markdown('''<span style='color:#62BD91;font-weight:bold;font-size: 180%'>If the top scent notes between the fragrances and the participant preferences are so different, 
does that mean that brands do not cater to the consumers well?</span>''', unsafe_allow_html=True)

st.markdown(''' 
The answer? <span style='color:#FEFFBE;font-weight:bold;font-style:italic'>Not necessarily</span>.

Let's revisit the idea of fragrance complexities (i.e, the idea of base notes and top notes we talked about at the end of 
the "Dataset Analysis" section. There are two main complexity types in fragrances: Linear and Non-Linear. <span style='color:#FEFFBE;font-weight:bold'>Linear</span> fragrances 
are fragrances that essentially only have one or two scent note(s). For most people, the popular variation of linear fragrances would be essential fragrance oils, 
usually used in aromatherapy. There are linear fragrances that are used for every day wear, however. In fact, if you check out our 
Recommendation System, inputting just "rose" as the note choice will yield multiple linear fragrance recommendations, meaning fragrances 
that only have rose in their notes list. These fragrances are meant to [smell the same over time on the skin](https://commodityfragrances.com/blogs/commodity-blog/linear-non-linear-fragrance#:~:text=In%20the%20fragrance%20world%2C%20the,Rose%20note%20detectable%20over%20time.). <span style='color:#FEFFBE;font-weight:bold'>Non-Linear</span> fragrances, on the other hand, are fragrances
that tend to [evolve on the skin over time](https://commodityfragrances.com/blogs/commodity-blog/linear-non-linear-fragrance#:~:text=In%20the%20fragrance%20world%2C%20the,Rose%20note%20detectable%20over%20time.). The way they smell from the initial spray and an hour or more after the initial spray 
are different from each other. These initial scents are known as <span style='color:#FEFFBE;font-weight:bold'>top notes</span>, the notes that initially draw the consumer in. The notes that last the longer time 
on the skin are known as <span style='color:#FEFFBE;font-weight:bold'>base notes</span>. There can also be middle notes, which are exposed while the fragrance 
begins to dry down on the skin. 

So, what does the above have to do with the brands giving the customers what they want? Well, since everyone has their own 
opinions and preferences when it comes to fragrances, it's safe to assume that there are some consumers who prefer linear fragrances, some
who prefer non-linear fragrances, and others who enjoy both! Most popularized fragrances tend to be non-linear, so for now I will be focusing on 
those. 

''', unsafe_allow_html=True)
st.markdown('''
<span style='color:#A4E675;font-weight:bold;font-size: 110%'>Non-Linear Fragrances allow for consumers to experience multiple scent notes in one product. </span>
In other words, non-linear fragrances give a [dynamic experience](https://commodityfragrances.co.uk/blogs/commodity-blog/linear-non-linear-fragrance#:~:text=On%20the%20other%20hand%2C%20a,dynamic%20and%20multidimensional%20sensory%20experience.)
to the consumer, allowing the consumers to experience multiple notes that they may enjoy, as long as the combination of notes exist. In addition, it helps brands continue to produce
unique fragrances, so that consumers continue to be intrigued with the brand. 

For example, let's say consumer A likes the smell of oranges, and is fine with other citrus notes and spice notes. Consumer B enjoys lemon and cinnamon, and is fine with other citrus scents. If there is a fragrance product 
containing some (or all) of these notes on the top, then one spray of the fragrance will most likely be enticing to both consumers A and B, as [top notes are what create the first impression](https://www.ilovecosmetics.co.uk/blog/what-are-fragrance-notes/#:~:text=As%20a%20result%20of%20their,when%20trying%20a%20new%20fragrance.)
Because of this, it is likely the consumers do not pay as much attention to the base notes as they do the top notes. In any case, 
as exemplified by the above visualization, consumers tend to like some of the most popular base notes- vanilla, sandalwood, and musk- so brands can 
focus on creating unique top and middle note blends, and effectively meeting the needs of the consumers. 

<span style='color:#62BD91;font-weight:bold;font-size: 180%'>Conclusion/Future Analysis</span>

Fragrances allow users to express their individuality through the sense of smell. With the thousands of fragrances on the market, 
we may wonder if there really is a fragrance for everybody, and if brands really do cater to the consumers' preferences. Based on the analysis conducted above, 
I believe it is safe to say that consumers can find what they want, at least to some extent. With linear and non-linear fragrance options, 
it is possible for consumers to find fragrances with their preferred scent notes, though in non-linear fragrances, there may be 
additional scent notes that consumers are not fond of. There also may not be fragrances in a consumer's preferred brand that has the particular preferred notes. 
With all the combinations of fragrance notes possible, brands have the capacity to expand their ranges and continue to 
release unique fragrance products that will catch the attention of the masses. 

In the future, for this project as a whole, I would like to delve more into what consumer want in fragrances overall, including ideal price points/how price points 
affect fragrance purchases. With this, I would be able to expand the recommendation system to take into consideration 
price points, and other potential characteristics, like bottle size, bottle color, fragrance type (oil vs. spray), and others. 

''', unsafe_allow_html=True)