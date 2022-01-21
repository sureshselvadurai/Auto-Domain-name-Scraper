import requests
import whois
import tldextract
from bs4 import BeautifulSoup
import urllib.request as urllib2
import re
import pandas as pd
from urllib.parse import urlencode, urlparse, parse_qs
from lxml.html import fromstring
from requests import get
from lxml.html import parse
import cssselect
import requests
import array
import time
import datetime
import os
import random
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import datetime

#initilize google sheet
googledr = gspread.service_account('cred.json')
maindoc = googledr.open_by_key(" ")
main = get_as_dataframe(maindoc.get_worksheet(0))[['host','Domain']].dropna()
maindoc.get_worksheet(1).clear()
maindoc.get_worksheet(2).clear()
l = main.shape
cargo = pd.DataFrame(columns = main.columns)
main['Leads'] = ''
main['contact'] = ''
main['time']=''
main['count']=''
main['failed'] = 0
main['domain'] = main['Domain']
st = 0
processlength = l[0]
#initialize chrome
chromedriver_path = r'/home/sureshrajaselvadurai/chromedriver'
driver = webdriver.Chrome(chromedriver_path)

driver.get("https://duckduckgo.com/?q=test&t=hk&ia=web")
driver.maximize_window()
login_form = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div/ul[3]/li/div/a")
login_form.click()
try:     
    login_form = driver.find_element_by_xpath("/html/body/div[6]/div[2]/div/div/div[2]/div[2]/div/label")
    login_form.click()
except Exception as e:
    login_form = driver.find_element_by_xpath("/html/body/div[7]/div[2]/div/div/div[2]/div[2]/div/label")
    print(e)
    login_form.click()

for i in range(st,l[0]):
    
    temp = ""
    cont = ''
    tempcont = ''

    #Get URLS
    try:
        query = 'www.' +  str(main['host'][i]) 
        url = "https://duckduckgo.com/?q="+query+"&t=hk&ia=web"
        driver.get(url)    
        
        if "Oops, there was an error" not in str(driver.page_source):
            elems = driver.find_elements_by_xpath("//a[@href]")
        else:
            time.sleep(2)
            elems = driver.find_elements_by_xpath("//a[@href]")
                    
        ss= ''        
        for elem in elems:
            link = str(elem.get_attribute("href"))
            data = urlparse(link)
            ss = ss+str(data.netloc)+','
            
    except Exception as e:
        time.sleep(5)
        main['failed'][i] = 1
        
    try:        
        ss = ss.split(",")
        ss = list(dict.fromkeys(ss))
        ss = list(filter(None,ss))
        ss = ','.join(ss)
        ss = ss.split(",")
        
        for qq in ss : 
            tempj = str(qq)
            l = tldextract.extract(tempj)
            lp = tldextract.extract(tempj)
            l = '.'.join(l[1:3])
            l = str(l)     
            
            #LOOP EACH RESULT
            if ((str(main['host'][i]).replace("-", "")  in str('.'.join(lp[1:3])).replace("-", "")) and str(main['Domain'][i]) != str('.'.join(lp[1:3]))):
                temp = temp + l + ","               
                url = "https://duckduckgo.com/?q=%40"+l+" email&t=hk&ia=web"                
                raw = driver.get(url)
                
                if "Oops, there was an error" not in str(driver.page_source):
                    raw = str(driver.page_source)
                else:
                    time.sleep(2)
                    raw = str(driver.page_source)
                           
                maturl =  '[\w\.-]+@'+l+'+'
                match = re.findall(maturl, raw)
                match = ','.join(match)
                cont = cont + str(match) + ","
                tempcont = ''
                tempcont = tempcont  + str(match) + ","          
                cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : l ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)
    
                whoiscont = whois.whois(str(l))
        
                if (whoiscont.emails is not None)&(str(main['Domain'][i]) !=str('.'.join(lp[1:3])) ) :
                
                    if( type(whoiscont.emails) is str):
                        cont = cont + str(whoiscont.emails)+","
                        tempcont = tempcont   + str(whoiscont.emails)+","
                        cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : l ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)
                    else : 
                        tp =','.join(whoiscont.emails)
                        cont = cont + str(tp)+","
                        tempcont = tempcont   + str(tp)+","
                        cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : l ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)

    except Exception as e:
        time.sleep(10)
        main['failed'][i] = 1

    tempcont = ''    
    try:
        whoiscont = whois.whois(str(main['host'][i])+'.net')
        if (whoiscont.emails is not None) :
            if(type(whoiscont.emails) is str):
                cont = cont + str(whoiscont.emails)+","
                tempcont = tempcont   + str(whoiscont.emails)+","
                cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : str(main['host'][i])+'.net' ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)

            else : 
                tp =','.join(whoiscont.emails)
                cont = cont + str(tp)+","
                tempcont = tempcont   + str(tp)+","                
                cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : str(main['host'][i])+'.net' ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)

    except Exception as e:
            print('No .Net')
        
    tempcont = ''    
    try:
        whoiscont = whois.whois(str(main['host'][i])+'.org')
        if (whoiscont.emails is not None) :
            if(type(whoiscont.emails) is str):
                cont = cont + str(whoiscont.emails)+","
                tempcont = tempcont   + str(whoiscont.emails)+","
                cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : str(main['host'][i])+'.org' ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)
                
            else : 
                tp =','.join(whoiscont.emails)
                cont = cont + str(tp)+","
                tempcont = tempcont   + str(tp)+","                
                cargo = cargo.append({'host' : main['host'][i], 'Domain' : main['Domain'][i] , 'Leads' : str(main['host'][i])+'.org' ,'contact' : str(tempcont),'domain' : main['domain'][i]},  ignore_index = True)            

    except Exception as e:
        print('No .org')   
        
    temp = temp.split(",")
    temp = list(dict.fromkeys(temp))
    temp = list(filter(None,temp))
    temp = ','.join(temp)
    main['Leads'][i] = temp 
    
    cont = cont.split(",")
    cont = list(dict.fromkeys(cont))
    cont = list(filter(None,cont))
    cont = ','.join(cont)
    
    main['contact'][i] = cont 
    main['count'][i] = str(i)+'/'+str(processlength)
    main['time'][i] = str(datetime.datetime.now())
    
    maindoc.get_worksheet(1).update([main.columns.values.tolist()] + main.values.tolist())
    maindoc.get_worksheet(2).update([cargo.columns.values.tolist()] + cargo.values.tolist())
    

