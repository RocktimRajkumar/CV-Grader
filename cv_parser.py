import utils.pdf2text as pdf2text
import spacy
from spacy.matcher import Matcher
import re

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

cv_text = pdf2text.get_Text("./resumes/Resume.pdf")

print(extract_name(cv_text))
print(extract_mobile_number(cv_text))