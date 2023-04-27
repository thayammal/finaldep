import requests, PyPDF2
from io import BytesIO
import io
import pandas as pd 
import PyPDF2
import string
import os
import glob
import nltk
import time
from nltk.corpus import stopwords
import datetime
import logging    #change 1



def download_pdf_and_save_folder(pdf_link,folder,cat_name,cat_val):

    # print("download pdf link  ---------------- >>>> ",pdf_link)
    # logging.info(f"download pdf link : {pdf_link}")  #change 1

    current_time = datetime.datetime.now()
    time = str(current_time).replace(" ",'_')
    print("time >> ",time)

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' } 
    response = requests.get(pdf_link, headers = headers)
    pdf_name = pdf_link.split("/")[-1]
    pdf_name = pdf_link.split(".")
    # print("pdf_name --------->>>>>> ",pdf_name)

    # logging.info(f"pdf_name : {pdf_name}")  #change 1
    if cat_name != 0:
        file = open(f"{folder}/{cat_name}/{pdf_name[0]}.pdf", "wb")
    else:
        file = open(f"{folder}/{pdf_name}", "wb")
    file.write(response.content)
    file.close()
    return pdf_name


def pdf_existance_check(pdf_dir,pdf_name):
    pdf_file = []
    for dirpath, dirnames, filenames in os.walk(pdf_dir):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            pdf_file.append(filename)
    indicator = any(pdf_name in x  for x in pdf_file)   
    return indicator


def word_count(words):
    counts = dict()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts


def category_selection1(pages_text):
    if len(pages_text.strip()) != 0:
        for line in io.StringIO(pages_text):
            if 'strateg' in line.lower():
                cat_name = "strategy"
            elif 'polic' in line.lower():
                cat_name = 'policy'
            elif ('guidelines' in line.lower() or 'guide' in line.lower()):
                cat_name = 'guildlines'
        return cat_name
    else:
        return ""

def category_selection2(x):
    catagory_name = 0
    keywords = ['strateg','polic','guidline']
    my_dict = {}
    for i in keywords:
        y = [j for j in x if i in j[0]]
        result = sum(tup[1] for tup in y)
        my_dict[i] = result
    print("my_dict : ",my_dict)
    s = len(set(my_dict.values()))
    if s>2:
        cat_name = max(my_dict, key=my_dict.get)
        cat_val = max(my_dict.values())
        if cat_val >= 20:
            catagory_name = 'policy' if cat_name == 'polic' else "strategy" if cat_name == 'strateg' else 'guildlines' 
    return catagory_name

def pdf_score(cat_name,sorted_word_count_in_pdf):
    df = pd.read_excel("C:/Users/admin/Desktop/INT-INFOWAREHOUSE/CyberSecurity_Deployment/Regulator.xlsx", sheet_name='scoring')
    if cat_name == 'policy':
        colum_name = 'cyber_security_policy'
    if cat_name == 'strategy':
        colum_name = 'Cyber_security_strategy'
    if cat_name == 'guildlines':
        colum_name = 'Cyber_security_guidelines'

    score_keyword = [i for i in df[colum_name].tolist() if str(i) != 'nan']

    total_score = 0
    for i in score_keyword:
        y = i.split('-')
        word = y[0].lower()
        weight = y[1]
        for j in sorted_word_count_in_pdf:  
            if word == j[0]:
                frequency = j[1]
                sub_score = int(weight) * int(frequency)
                total_score += sub_score
    return total_score


def pdf_selector(pdf_link,folder,country_name):
    filter_1 = False
    filter_2 = False
    filter_3 = False
    filter_4 = False
    filter_5 = False

    try:
        pdf_name = pdf_link.split("/")[-1]
        ispdfexit = pdf_existance_check(folder,pdf_name)
        
        if ispdfexit:
            pass
        else:
            print("-----------------------------------else-------------------------------")

            df = pd.read_excel("C:/Users/admin/Desktop/INT-INFOWAREHOUSE/CyberSecurity_Deployment/Regulator.xlsx", sheet_name='keywords')
            keyword_list = [i for i in df['content_keywords'].tolist() if str(i) != 'nan']

            basic_pdf_keywords = [i for i in df['pdf_basic_keyword'].tolist() if str(i) != 'nan'] 

            ##pdf link
            headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' } 
            time.sleep(0.01)
            response = requests.get(pdf_link, headers = headers)
            my_raw_data = response.content
            pdf_content = ''

            with BytesIO(my_raw_data) as data:
                read_pdf = PyPDF2.PdfReader(data)
                pages_text1 = read_pdf.pages[0].extract_text()
                pages_text2 = read_pdf.pages[1].extract_text()
                # print("pages text >>>>>>>>>. ",pages_text)
                for page in range(len(read_pdf.pages)):
                    each_page_content = read_pdf.pages[page].extract_text()
                    text = each_page_content.replace("\n",' ').lower()
                    pdf_content += text
                    
            swa_1 = pdf_content.split()           
            filtered_words = [word for word in swa_1 if word not in stopwords.words('english')]
            word_fre = word_count(filtered_words)        
            sorted_word_count_in_pdf = sorted(word_fre.items(), key=lambda x:x[1], reverse=True)
            # print("sorted_word_count_in_pdf",sorted_word_count_in_pdf)

            ## pdf path


            ## filter 1.
            frequency_keys = [i for i in df['word_frequency_count'].tolist() if str(i) != 'nan']
            y = []
            for i in frequency_keys:
                x = i.lower().split("-")
                if '/' in x[0]:
                    w1 = x[0].split("/")[0]
                    w2 = x[0].split("/")[1]
                    c = x[1]
                    y1 = [w1 for i in sorted_word_count_in_pdf if ((w1 in i[0] or w2 in i[0]) and (i[1] >= int(c)))]
                    y.append(y1[0])
                else:
                    w = x[0]
                    c = x[1]
                    y2 = [w for i in sorted_word_count_in_pdf if ((w in i[0]) and (i[1] >= int(c)))]
                    y.append(y2[0])

            if len(y) == 5:
                filter_1 = True
                print("filter 1 pass")
            
            ## filter 2.
            basic_count = 0
            for j in basic_pdf_keywords:            
                for i in set(filtered_words):
                    if j == i:
                        basic_count +=1
            print("basic count : ",basic_count)
            if basic_count >= 6:   # 9
                filter_2 = True
                print("filter 2 pass")

            ## filter 3.
            year_list = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025','2026','2027','2028','2029','2030','2031','2032','2033','2034','2035','2036','2037']
            yearcounts = dict()
            for j in year_list:            
                for i in set(filtered_words):
                    if j in i:                    
                        if j in yearcounts:
                            yearcounts[j] += 1
                        else:
                            yearcounts[j] = 1

            # print("count >> ",yearcounts)

            if len(yearcounts) >= 2:
                filter_3 = True
                print("filter 3 pass")
            if len(yearcounts) == 1:
                if int(list(yearcounts.keys())[0]) >= 2020:
                    filter_3 = True
                    print("filter 3 pass")

            ##filter 4.
            match_keywords = [i for i in keyword_list if (i.lower().replace(' ','') in pdf_content.replace(" ",''))]
            if len(match_keywords) >= 15:
                filter_4 = True
                print("filter 4 pass")

            ##filter 5.
            ucountry_name = country_name.replace(' ','').lower()
            if ucountry_name in pdf_content.replace(" ",''):
                filter_5 = True
                print("filter_5 pass")


            ### if all filtering conditions are satisfied then download this pdf.
            if filter_1 and filter_2 and filter_3 and filter_4 and filter_5:
                try:                   
                    cat_name = category_selection1(pages_text1.strip())
                    #DEBUG: Check cat_name element
                    if len(pages_text1.strip()) == 0:
                        cat_name = category_selection1((pages_text2.strip())[:100])
                except:
                    cat_name = category_selection2(sorted_word_count_in_pdf)
                print("cat_name : ",cat_name)
                cat_val = pdf_score(cat_name,sorted_word_count_in_pdf)
                # if cat_val > 350:
                download_pdf_name = download_pdf_and_save_folder(pdf_link,folder,cat_name,cat_val)

            return download_pdf_name
    except Exception as e:
        print(e)
        # logging.exception("Exception occurred")
        print("----pdf can not download----")
        return "No pdf downloaded"





