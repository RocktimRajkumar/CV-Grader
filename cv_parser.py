import utils.pdf2text as pdf2text
import spacy
from spacy.matcher import Matcher
import re
import pandas as pd
import multiprocessing as mp

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)


def extract_name(resume_text):
    nlp_text = nlp(resume_text)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

    matcher.add('NAME', None, [*pattern])

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        if 'name' not in span.text.lower():
            return span.text


def extract_mobile_number(text):
    mob_num_regex = r'''(0)?(\+91)?[-\s]?(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\) [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
    phone = re.findall(re.compile(mob_num_regex), text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number


def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def check_skills(word, skills_data):

    for skill in skills_data:
        if str(word).lower() == str(skill).lower():
            return str(skill)
    return False


def extract_skills(resume_text):

    nlp_text = nlp(resume_text)

    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    data = pd.read_csv('./utils/skills_db.txt', header=None, delimiter='\n')
    # extract values
    skills_data = data[0].tolist()

    pool = mp.Pool(mp.cpu_count())

    skills = [pool.apply_async(check_skills, args=(
        str(word), skills_data))for word in nlp_text.noun_chunks]

    token_skills = [pool.apply_async(check_skills, args=(
        str(word), skills_data)) for word in tokens]

    skills.extend(token_skills)

    skills = [p.get() for p in skills if p.get() is not False]

    return list(set(skills))


if __name__ == '__main__':

    cv_text = pdf2text.get_Text("./resumes/cv1.pdf")

    print(extract_name(cv_text))
    print(extract_mobile_number(cv_text))
    print(extract_email(cv_text))
    print(extract_skills(cv_text))
