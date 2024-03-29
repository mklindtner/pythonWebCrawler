import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #disable warning for bad certificates
import conf

urls_response = {}
#consider putting credentials in a .conf file
email_login = 'christian@guzzy.dk'
email_password = 'hackerhome'

def checkRequestUrl(url):    
    if("https" in url):
        try:
            #don't do this for production. Instead make a white list of accepted https
            # the reason why we don't verify is because some of them gives a bad handshake i.e. bad certificate, lazy bums!
            request = requests.get(url, verify=False)
            if(request.status_code >= 200 and request.status_code <= 400):
                urls_response[url] = request.status_code
            else: 
                urls_response[url] = 404
        except:
            urls_response[url] = 404
    return urls_response


def getHttpsFromWebsite(url):
    #startup browser and login
    browser = webdriver.Firefox(executable_path  = conf.firefox_geckodriver) #remember to change me to your own path
    browser.get(url) 
    email = browser.find_element_by_id('email')
    password = browser.find_element_by_id('password')
    email.send_keys(conf.email_login)
    password.send_keys(conf.email_password)

    submit_button = browser.find_element(By.XPATH, '//button[@type="submit"]')
    submit_button.click()

    try:
        while(True):
            #find tables 
            table = browser.find_element(By.TAG_NAME, "tbody")
            table_rows = table.find_elements(By.TAG_NAME, "tr")
            for tr in table_rows:
                specific_col = tr.find_elements(By.TAG_NAME, "td")[3]
                checkRequestUrl(specific_col.get_attribute("innerHTML"))        

            #get next page link
            pages = browser.find_element_by_class_name("pagination")
            link = pages.find_elements(By.TAG_NAME, "li")[-1]            
            strLink = link.get_attribute("innerHTML")            
            links = re.findall("(\"https.*?\")",strLink)
            if(not links): 
                break #break if at last page, empty links list = no next page
            link = links[0][1:-1] #get first element and remove first " and last ""

            displayWrongLinks()
            print("----")
            browser.get(link) #next page
        
        displayWrongLinks()        
        print("---finished searching---")

    finally:
        browser.quit()
    

def displayWrongLinks():
    for key, value in urls_response.items():
        if(value == 404):
            print(key)


getHttpsFromWebsite("https://www.plusserviceonline.com/marketing/endpage-offers?page=1")