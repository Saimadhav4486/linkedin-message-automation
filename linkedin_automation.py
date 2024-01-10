from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from nltk.sentiment import SentimentIntensityAnalyzer
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
#Login to your linkedin profile
def login_to_linkedin(username, password):
    driver.get("https://www.linkedin.com/login")
    username_field = driver.find_element(By.ID,"username")
    password_field = driver.find_element(By.ID,"password")
    login_button = driver.find_element(By.CSS_SELECTOR,".login__form_action_container button")
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()


def get_section_text(driver, css_selector):
    try:
        section_text = driver.find_element(By.CSS_SELECTOR, css_selector)
        
        return section_text
    except NoSuchElementException:
        return ""
    
# Fetching about_us and recent_posts
def analyze_profile(connection_url):
    driver.get(connection_url)
    time.sleep(2)
    first_div = driver.find_element(By.CSS_SELECTOR, '.mt2.relative')
    about_us = first_div.find_element(By.CSS_SELECTOR, '.ztuHgugtzMptZBrByYjSNvODTFgWwuW.inline-show-more-text--is-collapsed.inline-show-more-text--is-collapsed-with-line-clamp.inline').text
    recent_posts = get_section_text(driver, '.scaffold-finite-scroll__content')
    recent_post = recent_posts.find_element(By.CSS_SELECTOR, '[dir=ltr]').text
    
    print(f"About us:{about_us}")
    return about_us, recent_post

#Generating personalized messages using about_us and recent posts
def generate_personalized_message(connection_name, about_us, recent_posts):
    sia = SentimentIntensityAnalyzer()
    about_us_sentiment = sia.polarity_scores(about_us)['compound']
    recent_posts_sentiment = sia.polarity_scores(recent_posts)['compound']
    about_us_message = (
        "I noticed your positive outlook in the 'About Us' section."
        if about_us_sentiment >= 0.2 else
        "I see some challenges in your 'About Us' section, let's connect and discuss."
        if about_us_sentiment <= -0.2 else
        "Your 'About Us' section seems balanced and interesting."
    ) if about_us else ""

    posts_message = (
        f"Your recent posts are quite positive. "
        if recent_posts_sentiment >= 0.2 else
        f"I noticed some concerns in your recent posts. "
        if recent_posts_sentiment <= -0.2 else
        f"Your recent posts are well-balanced. "
    ) if recent_posts else ""


    personalized_message = (
        f"Hello {connection_name}, {about_us_message} {posts_message}"
        f"I'm interested in connecting to learn more about your experiences."
    )

    return personalized_message

#Finally sending the request with a note
def send_connection_request(connection_url, message):
    driver = webdriver.Chrome()
    driver.get(connection_url)

    connect_button = driver.find_element(By.CSS_SELECTOR, '.pv-s-profile-actions__action')
    connect_button.click()

    add_note_button = driver.find_element(By.CSS_SELECTOR, '.mr1')
    add_note_button.click()

    note_textbox = driver.find_element(By.ID, 'custom-message')
    note_textbox.send_keys(message)

    send_request_button = driver.find_element(By.CSS_SELECTOR, '.ml1')
    send_request_button.click()

    driver.quit()


def monitor_new_connections():
    driver.get("Competitor's profile") # Customize it with competitor's linkedin profile page
    time.sleep(1)
    new_connections = driver.find_elements(By.CSS_SELECTOR,".scaffold-finite-scroll__content")
    for connection in new_connections:
        connection_name = connection.find_element(By.CSS_SELECTOR,".mn-connection-card__name").text
        connection_link = connection.find_element(By.CSS_SELECTOR,".mn-connection-card__link").get_attribute('href')
        about_us, recent_post = analyze_profile(connection_link)
        personalized_message = generate_personalized_message(connection_name, about_us, recent_post)

        send_connection_request(connection_link, personalized_message)


login_to_linkedin('username','password')
monitor_new_connections()

