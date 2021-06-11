# -*- coding: utf-8 -*-
########################################################
#                   Jordy Naiya                        #
#               jordynabina@gmail.com                  #
########################################################


"""
This is a sample task for automation software Phonebot.co on Browser Firefox & Chrome
https://github.com/phonebotco/phonebot

"""

import logging
import sqlite3
import threading
import mymodulesteam

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime
import pathlib
import platform
import psutil
import random
import time
import unidecode
if platform.system() == 'Windows':
    import winsound



# ==================== LOG FILE ==================================================
open(mymodulesteam.LoadFile('log.log'), 'w').close()
logger = logging.getLogger('__Linkedin_Search_By_Keywords_And_City__')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler(mymodulesteam.LoadFile('log.log'))
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# ================================================================================



# ==============================================================================================================
# ============================   RANDOM TIME.SLEEP FOR BEING A STEALTH BOT  ====================================
# ==============================================================================================================
def Sleeping_Bot(borne_inf=float, borne_sup=float):
    ts = random.uniform(borne_inf, borne_sup)
    ts = round(ts, 2)
    sleep(ts)



# ==============================================================================================================
# ============================    SIMPLIFYING THE PROFILE4S URL FOR MOR STEALTH   ==============================
# ==============================================================================================================
def Simplifying_Urls(scapped_url=str):
    carac = ''
    for i in range(0, len(scapped_url)):
        carac = scapped_url[i]
        if (carac == '?'):
            limit_count = i

    limit = len(scapped_url) - limit_count
    simplified_url = scapped_url[:len(scapped_url) - limit]

    return (simplified_url)




# ==============================================================================================================
# ===================   FUNCTION THTA TEST IF A DATA IS ALMOST IN DATABASE    ==================================
# ==============================================================================================================
def Presence_Of_Data(p_platform, p_city, p_username, p_url_linkedin):
    try:
        connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
        cursor = connection.cursor()
        data_Parameter = (p_platform, p_city, p_username, p_url_linkedin)
        cursor.execute("SELECT * FROM contacts WHERE platform = ? AND city = ? AND username = ? AND url_linkedin = ?",
                       data_Parameter)
        logger.info("-----Request SENT-----")

        if len(cursor.fetchall()) == 0:
            logger.info("-----Element doesn't exist-----")
            connection.close()
            return False
        else:
            logger.info("-----Element almost exist-----")
            connection.close()
            return True
    except Exception as ex:
        logger.error(f"Error when trying to get the id in the dataBase {ex}")
        # Go to the last save.
        connection.rollback()
    finally:
        connection.close()




# ==============================================================================================================
# ================================    EXTRACT SPREADSHEET ID    ================================================
# ==============================================================================================================
def extract_ss_id(spread_sheet_url):
    spread_sheet_url = spread_sheet_url.replace('https://docs.google.com/spreadsheets/d/', '')
    ind = spread_sheet_url.index('/')
    spread_sheet_url = spread_sheet_url[:ind]
    return spread_sheet_url




# ==============================================================================================================
# ============================   RETURN A KEY AND LIST OF CITITES   ============================================
# ==============================================================================================================
def get_keyword_city(key_city, min):
    # list to return
    key_city_list = []
    # get spreadsheet id
    ss_id = extract_ss_id(key_city)
    # get spreadsheet data
    values = mymodulesteam.GoogleSheetGetValues(ss_id)
    ind = []
    length = len(values)
    ind += random.sample(range(length), min)
    # print(ind)
    for i in ind:
        key_city_list.append(values[i])
    return key_city_list




# ==============================================================================================================
# ============================ FUNCTION TO SCRAP GOOGLE RESULTS ================================================
# ==============================================================================================================
def ScrapGoogleResults(p_driver, p_mylinkedinprofile, p_counter_page_result, p_cursor1, p_sqliteConnection, p_firstname,
                       string_keywords_google_search):
    # We will scrap only 3 pages. this is the safest way to scrap google. Let's be a NINJA, not a RAMBO!
    # EN Français : on fait pas les bourins à scraper 20 pages google d'un coup. On y va molo.
    # Il va donc falloir sur quelle page de résultat (la N°3,4,???) surlaquelle on s'est arrêté pour pouvoir
    # revenir dessus lors d'une prochaine fois

    logger.info(
        "================================== START ScrapGoogleResults =========================================")
    counter_page_result = p_counter_page_result
    sql_google_search = "SELECT * FROM google_search where id_profile='" + p_mylinkedinprofile + "'"
    print(
        f"counter_page_result START = {counter_page_result}*********************************")
    while counter_page_result <= 3:
        try:
            print("# extract all the urls of the results of the page")
            links = p_driver.find_elements_by_xpath("*//div[@id='search']//a")

            print(f"len(links) : {len(links)}")
            print(f"links) : {links}")
            if len(links) == 0:
                logger.info(f"DESKTOP|||No result. We can stop!")
                print(
                    f"counter_page_result BEFORE RETURN = {counter_page_result}*********************************")
                return counter_page_result

            print(f"links) : {links}")
            print(f"len(links) : {len(links)}")

            print("# get the url of the page")

            counter_page_result += 1
            for link in links:
                url = str(link.get_attribute('href'))

                position = url.find('linkedin.com/in', 0, 28)
                if position != -1:

                    print("# Save the link in table 'linkedin_profiles'")
                    if p_cursor1.execute("SELECT * FROM linkedin_profiles WHERE url=?", (url,)).fetchone():
                        logger.info(
                            f"DESKTOP|||This Linkedin profile is already in table 'linkedin_profiles'")
                    else:
                        rightnow = datetime.now()
                        date_n_time = str(rightnow.strftime("%d/%m/%Y %H:%M:%S"))
                        p_cursor1.execute(
                            "INSERT INTO linkedin_profiles (url,date,id_social_account,source) VALUES (?,?,?,?)",
                            (url, date_n_time, p_mylinkedinprofile, string_keywords_google_search))
                        p_sqliteConnection.commit()
                        print(
                            f"counter_page_result BEFORE +1 = {counter_page_result}*********************************")

                        print(
                            f"counter_page_result AFTER +1 = {counter_page_result}*********************************")

            print("# ======================================= NEXT PAGE =============================================")
            next_page = p_driver.find_elements_by_id("pnnext")

            if len(next_page) == 0:
                print("# ============================== NO NEXT PAGE, MAYBE OMITED RESULTS ? ========================")
                logger.info(
                    f"DESKTOP|||There is not NEXT button anymore. Maybe it is the opportunity to get more results....")
                link_search_with_more_results = p_driver.find_elements_by_xpath(
                    "//a[contains(text(),'relancer la recherche pour inclure les résultats omis')]")

                if len(link_search_with_more_results) == 0:
                    print("# ======================== NO FRENCH OMITED RESULTS, MAYBE ENGLISH ONE ? ==================")
                    logger.info(
                        f"DESKTOP|||We couldn't find the FRENCH link 'relancer la recherche pour inclure les résultats omis'. Let's try to find it in ENGLISH!")
                    link_search_with_more_results = p_driver.find_elements_by_xpath(
                        "//a[contains(text(),'repeat the search with the omitted results included')]")
                    if len(link_search_with_more_results) == 0:
                        print("# ===================== NO ENGLISH OMITED RESULTS, MAYBE RECAPTCHA ? ==================")
                        logger.info(
                            f"DESKTOP|||We couldn't find the ENGLISH link 'repeat the search with the omitted results included'. We have to give up! :-(")
                        logger.critical(f"DESKTOP|||Maybe the Google Recaptcha")
                        recaptcha = p_driver.find_elements(By.CSS_SELECTOR,
                                                           "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")
                        if len(recaptcha) == 0:
                            print("# ==================== NO RECAPTCHA. IT IS END OF RESULTS!!!! ==================")

                            logger.info(
                                f"DESKTOP|||There was no RECAPTCHA! We are certainly at the end of results! Let's stop everything.")
                            # We will save this url of english omitted result in the table 'google_search'

                            if p_cursor1.execute(sql_google_search).fetchone():
                                p_cursor1.execute(
                                    "UPDATE google_search set omited_result_url=?, next_page_url=? WHERE id_profile=?",
                                    ('', '', p_mylinkedinprofile))
                                p_sqliteConnection.commit()
                            else:
                                p_cursor1.execute(
                                    "INSERT INTO google_search (omited_result_url,next_page_url, id_profile) VALUES (?,?,?)",
                                    ('', '', p_mylinkedinprofile))
                                p_sqliteConnection.commit()

                            # We need to update table firstnames in order not to select again the same firstname
                            p_cursor1.execute("UPDATE firstnames set linkedin_done=? where firstname=?",
                                              (1, p_firstname))
                            p_sqliteConnection.commit()
                            logger.info(f"DESKTOP|||*************************************************")
                            logger.info(f"DESKTOP|||We finish the Google scraping for Linkedin task!")
                            logger.info(f"DESKTOP|||*************************************************")
                            print(
                                f"counter_page_result BEFORE RETURN = {counter_page_result}*********************************")
                            return counter_page_result
                        else:
                            while True:
                                winsound.PlaySound('alert_captcha.wav', winsound.SND_FILENAME)
                                logger.info(f"DESKTOP|||We have a RECAPTCHA case! :-)")
                                WebDriverWait(p_driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
                                    (By.CSS_SELECTOR,
                                     "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
                                WebDriverWait(p_driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
                                p_driver.implicitly_wait(15)
                                logger.info(
                                    f"DESKTOP|||The bot will sleep just a few seconds..............................")
                                time.sleep(random.uniform(8.9, 13.3))
                                links = p_driver.find_elements_by_xpath("*//div[@id='search']//a")
                                if len(links) == 0:
                                    logger.info(f"DESKTOP|||No result. Let's paly Alert sound again!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!                              !!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!! GOOGLE RECAPTCHA WITH IMAGES !!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!                              !!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                else:
                                    break
                    else:
                        print("# ============================== THERE ARE ENGLISH OMITED RESULTS  ====================")
                        logger.info(
                            f"DESKTOP|||We FOUND the ENGLISH link 'repeat the search with the omitted results included'.")
                        # ======    IF counter_page_result < 3: We continue scraping
                        # ======    ELSE We save this omitted url in table google_search
                        url = str(link_search_with_more_results[0].get_attribute('href'))
                        print(
                            f"counter_page_result = {counter_page_result}*********************************")
                        if counter_page_result < 3:
                            p_driver.get(url)
                            # Let's check if the 'I agree' popup is showing uop or not
                            try:
                                p_driver.switch_to.frame(p_driver.find_element_by_xpath("//iframe"))
                                p_driver.find_element_by_xpath("*//div[@id='introAgreeButton']").click()
                                time.sleep(random.uniform(1.9, 2.3))
                                p_driver.switch_to.default_content()
                            except:
                                logger.info("There was not 'Accept agreement' popup!")
                            time.sleep(random.uniform(1.9, 2.3))
                        else:
                            print(f"p_mylinkedinprofile : {p_mylinkedinprofile} - {type(p_mylinkedinprofile)}")
                            # We will save this url of english omitted result in the table 'google_search'

                            if p_cursor1.execute(sql_google_search).fetchone():
                                p_cursor1.execute(
                                    "UPDATE google_search set omited_result_url=?, next_page_url=? WHERE id_profile=?",
                                    (url, '', str(p_mylinkedinprofile)))
                                p_sqliteConnection.commit()
                            else:
                                p_cursor1.execute(
                                    "INSERT INTO google_search (omited_result_url,next_page_url, id_profile) VALUES (?,?,?)",
                                    (url, '', str(p_mylinkedinprofile)))
                                p_sqliteConnection.commit()



                else:
                    print("# ============================== THERE ARE FRENCH OMITED RESULTS ==========================")
                    logger.info(
                        f"DESKTOP|||We FOUND the FRENCH link 'relancer la recherche pour inclure les résultats omis'.")
                    url = str(link_search_with_more_results[0].get_attribute('href'))
                    print(
                        f"counter_page_result = {counter_page_result}*********************************")
                    if counter_page_result < 3:
                        p_driver.get(url)
                        # Let's check if the 'I agree' popup is showing uop or not
                        try:
                            p_driver.switch_to.frame(p_driver.find_element_by_xpath("//iframe"))
                            p_driver.find_element_by_xpath("*//div[@id='introAgreeButton']").click()
                            time.sleep(random.uniform(1.9, 2.3))
                            p_driver.switch_to.default_content()
                        except:
                            logger.info("There was not 'Accept agreement' popup!")
                        time.sleep(random.uniform(1.9, 2.3))
                    else:
                        # We will save this url of french omitted result in the table 'google_search'
                        if p_cursor1.execute(sql_google_search).fetchone():
                            p_cursor1.execute(
                                "UPDATE google_search set omited_result_url=?, next_page_url=? WHERE id_profile=?",
                                (url, '', str(p_mylinkedinprofile)))
                            p_sqliteConnection.commit()
                        else:
                            p_cursor1.execute(
                                "INSERT INTO google_search (omited_result_url,next_page_url, id_profile) VALUES (?,?,?)",
                                (url, '', str(p_mylinkedinprofile)))
                            p_sqliteConnection.commit()


            else:
                # ============================== THERE IS NEXT PAGE =============================
                logger.info(f"DESKTOP|||We FOUND the NEXT page.")
                print(
                    f"counter_page_result = {counter_page_result}*********************************")
                if counter_page_result < 3:
                    next_page[0].click()
                else:
                    url = str(next_page[0].get_attribute('href'))
                    print(f"url : {url}-{type(url)}")
                    print("# We will save this next_page in the table 'google_search'")
                    print(f"p_mylinkedinprofile : {p_mylinkedinprofile}")
                    if p_cursor1.execute(sql_google_search).fetchone():
                        p_cursor1.execute(
                            "UPDATE google_search set omited_result_url=?, next_page_url=? WHERE id_profile=?",
                            ('', url, p_mylinkedinprofile))
                        p_sqliteConnection.commit()
                    else:
                        p_cursor1.execute(
                            "INSERT INTO google_search (omited_result_url,next_page_url, id_profile) VALUES (?,?,?)",
                            ('', url, p_mylinkedinprofile))
                        p_sqliteConnection.commit()
                    p_cursor1.execute(
                        "UPDATE google_search set omited_result_url=?, next_page_url=? WHERE id_profile=?",
                        ('', url, p_mylinkedinprofile))
                    p_sqliteConnection.commit()

            # Let's make a little pause
            p_driver.implicitly_wait(15)
            logger.info(f"DESKTOP|||The bot will sleep just a few seconds..............................")
            time.sleep(random.uniform(8.9, 13.3))
            print(
                f"counter_page_result = {counter_page_result}*********************************")
            if counter_page_result >= 3:
                return counter_page_result


        # except ValueError:
        # logger.critical(f"DESKTOP|||Something was wrong with Google scraping results!")
        except Exception as ex:
            logger.critical(f"{ex} -> DESKTOP|||Something was wrong with Google scraping results!")
            if p_driver:
                p_driver.quit()
            break
    if p_driver:
        p_driver.quit()




# ===================================================================================================================
# ============================ METHOD MAKE A GOOGLE SEARCH FOR LINKEDIN AND SCRAP RESULTS ===========================
# ===================================================================================================================
def MakeGoogleSearchforLinkedin(myprofile_username, p_browser):
    try:
        # =================================================================================
        # =========================== PLAY STOP OR PAUSE ? ================================
        # =================================================================================
        # mymodulesteam.PlayStopPause("MakeGoogleSearchforLinkedin", 'Google_Bot MakeGoogleSearchforLinkedin')
        # =================================================================================
        # =================================================================================
        # =================================================================================
        sqliteConnection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))  # we prepare db
        cursor1 = sqliteConnection.cursor()

        logger.info(
            "================================== START MakeGoogleSearchforLinkedin =========================================")

        # === We need to scrap google results only if we didn't scrap since more than 2 hours
        # === but also if the myprofile_username doesn't have any urls for linkedin tasks

        """number_hours = mymodulesteam.NumberHoursLastGoogleScrapLinkedin()
        result_linkedin_profiles=cursor1.execute("SELECT * FROM linkedin_profiles WHERE id_social_account=?",(myprofile_username,)).fetchall()

        if number_hours < 2 and len(result_linkedin_profiles)>70 :
            logger.info(f"DESKTOP|||PhoneBot scrapped Google less than 2 hours ago. Let's move this task for later")
            return False"""

        # =======================================================================================================
        # =======================================================================================================
        # We need to check first if we already made a Google query previously and then carry on the scrapping
        # of this Google query before to make a new Google query.
        # There are 2 scenarios: Or we stop at a 'next page', or we stop at a 'Ommited result' page
        # =======================================================================================================
        # =======================================================================================================

        firstname = ''
        sql_google_search = "SELECT * FROM google_search where id_profile='" + myprofile_username + "'"
        google_search = cursor1.execute(sql_google_search).fetchone()
        if google_search:
            logger.info(f"PhoneBot found a previous Google search for user {myprofile_username}. It will carry on.")
            print(f"google_search :{google_search}")
            next_page = google_search[2]
            omited_result = google_search[1]
            mylinkedinprofile = google_search[3]
            new_search = False
        else:
            logger.info(
                f"PhoneBot didn't find a previous Google search for user {myprofile_username}. It will start a new one.")
            mylinkedinprofile = myprofile_username
            new_search = True

        counter_number_pages_scrapped = 0
        print(
            f"counter_number_pages_scrapped START = {counter_number_pages_scrapped}*********************************")

        # Open the browser
        if p_browser == "Chrome":
            driver = mymodulesteam.ChromeDriverWithProfile()
        elif p_browser == "Firefox":
            driver = mymodulesteam.FireFoxDriverWithProfile()
        else:
            logger.error(f"PhoneBot didn't find the browser called '{p_browser}'.")

        driver.maximize_window()

        if not new_search:
            if not next_page or next_page == '':
                print("There is not next_page")
                if not omited_result or omited_result == '':
                    print("There is not omited_result")
                    print(
                        "# ==============================   WE HAVE TO MAKE A NEW SEARCH  ================================")
                    print(
                        "# ============================ CHECK THE OPTIONS IN PHONEBOT 'Account Details' =========================")

                    # list_of_keywords_locations = mymodulesteam.GetValueFromCustomField('GOOGLE DESKTOP', 'linkedin', mylinkedinprofile,'list_of_keywords_locations')
                    result = mymodulesteam.GetDetailsTaskUser(276)
                    list_of_keywords_locations = get_keyword_city(result['url_keywords'], 1)

                    if not list_of_keywords_locations:
                        logger.info(
                            f"We couldn't find keywords in your settings on our website PhoneBot.co. Please go to your 'Account details' and fill the textarea of keywords for the account '{mylinkedinprofile}'.")
                    else:
                        print(f"list_of_keywords_locations : {list_of_keywords_locations}")
                        # --- We need to transform the string in a list of keywords

                        # list_of_keywords_locations_list = str(list_of_keywords_locations).split("\\n")
                        list_of_keywords_locations_list = list_of_keywords_locations[0]
                        print(f"list_of_keywords_locations_list : {list_of_keywords_locations_list}")
                        choice_linkedin_keywords = random.randint(0, len(list_of_keywords_locations_list) - 1)
                        # keywords_place_language = str(list_of_keywords_locations_list[choice_linkedin_keywords]).split(";")

                        keywords_place_language = list_of_keywords_locations_list
                        print(f"keywords_place_language len : {len(keywords_place_language)}")
                        if len(
                                keywords_place_language) != 3:  # We check that user fill correctly the list of keywords, place and language in Account details
                            logger.info(
                                f"There is an issue with the 'keyword,place,language' you fill in 'Account details' on https://phonebot.co for the Linkedin account {mylinkedinprofile}. Please correct it.")
                        else:
                            keyword = str(keywords_place_language[0])
                            keyword = unidecode.unidecode(keyword)  # We need to remove special characters
                            place = keywords_place_language[1]
                            language = str(keywords_place_language[2]).lower()
                            print(f"keyword : {keyword}")
                            print(f"place : {place}")
                            print(f"language : {language}")

                            print("# We need to pick up a first name based on language from the table 'firstnames'")
                            prepare_language_string_sql = "'%" + language + "%'"
                            print(f"prepare_language_string_sql : {prepare_language_string_sql}")
                            sql = "SELECT firstname FROM firstnames WHERE language LIKE " + prepare_language_string_sql + " AND linkedin_done IS NULL"
                            # firstnames_tuple=p_cursor1.execute("SELECT firstname FROM firstnames WHERE language LIKE ?",(prepare_language_string_sql,)).fetchall()
                            firstnames_tuple = cursor1.execute(sql).fetchall()

                            print(f"firstnames_tuple : {firstnames_tuple}")
                            firstnames_list = [item[0] for item in firstnames_tuple]
                            print(f"first_names_list : {firstnames_list}")
                            index_firstname = random.randint(0, len(firstnames_list) - 1)
                            firstname = firstnames_list[index_firstname]
                            print(f"firstname : {firstname}")

                            while True:

                                # =================================================================================
                                # =========================== PLAY STOP OR PAUSE ? ================================
                                # =================================================================================
                                # mymodulesteam.PlayStopPause("MakeGoogleSearchforLinkedin", 'Google_Bot Make Google request')
                                # =================================================================================
                                # =================================================================================
                                # =================================================================================
                                try:

                                    print("DESKTOP||| We prepare the Google request string")
                                    google_request = firstname + ' ' + keyword + ' ' + place + ' ' + "inurl:linkedin.com/in"
                                    print(f"google_request : {google_request}")
                                    string_keywords_google_search = keyword + ' ' + place
                                    logger.info("DESKTOP||| We say NO PROXY and we open Google")

                                    driver.get("https://www.google.com")
                                    driver.implicitly_wait(5)

                                    logger.info(
                                        f"DESKTOP|||The bot will sleep just a few seconds..............................")
                                    time.sleep(random.uniform(5.9, 9.3))

                                    # Let's check if the 'I agree' popup is showing uop or not
                                    try:
                                        driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
                                        driver.find_element_by_xpath("*//div[@id='introAgreeButton']").click()
                                        time.sleep(random.uniform(1.9, 2.3))
                                        driver.switch_to.default_content()
                                    except:
                                        logger.info("There was not 'Accept agreement' popup!")
                                    time.sleep(random.uniform(1.9, 2.3))

                                    """search_field = driver.find_element_by_name("q")
                                    search_field.clear()
                                    for c in google_request:
                                        search_field.send_keys(c)
                                        time.sleep(random.uniform(0.05, 0.3))
                                    search_field.send_keys(Keys.RETURN)"""

                                    search_field = "https://www.google.com/search?q=" + google_request
                                    driver.get(search_field)

                                    # Let's make a little pause
                                    driver.implicitly_wait(5)
                                    logger.info(
                                        f"DESKTOP|||The bot will sleep just a few seconds..............................")
                                    time.sleep(random.uniform(2.9, 6.3))
                                    print(
                                        f"counter_number_pages_scrapped BEFORE = {counter_number_pages_scrapped}*********************************")
                                    counter_number_pages_scrapped = ScrapGoogleResults(driver, mylinkedinprofile,
                                                                                       counter_number_pages_scrapped,
                                                                                       cursor1, sqliteConnection,
                                                                                       firstname,
                                                                                       string_keywords_google_search)
                                    print(
                                        f"counter_number_pages_scrapped AFTER = {counter_number_pages_scrapped}*********************************")

                                    break
                                # except ValueError:
                                # logger.critical(
                                # f"DESKTOP|||Something was wrong with Google scraping results!Let's try again!")
                                except Exception as ex:
                                    logger.critical(
                                        f"{ex} -> DESKTOP|||Something was wrong with Google scraping results!Let's try again!")
                                    break
                else:
                    print("There is omited_result")
                    print(
                        f"counter_number_pages_scrapped BEFORE = {counter_number_pages_scrapped}*********************************")

                    driver.get(omited_result)

                    driver.implicitly_wait(10)
                    logger.info(f"DESKTOP|||The bot will sleep just a few seconds..............................")
                    time.sleep(random.uniform(1.9, 3.3))
                    # Let's check if the 'I agree' popup is showing uop or not
                    try:
                        driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
                        driver.find_element_by_xpath("*//div[@id='introAgreeButton']").click()
                        time.sleep(random.uniform(1.9, 2.3))
                        driver.switch_to.default_content()
                    except:
                        logger.info("There was not 'Accept agreement' popup!")
                    time.sleep(random.uniform(1.9, 2.3))

                    counter_number_pages_scrapped = ScrapGoogleResults(driver, mylinkedinprofile,
                                                                       counter_number_pages_scrapped,
                                                                       cursor1, sqliteConnection, firstname, '')
                    print(
                        f"counter_number_pages_scrapped AFTER = {counter_number_pages_scrapped}*********************************")

            else:
                print("There is next_page")
                print("# We open Google search url next_page")

                driver.get(next_page)

                driver.implicitly_wait(5)
                logger.info(f"DESKTOP|||The bot will sleep just a few seconds..............................")
                time.sleep(random.uniform(5.9, 9.3))

                print(
                    f"counter_number_pages_scrapped BEFORE = {counter_number_pages_scrapped}*********************************")
                counter_number_pages_scrapped = ScrapGoogleResults(driver, mylinkedinprofile,
                                                                   counter_number_pages_scrapped,
                                                                   cursor1, sqliteConnection, firstname, '')
                print(
                    f"counter_number_pages_scrapped AFTER = {counter_number_pages_scrapped}*********************************")

        else:
            print("# ==============================   WE HAVE TO MAKE A NEW SEARCH  ================================")
            print(
                "# ============================ CHECK THE OPTIONS IN PHONEBOT 'Account Details' =========================")

            # list_of_keywords_locations = mymodulesteam.GetValueFromCustomField('GOOGLE DESKTOP', 'linkedin', mylinkedinprofile,'list_of_keywords_locations')
            result = mymodulesteam.GetDetailsTaskUser(276)
            list_of_keywords_locations = get_keyword_city(result['url_keywords'], 1)

            if not list_of_keywords_locations:
                logger.info(
                    f"We couldn't find keywords in your settings on our website PhoneBot.co. Please go to your 'Account details' and fill the textarea of keywords for the account '{mylinkedinprofile}'.")
            else:
                print(f"list_of_keywords_locations : {list_of_keywords_locations}")
                # --- We need to transform the string in a list of keywords
                list_of_keywords_locations_list = list_of_keywords_locations[0]
                print(f"list_of_keywords_locations_list : {list_of_keywords_locations_list}")
                choice_linkedin_keywords = random.randint(0, len(list_of_keywords_locations_list) - 1)

                keywords_place_language = list_of_keywords_locations_list
                if len(
                        keywords_place_language) != 3:  # We check that user fill correctly the list of keywords, place and language in Account details
                    logger.info(
                        f"There is an issue with the 'keyword;place;language' you fill in 'Account details' on https://phonebot.co for the Linkedin account {mylinkedinprofile}. Please correct it.")
                else:
                    keyword = str(keywords_place_language[0])
                    keyword = unidecode.unidecode(keyword)  # We need to remove special characters
                    place = keywords_place_language[1]
                    language = str(keywords_place_language[2]).lower()
                    print(f"keyword : {keyword}")
                    print(f"place : {place}")
                    print(f"language : {language}")
                    string_keywords_google_search = keyword + ' ' + place + ' ' + language
                    print("# We need to pick up a first name based on language from the table 'firstnames'")
                    prepare_language_string_sql = "'%" + language + "%'"
                    print(f"prepare_language_string_sql : {prepare_language_string_sql}")
                    sql = "SELECT firstname FROM firstnames WHERE language LIKE " + prepare_language_string_sql + " AND linkedin_done IS NULL"
                    # firstnames_tuple=p_cursor1.execute("SELECT firstname FROM firstnames WHERE language LIKE ?",(prepare_language_string_sql,)).fetchall()
                    firstnames_tuple = cursor1.execute(sql).fetchall()

                    print(f"firstnames_tuple : {firstnames_tuple}")
                    firstnames_list = [item[0] for item in firstnames_tuple]
                    print(f"first_names_list : {firstnames_list}")
                    index_firstname = random.randint(0, len(firstnames_list) - 1)
                    firstname = firstnames_list[index_firstname]
                    print(f"firstname : {firstname}")

                    while True:

                        # =================================================================================
                        # =========================== PLAY STOP OR PAUSE ? ================================
                        # =================================================================================
                        # mymodulesteam.PlayStopPause("MakeGoogleSearchforLinkedin", 'Google_Bot Make Google request')
                        # =================================================================================
                        # =================================================================================
                        # =================================================================================
                        try:

                            print("# We prepare the Google request string")
                            google_request = firstname + ' ' + keyword + ' ' + place + ' ' + "inurl:linkedin.com/in"

                            print("# We open Google")

                            driver.get("https://www.google.com")
                            driver.implicitly_wait(5)

                            logger.info(
                                f"DESKTOP|||The bot will sleep just a few seconds..............................")
                            time.sleep(random.uniform(5.9, 9.3))

                            # Let's check if the 'I agree' popup is showing uop or not
                            try:
                                driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
                                driver.find_element_by_xpath("*//div[@id='introAgreeButton']").click()
                                time.sleep(random.uniform(1.9, 2.3))
                                driver.switch_to.default_content()
                            except:
                                logger.info("There was not 'Accept agreement' popup!")
                            time.sleep(random.uniform(1.9, 2.3))


                            """search_field = driver.find_element_by_name("q")
                            search_field.clear()
                            for c in google_request:
                                search_field.send_keys(c)
                                time.sleep(random.uniform(0.05, 0.3))
                            search_field.send_keys(Keys.RETURN)"""

                            search_field = "https://www.google.com/search?q=" + google_request
                            driver.get(search_field)

                            # Let's make a little pause
                            driver.implicitly_wait(5)
                            logger.info(
                                f"DESKTOP|||The bot will sleep just a few seconds..............................")
                            time.sleep(random.uniform(2.9, 6.3))
                            print(
                                f"counter_number_pages_scrapped BEFORE = {counter_number_pages_scrapped}*********************************")
                            counter_number_pages_scrapped = ScrapGoogleResults(driver, mylinkedinprofile,
                                                                               counter_number_pages_scrapped,
                                                                               cursor1, sqliteConnection, firstname,
                                                                               string_keywords_google_search)
                            print(
                                f"counter_number_pages_scrapped AFTER = {counter_number_pages_scrapped}*********************************")

                            break
                        # except ValueError:
                        # logger.critical(
                        # f"DESKTOP|||Something was wrong with Google scraping results!Let's try again!")
                        except Exception as ex:
                            logger.critical(
                                f"{ex} -> DESKTOP|||Something was wrong with Google scraping results!Let's try again!")
                            break

        try:
            if driver:
                driver.quit()
        except:
            logger.error("Phonebot could'nt close the driver.")
        try:
            if cursor1:
                cursor1.close()
        except:
            logger.error("Phonebot could'nt close cursor1.")

        try:
            if sqliteConnection:
                sqliteConnection.close()
        except:
            logger.error("Phonebot could'nt close sqliteConnection.")
        return True
    # except ValueError:
    # logger.critical(f"DESKTOP|||Error with Google_bot!")
    except Exception as ex:
        logger.critical(f"{ex} -> DESKTOP|||Error with Google_bot!")




# ===================================================================================================================
# ============================ FUNCTION TO SCRAP ONE LINKEDIN PROFIL ================================================
# ===================================================================================================================
def Scrap_One_User(profil_Url, driver, city, p_id_social_account,p_taskuser_id):
    driver.get(profil_Url)
    Sleeping_Bot(2.5, 3.5)


    username = ""
    first_name = ""
    last_name = ""
    city = city
    city2 = city
    country = "France"
    email = ""
    phone = ""
    website = ""
    url_linkedin = ""
    about_user = ""
    job = ""
    twitter = ""


    try:

        #Scrap data from the main profil window

        #JOB SCRAPPING
        try:
            job_present = False
            job = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, (
                    "//section[contains(@class,'pv-top-card')]//div[contains(@class,'mr5')]//div[contains(@class,'break-words')]"))))
            Sleeping_Bot(2.5, 3.5)
            newJob = job.text
            job_present = True
            #print("Job = " + newJob)

        except Exception as ex:
            if (job_present):
                if (len(newJob) == 0):
                    newProfileUrl = "NO JOB"
                    #print("Job = " + newJob)

            else:
                newJob = "NO JOB"
                #print("Job = " + newJob)
            logger.warning(f"Warning exception when trying to get job (element not find or empty); {ex}")

        # LOCALISATION SCRAPPING
        try:
            loca_present = False
            city = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, (
                    "//div[@class='pb2']//span[contains(@class,'break-words')]"))))
            Sleeping_Bot(2.5, 3.5)
            newLoca = city.text
            job_present = True
            # print("Localisation = " + newLoca)

        except Exception as ex:
            if (loca_present):
                if (len(newJob) == 0):
                    newLoca = city2
                    # print("Localisation = " + newLoca)

            else:
                newLoca = city2
                # print("Localisation = " + newLoca)
            logger.warning(f"Warning exception when trying to get Localisation (element not find or empty); {ex}")


        #ABOUT USER SCRAPPING
        try:
            aboutUser_present = False
            about_user = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, (
                    "//section[contains(@class,'pv-about-section')]//div[contains(@class,'inline-show-more-text')]"))))
            Sleeping_Bot(2.5, 3.5)
            newAbout = about_user.text
            aboutUser_present = True
            #print("Bio = " + newAbout)

        except Exception as ex:
            if (aboutUser_present):
                if (len(newAbout) == 0):
                    newProfileUrl = "NO ABOUT"
                    #print("Bio = " + newAbout)

            else:
                newAbout = "NO ABOUT"
                #print("Bio = " + newAbout)
            logger.warning(f"Warning exception when trying to get user_bio (element not find or empty); {ex}")


        #Scrap data from User Contact info
        try:

            contact_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, (
                "//div[@class='pb2']//a[contains(@class,'ember-view') and contains(@href,'/contact-info')]"))))
            sleep(10)
            driver.execute_script("arguments[0].click();", contact_info)
            logger.info(f"contact info button find and clicked")

            #USERNAME SCRAPPING
            try:
                username_present = False
                username = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ("//h1[@id='pv-contact-info']"))))
                Sleeping_Bot(2.5, 3.5)

                newUsername = username.text
                username_present = True
                #print("Username = " + newUsername)

                #Split the username into first and last name
                if(username_present):
                    name_split = newUsername.split(maxsplit=1)
                    first_name = name_split[0]
                    last_name = name_split[1]

                    #print("Fisrt Name = {}\nLast Name = {}".format(first_name, last_name))

            except Exception as ex:
                if (username_present):
                    if (len(newUsername) == 0):
                        newUsername = "NO USERNAME"
                        first_name = ""
                        last_name = ""
                        #print("Username = " + newUsername)

                else:
                    newUsername = "NO USERNAME"
                    first_name = ""
                    last_name = ""
                    #print("Username = " + newUsername)
                logger.warning(f"Warning exception when trying to get username (element not find or empty); {ex}")


            #PROFIL URL SCRAPING
            try:
                profUrl_present = False
                url_linkedin = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, (
                        "//div[@class='ember-view']//section[contains(@class,'ci-vanity-url')]//a[contains(@href,'.com/in')]"))))
                Sleeping_Bot(2.5, 3.5)
                newProfileUrl = url_linkedin.text
                profUrl_present = True
                #print("Profil url = " + newProfileUrl)

            except Exception as ex:
                if (profUrl_present):
                    if (len(newProfileUrl) == 0):
                        newProfileUrl = "NO PROFIL URL"
                        #print("Profil url = " + newProfileUrl)

                else:
                    newProfileUrl = "NO PROFIL URL"
                    #print("Profil url = " + newProfileUrl)
                logger.warning(f"Warning exception when trying to get user profil url (element not find or empty); {ex}")


            #WEBSITE SCRAPPING
            try:
                website_present = False
                website = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, (
                        "//div[@class='ember-view']//section[contains(@class,'ci-websites')]//a[contains(@class,'contact-link')]"))))
                Sleeping_Bot(2.5, 3.5)
                newWebSite = "https://" + website.text
                website_present = True
                #print("Website = " + newWebSite)

            except Exception as ex:
                if (website_present):
                    if(len(newWebSite) ==0):

                        newWebSite = "NO WEBSITE"
                        #print("Website = " +newWebSite)

                else:
                    newWebSite = "NO WEBSITE"
                    #print("Website = " + newWebSite)
                logger.warning(f"Warning exception when trying to get website (element not find or empty); {ex}")


            #PHONE NUMBER SCRAPPING
            try:
                phone_present = False
                phone = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, (
                        "//div[@class='ember-view']//section[contains(@class,'ci-phone')]//span[1]"))))
                Sleeping_Bot(2.5, 3.5)
                newPhone = phone.text
                phone_present = True
                #print("Phone number = " + newPhone)

            except Exception as ex:
                if (phone_present):
                    if (len(newPhone) == 0):
                        newPhone = "NO PHONE NUMER"
                        #print("Phone number = " + newPhone)

                else:
                    newPhone = "NO PHONE NUMBER"
                    #print("Phone number = " + newPhone)
                logger.warning(f"Warning exception when trying to get phone number (element not find or empty); {ex}")

            #EMAIL SCRAPPING
            try:
                email_present = False
                email = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, (
                        "//div[@class='ember-view']//section[contains(@class,'ci-email')]//a[contains(@href,'mailto')]"))))
                Sleeping_Bot(2.5, 3.5)
                newEmail = email.text
                email_present = True
                #print("Email = " + newEmail)

            except Exception as ex:
                if (email_present):
                    if (len(newEmail) == 0):
                        newEmail = "NO EMAIL"
                        #print("Email = " + newEmail)

                else:
                    newEmail = "NO EMAIL"
                    #print("Email = " + newEmail)
                logger.warning(f"Warning exception when trying to get email (element not find or empty); {ex}")


            # TWITTER SCRAPPING
            try:
                twitter_present = False
                twitter = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, (
                        "//div[@class='ember-view']//section[contains(@class,'ci-twitter')]//a[contains(@href,'twitter')]"))))
                Sleeping_Bot(2.5, 3.5)
                newTwitter = twitter.text
                url_twitter = "https://twitter.com/"+newTwitter
                twitter_present = True
                # print("Twitter = " + newTwitter)

            except Exception as ex:
                if (twitter_present):
                    if (len(newTwitter) == 0):
                        newTwitter = "NO TWITTER"
                        url_twitter = ""
                        # print("Twitter = " + newTwitter)

                else:
                    newTwitter = "NO TWITTER"
                    url_twitter = ""
                    # print("Twitter = " + newTwitter)
                logger.warning(f"Warning exception when trying to get twitter (element not find or empty); {ex}")


        except Exception as ex:
            Sleeping_Bot(2.5, 4.5)
            logger.error(f"Error when trying to click on Contact Info {ex}")


    except Exception as ex:
        logger.error(f"Error when trying to scrap user : {ex}")



    #DATABASE HANDLER
    p_platform = "linkedin"
    p_city = newLoca
    p_username = newUsername

    p_first_name = first_name
    p_last_name = last_name
    p_email = newEmail
    p_url_linkedin = profil_Url
    p_linkedin_bio = newAbout
    p_job = newJob

    p_twitter = newTwitter
    p_url_twitter = url_twitter
    p_website = newWebSite
    p_phone = newPhone
    date = datetime.today()
    p_type_action = "scrap"



    add_or_update = Presence_Of_Data(p_platform, p_city, p_username, p_url_linkedin)

    # Transfert or update of scrapped data
    if add_or_update == True:
        # Update the data
        try:
            connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
            cursor = connection.cursor()
            data_Parameter = (p_username, p_first_name, p_last_name, p_email, p_phone, p_website,p_twitter, p_linkedin_bio, p_url_twitter, p_job,p_taskuser_id, date, p_platform, p_city, p_url_linkedin)
            with lock:
                cursor.execute(
                    "UPDATE contacts SET username = ?, first_name = ?, last_name = ?, email = ?, phone = ?, website = ?, twitter = ?, linkedin_bio = ?, url_twitter = ?, job = ?, id_task_user = ?, date_update = ? WHERE platform = ? AND city = ? AND url_linkedin = ?",
                    data_Parameter)
                logger.info("New UPDATE in the DataBase.")
                connection.commit()
            logger.info("Commited successfully.")
        except Exception as ex:
            logger.error(f"Error when trying to UPDATE the dataBase {ex}")
            # Go to the last save.
            connection.rollback()
        finally:
            connection.close()

    else:
        # Add informations in contact
        try:
            connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
            cursor = connection.cursor()
            newLine = (
                cursor.lastrowid, p_platform, p_username, first_name, last_name, p_city, p_email, p_phone, p_website, p_url_linkedin, p_twitter, p_linkedin_bio, p_url_twitter,
                p_job,p_taskuser_id, date)

            # The '?' allows to avoid attacks by SQL's Injections
            with lock:
                cursor.execute(
                    "INSERT INTO contacts (id, platform, username, first_name, last_name, city, email, phone, website, url_linkedin, twitter, linkedin_bio, url_twitter, job, id_task_user, date_created) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    newLine)

                logger.info("New added line in the DataBase.")
                connection.commit()
            logger.info("Commited successfully.")
        except Exception as ex:
            logger.error(f"Error when trying to commit new information in the contact {ex}")
            # Go to the last save.
            connection.rollback()
        finally:
            connection.close()

        # Add informations in actions
        try:
            connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
            cursor = connection.cursor()
            p_id_contact = cursor.execute("SELECT id FROM contacts WHERE username = ? AND phone = ?",
                                          (p_username, p_phone))
            p_id_contact = cursor.fetchone()[0]
            # print(p_id_contact)
            newLine = (p_platform, p_type_action,p_browser, p_id_social_account, date, p_id_contact,p_taskuser_id)
            # The '?' allows to avoid attacks by SQL's Injections
            with lock:
                cursor.execute(
                    "INSERT INTO actions (platform, type_action,id_smartphone, id_social_account, date_created, id_contact, id_task_user) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    newLine)
                logger.info("New added line in the DataBase.")
                connection.commit()
            logger.info("Commited successfully.")
        except Exception as ex:
            logger.error(f"Error when trying to commit new information in the actions {ex}")
            # Go to the last save.
            connection.rollback()
        finally:
            connection.close()

    #TEST PRINT
    list = []
    list.append(p_platform)
    list.append(newProfileUrl)
    list.append(newUsername)
    list.append(first_name)
    list.append(last_name)
    list.append(newLoca)
    list.append(newJob)
    list.append(newEmail)
    list.append(newPhone)
    list.append(newWebSite)
    list.append(newTwitter)
    list.append(url_twitter)
    list.append(newAbout)

    print("\n---- USER DATA SCRAPPED INFO ----")
    print(list)



# ===================================================================================================================
# ============================ METHOD TO SCRAP LINKEDIN RESULTS =====================================================
# ===================================================================================================================
def Linkedin_Search_By_Keywords_And_City(label_log, p_browser,p_id_social_account,p_limit, p_taskuser_id, lock, keywords=str, city=str):

    try:

        logger.info("======================================= [1] Open Browser =======================================")

        # Load the database
        sqliteConnection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))  # we prepare db
        cursor1 = sqliteConnection.cursor()

        # MakeGoogleSearchforLinkedin(p_id_social_account)
        MakeGoogleSearchforLinkedin(p_id_social_account, p_browser)
        Sleeping_Bot(7.5, 10.5)

        logger.info(
            "================================== START Scraping users data =========================================")

        # We get all the linkedin links in the database for the current user
        sql_urls = f"SELECT url FROM linkedin_profiles WHERE id_social_account = '{p_id_social_account}' "
        urls_linkedin_tuple = cursor1.execute(sql_urls).fetchall()
        urls_linkedin_list = [item[0] for item in urls_linkedin_tuple]

        scrap_limit = 1

        # Open the browser
        if p_browser == "Chrome":
            driver = mymodulesteam.ChromeDriverWithProfile()
        elif p_browser == "Firefox":
            driver = mymodulesteam.FireFoxDriverWithProfile()
        else:
            logger.error(f"PhoneBot didn't find the browser called '{p_browser}'.")

        # print the number or links find
        print(
            "\nNumber of profils find in database for current user : {} profils\n".format(str(len(urls_linkedin_list))))
        i = 0
        while (scrap_limit <= p_limit):

            link = urls_linkedin_list[i]
            print(f"link {i} : {link}\n")

            # Let's check if the user is already in contact table
            # if the profile is already in then we scrap it for an update but we don't count it as a scrap ( no scraping incrementation)
            sql_isAlreadyInDB = cursor1.execute("SELECT * FROM contacts WHERE url_linkedin=?", (link,)).fetchone()
            presence_sql = False

            if sql_isAlreadyInDB != None:
                presence_sql = True
            else:
                presence_sql = False

            # ============== PROFIL ALREADY IN CONTACT ======================

            if presence_sql == True:
                logger.info(
                    f"DESKTOP|||This Linkedin profile is already in table 'contacts'\n")
                total_time = 0
                # if last user update is upper dans one week we update the user
                udp_sql = cursor1.execute("SELECT date_update FROM contacts WHERE url_linkedin=?", (link,)).fetchone()
                upd_date = list(udp_sql)
                upd_date = upd_date[0]

                print(f"UPD_SQL --> '{udp_sql}'.")
                print(f"UPD_DATE --> {upd_date}")

                # We have to update the profil if the never did it before
                if upd_date == 'None' or upd_date == None:
                    logger.info(
                        f"DESKTOP|||updating this profile in the database \n")
                    Scrap_One_User(link, driver, city, p_id_social_account, p_taskuser_id)
                    Sleeping_Bot(2.5, 3.5)
                    i += 1

                else:
                    new_date = upd_date.split('.')
                    start = datetime.strptime(new_date[0], '%Y-%m-%d %H:%M:%S')

                    end = datetime.today()
                    total_time = end - start
                    total_time = total_time.total_seconds() / 604800.0  # convert datetime into week
                    total_time = int(total_time)

                print("Last update : {} weeks ago\n".format(str(total_time)))

                if total_time >= 4:
                    logger.info(
                        f"DESKTOP|||The last update for this Linkedin profile is greater than 4 weeks\n")
                    Scrap_One_User(link, driver, city, p_id_social_account, p_taskuser_id)
                    Sleeping_Bot(2.5, 3.5)
                    i += 1

                else:
                    logger.info(
                        f"DESKTOP|||The last update for this Linkedin profile is less than 4 weeks so we won't scrap him\n")
                    i += 1

            # ============== PROFIL NOT YET IN CONTACT ======================
            else:

                # Let's verify if the profil is unavailable
                driver.get(link)
                Sleeping_Bot(2.5, 3.5)
                is_unavailable_presence = False
                try:
                    is_unavailable = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.XPATH, (
                            "//div[contains(@class,'pv-profile-unavailable')]//div[contains(@class,'p8')]//div[contains(@class,'artdeco-empty-state')]//h1"))))
                    is_unavailable_presence = True
                except:
                    is_unavailable_presence = False

                Sleeping_Bot(2.5, 3.5)

                if is_unavailable_presence:
                    logger.info(
                        f"DESKTOP|||This Linkedin profile is no more available let's scrap another one\n")
                    i += 1

                else:
                    logger.info(
                        f"DESKTOP|||This Linkedin profile is not in table 'contacts'\n")
                    Scrap_One_User(link, driver, city, p_id_social_account, p_taskuser_id)
                    Sleeping_Bot(2.5, 3.5)
                    i += 1
                    scrap_limit += 1

        try:
            if driver:
                driver.quit()
        except:
            logger.error("Phonebot could'nt close the driver.")
        try:
            if cursor1:
                cursor1.close()
        except:
            logger.error("Phonebot could'nt close cursor1.")

        try:
            if sqliteConnection:
                sqliteConnection.close()
        except:
            logger.error("Phonebot could'nt close sqliteConnection.")
        return True

    except Exception as ex:
        logger.critical(f"{ex} -> DESKTOP|||Error with Linkedin_Search_By_Keywords_And_City!")



################################################################################################################################################
######################################################     [TEST]     ##########################################################################
################################################################################################################################################

"""
You must be connected with a linkedin account in your browser

If there is a bug when scraping all linkedin profils in Google, try to disconnect your google account and then retry

p_browser = "Firefox" or "Chrome"

p_id_social_account = "your_username"

p_limit = max_number_profils_toScrap
"""

p_browser = "Firefox"
p_id_social_account = "Julie Picasset"
p_limit = 2
p_taskuser_id = "276"
p_driver = ""
label_log = ""
lock = threading.Lock()


"""
for i in range(0, p_quantity_actions):
    keyword = key_city[i][0]
    city = key_city[i][1]
    city = city +", " +key_city[i][2]
    start = datetime.today()
    Linkedin_Search_By_Keywords_And_City(label_log, p_browser,p_id_social_account,p_limit, p_taskuser_id, lock, keyword, city)
    end = datetime.today()
    total_time = end - start
    total_time = total_time.total_seconds() / 60.0
    print(f"\\\\\ RUN DURATION : |{start}|---|{end}| /// ")
    print("Durée total : {} minutes".format(str(total_time)))"""


keyword = ""
city = ""
start = datetime.today()
Linkedin_Search_By_Keywords_And_City(label_log, p_browser,p_id_social_account,p_limit, p_taskuser_id, lock, keyword, city)
end = datetime.today()
total_time = end - start
total_time = total_time.total_seconds() / 60.0
print(f"\\\\\ RUN DURATION : |{start}|---|{end}| /// ")
print("Durée total : {} minutes".format(str(total_time)))