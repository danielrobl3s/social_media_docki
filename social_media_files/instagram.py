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
ig_mail = os.getenv("INSTAGRAM_USERNAME")

#Your password from .env file
ig_pass = os.getenv("INSTAGRAM_PASSWORD")


#Define our XPATH variables to locate the credentials fields:

#email field
email_field = "//input[@aria-label='Phone number, username, or email']"

#password field
passw_field = "//input[@aria-label='Password']"

#wait until Log In button activates
time.sleep(3)

#Enter button
enter_button = "//button[@type='submit']"



def pandas_to_csv(data: list[dict], filename: str) -> None:
    """
      Function that takes a list of dictionaries and a filename as arguments. \n
      such list comes from the "execute" function that extracts data from Facebook and turns it into a list of dictionaries. \n
      Filename is prompted by the user and is used to save the data in a CSV file. \n
    """

    # Create a DataFrame from the list of dictionaries

    df = pd.DataFrame([item for item in data])

    output_path = f"/output_logs/{filename}.csv"
    
    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)



def clean_data(data: list[str]) -> str:
   """
   Takes a list with a single string element inside as argument and if it is empty, returns 'empty', if not \n
   returns the first element of the list. \n
   """
   if not data:
      return "empty"
   else:
      return data[0]
   

def click_through_instagram_feed(driver, desired_posts) -> list:
    """
    Scrolls Instagram feed to load a specific number of posts.
    - Instagram posts are smaller (~400px tall) and appear in rows of 3.
    - Scrolls in smaller increments and adds randomness.
    """
    #variable to store the rows:
    posts_rows = []

    actions = ActionChains(driver)

    # Randomize scroll distance (150-300px)
    scroll_distance = random.randint(150, 300)

    # Execute the scroll action
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    
    # Random delay
    actions.pause(random.uniform(0.5, 1.5)).perform()


    # Wait for the feed to load
    time.sleep(4)

    # Click the first post to open it
    first_post = "(//div[@class='_aagw'])[1]" #XPATH for the first post in the feed
    driver.find_element(By.XPATH, first_post).click()

    #counter for the number of posts in console
    counter = 0

    # Loop through the desired number of posts
    for i in range(desired_posts):
      counter += 1 # Increment the counter for each post

      # We turn the source to a string and parse it with BeautifulSoup
      html = driver.page_source

      #Parse the HTML with BeautifulSoup
      soup = BeautifulSoup(html, "lxml")

      #We use etree to parse the HTML
      dom = etree.HTML(str(soup))

      # Wait for the post to load
      time.sleep(3)

      # Extract the title
      titles = [] #list to store the titles
      titles_xpath = "//div[@class='_a9zn _a9zo']//h1//text()" #XPATH to retrieve the titles
      titles_array = dom.xpath(titles_xpath) # Execute the XPATH query to get the titles 

      # We define a variable to store the titles, if there are multiple titles in the caption they are concatenated
      title = ""

      # Loop through the titles array and concatenate them
      for title_instance in titles_array:
         title += title_instance + " "

      # Get the number of likes from the post
      # We define a variable to store the likes
      # likes_xpath = "(//span[@class='x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi xpm28yp x8viiok x1o7cslx']//text())[1]"

      # likes = dom.xpath(likes_xpath) # Execute the XPATH query to get the likes
      # print(f"LIKES: {likes}")

      likes_xpath = "//span[@class='x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi xpm28yp x8viiok x1o7cslx']//text()"

      likes_raw = dom.xpath(likes_xpath)

      likes = None
      for text in likes_raw:
         text = text.strip()
         # Si el texto NO contiene "other" y sí tiene dígitos
         if "other" not in text.lower() and any(char.isdigit() for char in text):
            try:
                  likes = text  # quita comas y convierte a número
                  break  # salimos al encontrar el válido
            except ValueError:
                  continue


      #Get the date of the post
      date_xpath = "(//time[@title])[2]//text()"
      post_date = dom.xpath(date_xpath) # Execute the XPATH query to get the date

      #We set the extraction date of the post with the date.now method
      today_date = datetime.now()


      # Use a try/except block to handle cases where there are no likes
      try:
      
         print(f"Post {counter}: ")
         print({"title": title, "likes": likes})
         print({"date": post_date[0]})
         print({"extraction_date": today_date.strftime("%Y-%m-%d %H:%M:%S")})

         # Append the post data to the posts_rows list
         posts_rows.append({"title": title, "likes": likes, "date": post_date[0], "extraction_date": today_date.strftime("%Y-%m-%d %H:%M:%S")})
      
      except:
         # If there are no likes, we set the likes to 0 and we print all the data
         print(f"Post {counter}: ")
         print({"title": title, "likes": "0"})
         print({"date": post_date})
         print({"extraction_date": today_date.strftime("%Y-%m-%d %H:%M:%S")})

         # Append the post data to the posts_rows list with 0 likes
         posts_rows.append({"title": title, "likes": "0 likes", "date": post_date, "extraction_date": today_date.strftime("%Y-%m-%d %H:%M:%S")})

      # Click the next post button
      next_post_button = "//div[@class=' _aaqg _aaqh']//button"

      driver.find_element(By.XPATH, next_post_button).click()

    return posts_rows

    
   
   
def find_user(driver: webdriver.Chrome, username: str) -> None:
   """
   This function is used to find a user by their instagram username
   it takes only the driver as argument and applies the corresponding logic to find the user and start scraping
   """

   #click the search button to open the left sidebar and start looking for a user
   search_button = "(//div[@class='x9f619 x3nfvp2 xr9ek0c xjpr12u xo237n4 x6pnmvc x7nr27j x12dmmrz xz9dl7a xpdmqnj xsag5q8 x1g0dm76 x80pfx3 x159b3zp x1dn74xm xif99yt x172qv1o x4afuhf x1lhsz42 x10v4vz6 xdoji71 x1dejxi8 x9k3k5o x8st7rj x11hdxyr x1eunh74 x1wj20lx x1obq294 x5a5i1n xde0f50 x15x8krk'])[2]"
   driver.find_element(By.XPATH, search_button).click()

   #wait 3 seconds
   time.sleep(3)

   #Find the search input field
   search_field = "//div[@class='xjoudau x6s0dn4 x78zum5 xdt5ytf x1c4vz4f xs83m0k xrf2nzk x1n2onr6 xh8yej3 x1hq5gj4']//input"
   driver.find_element(By.XPATH, search_field).send_keys(username)

   time.sleep(5)

   #Search through the results the corresponding profile as with the exact username, the first result WILL ALWAYS be your target
   user_button = f"(//div[@class='html-div xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x9f619 xjbqb8w x78zum5 x15mokao x1ga7v0g x16uus16 xbiv7yw x1uhb9sk x1plvlek xryxfnj x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1cy8zhl x1oa3qoh x1nhvcw1']//*[contains(text(), '{username}')]/../..)[1]"
   driver.find_element(By.XPATH, user_button).click()

   time.sleep(30)




def execute(username: str, filename: str, length: int = 10) -> None:
   """

   "execute" function scrapes a Facebook profile and saves the data to a CSV file. \n
   It takes the following arguments: \n
   - username: The username of the Facebook profile to scrape. \n
   - filename: The name of the output file (without extension). \n
   - length: The number of posts to scrape (default is 10). \n
   \n
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
   driver = Driver.get(url=f"https://instagram.com", scroll=False)

   actions = ActionChains(driver)
   
   # Wait for the page to load

   #Send credentials here
   
   #email (replace with yours)
   driver.find_element(By.XPATH, email_field).send_keys(ig_mail)
   
   #password (replace with yours)
   driver.find_element(By.XPATH, passw_field).send_keys(ig_pass)

   time.sleep(3)

   #press log in button
   driver.find_element(By.XPATH, enter_button).click()

   time.sleep(10)

   #Skip the "Save your login info?" dialog with "not now" button
   #XPATH for "not now" button
   not_now_button = "//div[@class='x78zum5 xdt5ytf x1e56ztr']//div"
   driver.find_element(By.XPATH, not_now_button).click()

   time.sleep(4)

   #dismiss the novelty button
   novelty_button = "(//div[@role='button'])[last()]"
   driver.find_element(By.XPATH, novelty_button).click()

   time.sleep(4)

   #Start looking for the user
   find_user(driver, username)

   #Get through each post and store in a list
   posts = click_through_instagram_feed(driver, length)

   #parse everything and send to csv file
   pandas_to_csv(posts, filename)






def main():
   """
   This is the main function that runs the script. \n
   It displays a menu to the user and prompts them to select an option. \n
   If the user selects option 1, they are prompted to enter a username to scrape.
   Otherwise, the script exits.

   To scrape users, the script uses the execute function, which takes a username as an argument,
   a name for the output file and the length of the scraping in number of posts.

   """

   with open("params_ig.json", "r") as f:
    params_list = json.load(f)

   for params in params_list:

      username=params["username"]
      filename=params["filename"]
      length=params["length"]

      print(f"\n[INFO] Running scraper for: {username}")
      execute(username, filename, length)

      random_sleeper = random.randint(5, 30)
      time.sleep(random_sleeper)

   # # Display the menu to the user
   # menu = input("Welcome to the Instagram scraper script!, please select an option: \n"
   # "1. Scrape a Instagram Profile \n"
   # "2. Exit \n"
   # ">> "
   # )

   # # If the user selects option 1, prompt them to enter a username

   # if menu == "1":
   #    username = input("Please enter the username of the Instagram profile you want to scrape: \n" \
   #    ">> ")

   # # If the username is empty it will throw an error, otherwise, executes the function 'execute'
      
   #    if len(username) == 0:
   #       print("Please enter a valid username.")
   #       return
   #    else:
   #       # Prompt the user for the output file name
   #       filename = input("Please enter a name for the output file (without extension): \n" \
   #                        ">> ")
   #       length = int(input("How many posts do you want to scrape? (min 5) \n" \
   #                      ">> "))
         
   #       # If the length is empty it will throw an error, otherwise, executes the function 'execute'
   #       if length <= 0:
   #          return
   #       else:

   #          #execute our function with no filters since there are none for instagram
   #          execute(username, filename, length)
            

   # else:
   #    print("Goodbye!")




#Entry point! This is where the script starts executing
if __name__ == "__main__":
   main()