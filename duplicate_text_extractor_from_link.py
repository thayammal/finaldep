import string
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import pandas as pd
import requests
import time
from cleantext import clean
from pdf_selector_update1 import *

options = Options()
options.add_argument('--headless')

def clean_text(text):
    clean_text = clean(text=text,
                fix_unicode=True,
                to_ascii=True,
                lower=True,
                no_line_breaks=False,
                no_urls=False,
                no_emails=False,
                no_phone_numbers=False,
                no_numbers=False,
                no_digits=False,
                no_currency_symbols=False,
                no_punct=False,
                replace_with_punct="",
                replace_with_url="This is a URL",
                replace_with_email="Email",
                replace_with_phone_number="",
                replace_with_number="123",
                replace_with_digit="0",
                replace_with_currency_symbol="$",
                lang="en"
                )
    return clean_text

def check_text_for_cyber_security(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    y = text.split(" ")
    z =[word for word in y if word !='']
    a = [word.replace("\n",'').replace("\r",'') for word in z]
    text_string = ''.join(a)
    df = pd.read_excel("C:/Users/admin/Desktop/INT-INFOWAREHOUSE/CyberSecurity_Deployment/Regulator.xlsx", sheet_name='keywords')
    keywords = df['content_keywords'].tolist()
    match_keyword = [i for i in keywords if (i.lower().replace(' ','') in text_string)]
    len_match_keyword = len(list(set(match_keyword)))
    return len_match_keyword



headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' } 
def create_text_for_each_link(text_dir,sublinks_list,folder,country_name):
    # with open(text_dir,'w') as document:
    count = 0
    sub_pdf_list = []
    # for sublink in sublinks_list[:100]:
    for sublink in sublinks_list[:50]:   
        try:
            if 'pdf' in str(sublink).lower():
                x = pdf_selector(sublink,folder,country_name)
                if '.pdf' in x.lower():
                    sub_pdf_list.append(x)
            else:
                options = webdriver.ChromeOptions()
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
                driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
                driver.maximize_window()
                driver.get(sublink)
                time.sleep(2)

                lnk=driver.find_elements(By.XPATH, "//a[@href]")
                try:
                    for i in lnk:
                        sub_sub_link = str(i.get_attribute('href'))
                        if 'pdf' in sub_sub_link.lower():
                            print("pdf link in sub sub link ", sub_sub_link)
                            y = pdf_selector(sub_sub_link,folder,country_name)
                            if '.pdf' in y.lower():
                                sub_pdf_list.append(y)
                except:
                    pass

                driver.quit()
            print(f"------------complete {count} sub link")
            count += 1 

        except Exception as e:
            print(e)
            logging.exception("Exception occurred")
            pass

    return sub_pdf_list



