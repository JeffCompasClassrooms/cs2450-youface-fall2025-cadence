import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Configuration ---
# !! IMPORTANT !!
# Update these with a real username and password for your app
VALID_USERNAME = "YOUR_VALID_USERNAME"
VALID_PASSWORD = "YOUR_VALID_PASSWORD"

# Base URL for your running application
# Using the one from your example script
APP_URL = "http://localhost:5005/loginscreen"

# Set up Chrome options for headless execution
options = Options()
options.add_argument("--headless")
# options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the Chrome driver
driver = webdriver.Chrome(options=options)

# Test counters
total_tests = 0
tests_passed = 0

try:
    # Navigate to the app's login screen
    driver.get(APP_URL)
    # Wait for up to 10 seconds for elements to appear
    wait = WebDriverWait(driver, 10)

    # --- START OF TESTS ---
    # Replace "Jane Doe" with your actual name
    print("Beginning Tests - Caden Ringwood")

    # --- Login Page Tests ---

    # 1. Login Page Title (Assuming your login page has this title)
    total_tests += 1
    try:
        # Check for the title you provided in the example
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.brand-title"))).text
        if title.strip() == "OnlyCelebs":
             print("[PASSED] - Login Page Title is correct")
             tests_passed += 1
        else:
             print(f"[FAILED] - Login Page Title is incorrect. Found: '{title}'")
    except:
        print("[FAILED] - Login Page Title Not Found")


    # 2. Username Input Exists
    total_tests += 1
    try:
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
        print("[PASSED] - Username Input Exists")
        tests_passed += 1
    except:
        print("[FAILED] - Username Input Not Found")

    # 3. Password Input Exists
    total_tests += 1
    try:
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        print("[PASSED] - Password Input Exists")
        tests_passed += 1
    except:
        print("[FAILED] - Password Input Not Found")

    # 4. Login Button Exists
    total_tests += 1
    try:
        login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='submit'][value='Login']")))
        print("[PASSED] - Login Button Exists")
        tests_passed += 1
    except:
        print("[FAILED] - Login Button Not Found")

    # --- Perform Login ---
    try:
        # Find elements again to interact with them
        username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        
        username_input.send_keys('caden')
        password_input.send_keys('yay')
        login_button.click()
    except Exception as e:
        print(f"Error during login attempt: {e}")

    # --- Feed Page Tests (Post-Login) ---
    
    # 5. Login Succeeds (Test by finding a key element on the feed page)
    total_tests += 1
    try:
        # Wait for the "My Friends" title, which only appears on the feed page
        wait.until(EC.presence_of_element_located((By.XPATH, "//h3[text()='My Friends']")))
        print("[PASSED] - Login Succeeded (Feed Page loaded)")
        tests_passed += 1
    except:
        print("[FAILED] - Login Failed (Feed Page did not load)")
        # If login fails, we stop the script as other tests will also fail
        raise Exception("Login failed, cannot proceed with feed page tests.")

    # 6. Header Logo Exists on Feed Page
    total_tests += 1
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='Only Celebs Logo']")))
        print("[PASSED] - Header Logo Exists")
        tests_passed += 1
    except:
        print("[FAILED] - Header Logo Not Found")

    # 7. Search Bar Exists
    total_tests += 1
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search for celebs, news & gossip']")))
        print("[PASSED] - Search Bar Exists")
        tests_passed += 1
    except:
        print("[FAILED] - Search Bar Not Found")

    # 8. User Menu Button Exists
    total_tests += 1
    try:
        wait.until(EC.presence_of_element_located((By.ID, "userMenuButton")))
        print("[PASSED] - User Menu Button Exists")
        tests_passed += 1
    except:
        print("[FAILED] - User Menu Button Not Found")

    # 9. "My Story" Placeholder Exists
    total_tests += 1
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='My Story']")))
        print("[PASSED] - 'My Story' Placeholder Exists")
        tests_passed += 1
    except:
        print("[FAILED] - 'My Story' Placeholder Not Found")

    # 10. "Share Your Insight" Title Exists
    total_tests += 1
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//h3[text()='Share Your Insight']")))
        print("[PASSED] - 'Share Your Insight' Title Exists")
        tests_passed += 1
    except:
        print("[FAILED] - 'Share Your Insight' Title Not Found")


except Exception as e:
    # Print any unexpected errors during the test execution
    print(f"\nAn error occurred: {e}")

finally:
    # This block will run whether the tests succeed or fail
    print("Ending Tests:")
    # Print the final test summary
    print(f"{total_tests} Tests Ran: {tests_passed} Tests Passed")
    # Clean up and close the browser
    driver.quit()

