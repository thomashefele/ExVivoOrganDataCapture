import os
from PyPDF2 import PdfFileReader
import pandas as pd

# helper functions
def load_all_pages(pdf_path):
    temp = open(pdf_path, 'rb')
    PDF_read = PdfFileReader(temp)

    count = PDF_read.numPages
    all_pages_text = ""
    for i in range(count):
        page = PDF_read.getPage(i)
        all_pages_text += page.extractText()
  
    return all_pages_text

def get_line(text, line_index):
    return text.splitlines()[line_index]

def find_line_index(text, line_text):
    text_list = text.splitlines()
    index = text_list.index(line_text)
    return index

def get_line_after_header(text, line_text):
    text_list = text.splitlines()
    index = text_list.index(line_text)
    return text_list[index+1]

def get_multiple_lines_after_header(text, line_text):
    text_list = text.splitlines()
    while ' ' in text_list:
        text_list.remove(' ')
    return_values = []
    for index, x in enumerate(text_list):
        if x == line_text:
            while containsNumber(text_list[index+1]):
                return_values.append(text_list[index+1])
                index += 1
    return return_values

def containsNumber(value):
    for character in value:
        if character.isdigit():
            return True
    return False
  
parameter_name_list = ['ID', 
                       'Blood Type:', 'History of diabetes: ', 'Height: ', 
                       'We i g h t :  ', 'Age : ', 'Body Mass Index (BMI): ', 
                       'Gender: ', 'KDPI:', 'Ethnicity/race: ', 
                       'Cause of death: ', 'Mechanism of injury: ', 
                       'Circumstance of death: ', 'Cold Ischemic Time:', 
                       'Donor meets DCD criteria: ', 
                       'Cardiac arrest/downtime?: ', 'CP R adminis t e re d?: ',
                       'History of diabetes: ', 'History of cancer: ', 
                       'History of hypertension: ', 
                       'History of coronary artery disease (CAD): ',
                       'Previous gastrointestinal disease: ', 
                       'Cigarette use (>20 pack years) ever: ',
                       'Heavy alcohol use (2+ drinks/daily): ',
                       'I.V. drug usage: ']

parameter_name_list_2 = ['Average/Actual BP', 
                       'Average heart rate (bpm)', 
                       'High BP', 'Duration at high (minutes)', 
                       'Low BP', 'Duration at low (minutes)', 'WBC (thous/mcL)',
                       'RBC (mill/mcL)', 'HgB (g/dL)', 'Hct (%)', 
                       'Plt (thous/mcL)',
                       'Na (mEq/L)', 'K+ (mmol/L)', 'Cl (mmol/L)', 
                       'BUN (mg/dL)', 'Creatinine (mg/dL))', 'Glucose (mg/dL)',
                       'Total Bilirubin (mg/dL)', 'Direct Bilirubin (mg/dL)',
                       'Indirect Bilirubin (mg/dL)', 'SGOT (AST) (u/L)',
                       'SGPT (ALT) (u/L)', 'Alkaline phosphatase (u/L)',
                       'Prothrombin (PT) (seconds)', 'PTT (seconds)'
                       '            % Glomerulosclerosis: ',
                       '            Biopsy type: ',
                       '            Glomeruli Count: ']

df = pd.DataFrame(columns=parameter_name_list + parameter_name_list_2)

directory = '/content/'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if f.endswith(".pdf"):
        if os.path.isfile(f):
            text = load_all_pages(f)
            parameter_value_list = []

            parameter_value_list.append(get_line(text, 9))

            for param in parameter_name_list[1:]:
                parameter_value_list.append(get_line_after_header(text, param))

            for param in parameter_name_list_2:
                parameter_value_list.append(get_multiple_lines_after_header(text, param))

            df_length = len(df)
            df.loc[df_length] = parameter_value_list
