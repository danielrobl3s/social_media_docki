#We import all the necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from csv import DictReader
import os
import random, time, zipfile
from selenium_stealth import stealth
from cdriver import Driver
from bs4 import BeautifulSoup
from lxml import etree, html
import os
from dotenv import load_dotenv
import random
import pandas as pd
from datetime import datetime

# Load the .env file
load_dotenv()

#Get your actual credentials from the .env file
#Your mail from .env file (modify the .sample_env file to .env and add your credentials)
fb_mail = os.getenv("FACEBOOK_USERNAME")
#Your password from .env file
fb_pass = os.getenv("FACEBOOK_PASSWORD")


#Define our XPATH variables to locate the credentials fields:

#email field
email_field = "//input[@type='text']"

#password field
passw_field = "(//input[@type='password'])[2]"

#Enter button
enter_button = "//div[@aria-label='Log in to Facebook']"



def pandas_to_csv(data: list[dict], filename: str) -> None:
    """
      Function that takes a list of dictionaries and a filename as arguments. \n
      such list comes from the "execute" function that extracts data from Facebook and turns it into a list of dictionaries. \n
      Filename is prompted by the user and is used to save the data in a CSV file. \n
    """

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame([item for item in data])
    
    # Save the DataFrame to a CSV file
    df.to_csv(f'{filename}.csv', index=False)



def clean_data(data: list[str]) -> str:
   """
   Takes a list with a single string element inside as argument and if it is empty, returns 'empty', if not \n
   returns the first element of the list. \n
   """
   if not data:
      return "empty"
   else:
      return data[0]


def execute(username: str, filename: str, length: int = 10, year: str = "", month: str = "", day: str = "") -> None:
   """

   "execute" function scrapes a Facebook profile and saves the data to a CSV file. \n
   It takes the following arguments: \n
   - username: The username of the Facebook profile to scrape. \n
   - filename: The name of the output file (without extension). \n
   - length: The number of posts to scrape (default is 10). \n
   - year: The year to scrape as string (optional). \n
   - month: The month to scrape as string (optional). \n
   - day: The day to scrape as string (optional). \n
   The function uses the Selenium WebDriver to navigate to the Facebook profile page and scrape the data. \n
   It uses a modified instance of the webdriver Driver class to go undetected and increase success rate. \n
   The modified Driver takes the following arguments: \n
   - url: The URL of the website you want to scrape (A Facebook profile in this case). \n
   - headless: A boolean value that determines whether to run the browser in headless mode or not. \n
   - proxy: A boolean value that determines whether to run the scraper with proxy server or not. \n
   - scroll: A boolean value that determines whether to scroll the page or not. \n
   - cookies_fb: A boolean value that determines whether to use tailored cookies for Facebook or not. (You must include your own cookies file specifically named: "facebook_cookies.csv") \n
   - cookies_tk: A boolean value that determines whether to use tailored cookies for Tiktok or not. (You must include your own cookies file specifically named: "tiktok_cookies.csv") \n
   - capture_traffic: A boolean value that determines whether to capture network traffic or not. \n

    """
   
   # Create a new instance of the Driver class with the url to facebook using f string to match the profile url
   driver = Driver.get(url=f"https://facebook.com/{username}", scroll=False)

   actions = ActionChains(driver)
   
   # Wait for the page to load
   time.sleep(10)

   #Send credentials here
   
   #email (replace with yours)
   driver.find_element(By.XPATH, email_field).send_keys(fb_mail)
   
   #password (replace with yours)
   driver.find_element(By.XPATH, passw_field).send_keys(fb_pass)

   #press log in button
   driver.find_element(By.XPATH, enter_button).click()

   time.sleep(10)

   # Define scroll parameters
   POST_HEIGHT = 800  # Approx. height of one post in pixels
   DESIRED_POSTS = length  # Number of posts you want
   SCROLL_PAUSE_TIME = 2  # Time to wait between scrolls (for loading)

   # Calculate total scroll needed (posts × post height)
   total_scroll = POST_HEIGHT * DESIRED_POSTS

   # Find the buttons and dropdown lists to select the date
   if year:

      #Click the "Filters" button to open the filters menu
      driver.find_element(By.XPATH, "//*[contains(text(), 'Filtros')]").click()
      # Wait for the filters menu to load
      time.sleep(5)

      #Click the "Año" button to open the year dropdown
      driver.find_element(By.XPATH, "//div[@aria-haspopup='listbox']").click()

      # Wait for the year dropdown to load
      time.sleep(3)

      # Select the year from the dropdown
      driver.find_element(By.XPATH, f"//div[@class='x4k7w5x x1h91t0o x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1n2onr6 x1qrby5j x1jfb8zj']//*[contains(text(), '{year}')]/../../..").click()

      # Select month if provided
      if month:
         #Wait a bit
         time.sleep(5)

         #Click the "Mes" button to open the month dropdown
         driver.find_element(By.XPATH, "(//div[@aria-haspopup='listbox'])[2]").click()
         
         # Wait for the month dropdown to load
         time.sleep(5)

         # Select the month from the dropdown
         driver.find_element(By.XPATH, f"//div[@class='xu06os2 x1ok221b']/span[contains(text(), '{month}')]").click()

         # Select day if provided
         if day:
            #Wait a bit
            time.sleep(5)

            # Click the "Día" button to open the day dropdown
            driver.find_element(By.XPATH, "(//div[@aria-haspopup='listbox'])[3]").click()

            # Wait for the day dropdown to load
            time.sleep(5)

            string_day = int(day) + 1

            # Select the day from the dropdown
            driver.find_element(By.XPATH, f"(//div[@class='x1i10hfl xjbqb8w x1ejq31n x18oe1m7 x1sy0etr xstzfhl x972fbf x10w94by x1qhh985 x14e42zd xe8uvvx x1hl2dhg xggy1nq x1fmog5m xu25z0z x140muxe xo1y3bh x87ps6o x1lku1pv x1a2a7pz x6s0dn4 xjyslct x9f619 x1ypdohk x78zum5 x1q0g3np x2lah0s x1i6fsjq xfvfia3 x8e7100 x1a16bkn x10wwi4t x1x7e7qh xgm7xcn x1ynn3ck x1n2onr6 x16tdsg8 x1ja2u2z'])[{ str(string_day) }]").click()

      # Wait a bit
      time.sleep(5)

      # Click the "Aplicar" button to apply the filters
      driver.find_element(By.XPATH, "(//div[@aria-label='Listo'])[2]").click()

      # Wait for the filters to apply
      time.sleep(10)

   # Smooth scroll using JavaScript
   for i in range(0, total_scroll, POST_HEIGHT):  # Scroll in increments of post height
      
      rand_sleep_time = random.randint(1, 5)

      time.sleep(rand_sleep_time)
      driver.execute_script(f"window.scrollBy(0, {POST_HEIGHT});")
      time.sleep(SCROLL_PAUSE_TIME)  # Let new posts load

   # We turn the source to a string and parse it with BeautifulSoup
   html = driver.page_source

   #Parse the HTML with BeautifulSoup
   soup = BeautifulSoup(html, "lxml")
   #We use etree to parse the HTML
   dom = etree.HTML(str(soup))

   #We define an empty list to store all "rows" for our csv file
   data = []

   # Iterate through each post and get its title, reactions, comments and share counts respectively
   for i in range(1, length + 1):

      #post we want to get (it gets the number of posts we want to get and loops until the last of them on ["+str(i)+"]), i is the current iteration of length:
      posts = "(//div[@data-pagelet='ProfileTimeline']/div[@data-pagelet='TimelineFeedUnit_{n}'])["+str(i)+"]"

      #Expression added to "posts", to get that specific post title texts
      post_title = posts + "//div[@style='text-align: start;']//text()"

      #time.sleep(800)

      #We get the engagement elements, which are located on the reactions bar
      engagement_elements = posts + "//div[@class='x6s0dn4 xi81zsa x78zum5 x6prxxf x13a6bvl xvq8zen xdj266r xat24cr x1c1uobl xyri2b x1diwwjn xbmvrgn x1yrsyyn x18d9i69']"
      
      #We get the number of reactions, comments and shares using the xpath

      reactions_xpath = engagement_elements + "//span[@class='xt0b8zv x135b78x']//text()"
      reactions_count = dom.xpath(reactions_xpath)

      #Comments xpath:
      comments_count_xpath = engagement_elements + "//span[contains(text(), 'comentario')]//text()"
      #Comments count:
      comments_count = dom.xpath(comments_count_xpath)

      #Shares xpath:
      shares_count_xpath = engagement_elements + "//span[contains(text(), 'compartido')]//text()"
      #Shares count:
      shares_count = dom.xpath(shares_count_xpath)

      #Find using dom.xpath and passing post_title through
      text_elements = dom.xpath(post_title)

      #Find the post date
      post_date_xpath = "((//span[@class='html-span xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x1hl2dhg x16tdsg8 x1vvkbs']//a[@aria-label])/text())["+str(i)+"]"
      post_date = dom.xpath(post_date_xpath)

      #Get today date
      today_date = datetime.now().strftime("%d/%m/%Y")


      #We check if a post is a list and iterate through until "Ver más" text is present, it means the caption is over
      if type(text_elements) == list:

         #We need to concatenate the text elements to get the full title, we define an empty string for that: "complete_title"
         complete_title = ""

         # Iterate through the list of text elements
         for text in text_elements: 
               
               #Each element is concatenated to the previous "complete_title" string so it is updated each iteration
               complete_title += text + ""

               #Stop if "Ver más" is present, because all captions stop with "Ver más"
               if "ver más" in text.lower():
                  break

         
         
         #We clean the data from the reactions, comments and shares counts
         reactions_count = clean_data(reactions_count)
         comments_count = clean_data(comments_count)
         shares_count = clean_data(shares_count)


         # Print to check if the data is correct
         print(str(i) + ": " + complete_title + "\n" + " reactions: " + str(reactions_count) + "\n" + " comments: " + str(comments_count) + "\n" + " shares: " + str(shares_count) + "\n" + " date of post: " + str(post_date) + "\n" + " extraction date: " +str(today_date) + "\n")
      
      #If the text_elements variable is a single string and has a length greater than 0, we print it
      elif type(text_elements) == str and len(text_elements) > 0:
         print(str(i) + ": " + text_elements + "\n" + " reactions: " + str(reactions_count) + "\n" + " comments: " + str(comments_count) + "\n" + " shares: " + str(shares_count) + "\n"+ " date of post: " + str(post_date) + "\n" + " extraction date: " +str(today_date) + "\n")  
      
      #if not, then is likely no text is present
      else:
         print("No title" + "\n" + " reactions: " + str(reactions_count) + "\n" + " comments: " + str(comments_count) + "\n" + " shares: " + str(shares_count) + "\n" + " date of post: " + str(post_date) + "\n" + " extraction date: " + str(today_date) + "\n")
      
      data.append({"title": complete_title, "reactions": reactions_count, "comments": comments_count, "shares": shares_count, "date_of_post": post_date, "extraction_date": today_date})

   #We save the data to a CSV file using pandas
   pandas_to_csv(data, filename)

   print(f"{username} scraped successfully! , saved in {filename}.csv file with {length} posts")






def main():
   """
   This is the main function that runs the script. \n
   It displays a menu to the user and prompts them to select an option. \n
   If the user selects option 1, they are prompted to enter a username to scrape.
   Otherwise, the script exits.

   To scrape users, the script uses the execute function, which takes a username as an argument,
   a name for the output file and the length of the scraping in number of posts.

   """

   # Display the menu to the user
   menu = input("Welcome to the Facebook scraper script!, please select an option: \n"
   "1. Scrape a Facebook Profile \n"
   "2. Exit \n"
   ">> "
   )

   # If the user selects option 1, prompt them to enter a username

   if menu == "1":
      username = input("Please enter the username of the Facebook profile you want to scrape: \n" \
      ">> ")

   # If the username is empty it will throw an error, otherwise, executes the function 'execute'
      
      if len(username) == 0:
         print("Please enter a valid username.")
         return
      else:
         # Prompt the user for the output file name
         filename = input("Please enter a name for the output file (without extension): \n" \
                          ">> ")
         length = int(input("How many posts do you want to scrape? (min 5) \n" \
                        ">> "))
         
         # If the length is empty it will throw an error, otherwise, executes the function 'execute'
         if length <= 0:
            return
         else:
            # Prompt the user for the date to scrape
            year = input("What year do you want to scrape? (YYYY) \n" \
                        ">> ")
            month = input("What month do you want to scrape? (Month (Example: abril) \n" \
                          ">> ")
            day = input("What day do you want to scrape? (DD) \n" \
                        ">> ")
            
            # Apply filters, by year or not, month or not, day or not
            if year:
               if month:
                  if day:
                     execute(username, filename, length, year, month, day)
                  else:
                     execute(username, filename, length, year, month)

               else:
                  execute(username, filename, length, year)
            else:
               execute(username, filename, length)

   else:
      print("Goodbye!")




#Entry point! This is where the script starts executing
if __name__ == "__main__":
   main()