import streamlit as st
import nltk
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')
import pandas as pd
import base64, random
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
import pafy
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course
import plotly.express as px
import time, datetime
import google.generativeai as palm
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv,find_dotenv
import json


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


palm.configure(api_key=os.getenv("PALM_API_KEY"))


def get_table_download_link(df, filename, text):

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

def file_uploader(pdf_file):
    save_image_path = './Uploaded_Resumes/' + pdf_file.name
    with open(save_image_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    show_pdf(save_image_path)
    resume_data = ResumeParser(save_image_path).get_extracted_data()
    return resume_data,save_image_path

st.set_page_config(
    page_title="Resume Analyzer",
)

def get_response(resume_text):
    response = palm.generate_text(prompt=f"Grade this resume: {resume_text} on a scale of 1-10. Grade it on the basis of education, work experience, projects, awards & achievements and skills. Give individual and overall grade. Give positive points about the resume and also dont give the answer in single line give it in pointers, and display the grading in a good manner")
    # print(response.result)
    return response.result

def get_role(resume_text):
    response = palm.generate_text(prompt=f"Give answer in one word, according to the resume: {resume_text}, candidate has experience in which role. Don't mention skills, education, experience, projects and links")
    # print(response.result)
    return response.result


def get_level(resume_text):
    response = palm.generate_text(prompt=f"Give answer in one word, according to the resume: {resume_text}, what is the level of the candidate: (Fresher, Intermediate, Experienced).")
    # print(response.result)
    return response.result

def get_skills(skills,resume_text):
    response = palm.generate_text(prompt=f"Give answer in form of string seperated by commas, the candidate has following skills:{get_skills}, recommend 8 missing software skills if the desired role is {get_role(resume_text)}. without giving their definition or explanation")
    print(response.result)
    return response.result

def run():
    st.title("Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Resume Analyzer", "Resume Builder", "Resume Matching","Personality Insights"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # Resume analysing
    if choice == 'Resume Analyzer':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            resume_data,save_image_path = file_uploader(pdf_file)
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                st.markdown(f'''<h4 style='text-align: left; color: #d73b5c;'>You are at {get_level(resume_text)} level.</h4>''',
                                unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')
                missing = get_skills(resume_data['skills'],resume_text)
                missing_skills = list(missing.split("\n"))
                

                ##  recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                st.success("Our analysis says you are looking for " + get_role(resume_text)+" role.")
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=missing_skills, key='2')
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        rec_course = course_recommender(uiux_course)
                        break

                                ### Resume writing recommendation
                st.subheader("**Resume Score and Recommendations💡**")
                st.success(get_response(resume_text))
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")

            else:
                st.error('Something went wrong..') 

    elif choice == "Resume Builder":
        experience = st.text_input("experience")
        education = st.text_input("education(with duration)")
        work_experience = st.text_input("work_Experience-with duration and work done(if any)")
        information = "Experiencr"+ experience+ "Educstion" + education +"Work Experience" +work_experience
        job_link = st.text_input("link")
        if job_link:
            user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0']



            response = requests.get(job_link, headers={'User-Agent': random.choice(user_agents)})
            print(response.status_code)
            content = response.text

            soup = BeautifulSoup(content,"html.parser")
            job_description_raw_text = soup.get_text().replace('\n','').strip()
            print(job_description_raw_text)

            job_description = palm.generate_text(prompt=f"Get the job decription from the following text: {job_description_raw_text}.")
            print(job_description.result)
            resume_output = palm.generate_text(prompt=f"Get the job decription from the following text: {job_description_raw_text} and Write a keyword optimized resume for the specific job based on the extracte job description and by using the given information:{information}. For the bullet points, ensure decription is clear with the quantified achievment if necessary. For the skill section only list software skill. Keep the resume page to minimum 2 pages. Education and work experience are seperate entities")
            # print(resume_output.result)
            st.success(resume_output.result)
            result = st.button("Cover letter Generator")
            if result:
                cv_output = palm.generate_text(prompt=f"Write a cover letter for the specific job based on the following job description:{job_description.result} and by using the given information:{information}.")
                st.success(cv_output.result)

    elif choice == "Resume Matching":
        
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        job_link = st.text_input("link")
        if pdf_file is not None and job_link is not None:
            resume_data,save_image_path = file_uploader(pdf_file)
            if resume_data and job_link:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0']

                response = requests.get(job_link, headers={'User-Agent': random.choice(user_agents)})
                print(response.status_code)
                content = response.text

                soup = BeautifulSoup(content,"html.parser")
                job_description_raw_text = soup.get_text().replace('\n','').strip()
                print(job_description_raw_text)

                prompt = """You are a job role description extracter. You will take the text and extract the job role description or what will be the work of the role from the text"""
                model = palm.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt + job_description_raw_text)
                print(response.text)

                # job_description = palm.generate_text(prompt=f"Return the job decription from the given text: {job_description_raw_text}.")

                resume_output = palm.generate_text(prompt=f"Check if the candidate with the resume : {resume_text} is a good match or not for the following job description: {response.text} on the basis of level of experience, skillset and work experience with a breif explaination. Also provide recommendations. Do add Yes or No in the answer")
                # print(resume_output.result)
                st.success(resume_output.result)
                if "Yes" in resume_output.result:
                    result = st.button("Cover letter generator")
                    if result:
                        cv_output = palm.generate_text(prompt=f"Write a Cover letter for the specific job based on the following job description:{response.text} and by using the information from the resume :{resume_text}.")
                        st.success(cv_output.result)

    else:
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            resume_data,save_image_path = file_uploader(pdf_file)
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                BASE_URL = "https://api.humantic.ai/v1/user-profile/create"  # Base URL for create endpoint
                headers = {
                'Content-Type': 'application/json'
                }
                API_KEY = os.getenv("HUMANTIC_API_KEY")
                USER_ID = "201132@gmail.com"  # or, any unique identifier

                url = f"{BASE_URL}?apikey={API_KEY}&userid={USER_ID}&analysistype=talent"

                data = resume_text
                payload = json.dumps(data)

                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.status_code, response.text)
                time.sleep(7)
                FETCH_URL= "https://api.humantic.ai/v1/user-profile"  # Base URL for the FETCH endpoint

                url = f"{FETCH_URL}?apikey={API_KEY}&id={USER_ID}"

                response = requests.request("GET", url, headers=headers)
                # print(response.status_code, response.text)
                behaviouralFactor_raw = response.json()['results']['persona']['hiring']['behavioural_factors']
                print(behaviouralFactor_raw)
                name = []
                score = []
                for key,value in behaviouralFactor_raw.items():
                    name.append(key)
                    score.append(value['score'])

                behaviouralFactor = {"name": name, "score":score}
                print(behaviouralFactor)

                oceanPersonality_raw = response.json()['results']['personality_analysis']['ocean_assessment']
                print(oceanPersonality_raw)
                name = []
                score = []
                for key,value in oceanPersonality_raw.items():
                    name.append(key)
                    score.append(value['score'])

                oceanPersonality = {"name": name, "score":score}
                print(oceanPersonality)
                behaviour_data = pd.DataFrame(behaviouralFactor)
                behaviour_data=behaviour_data.set_index("name")
                st.bar_chart(behaviour_data)

                ocean_data = pd.DataFrame(oceanPersonality)
                ocean_data=ocean_data.set_index("name")
                st.bar_chart(ocean_data)
                personality = palm.generate_text(prompt=f"Use {oceanPersonality_raw} and {behaviouralFactor_raw} to depict the personality of the user with detailed explation of each trait and what impact these traits can have in a job role")
                st.success(personality.result)



                    
    
run()
