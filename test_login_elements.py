from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Test counters
total_tests = 0
tests_passed = 0

try:
    driver.get("http://localhost:5005/loginscreen")
    wait = WebDriverWait(driver, 10)

    print("--= Beginning Tests For Tyler Mullins =--")

    # 1. Logo image exists
    total_tests += 1
    try:
        logo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.logo")))
        print("[PASSED] - Logo image found.")
        tests_passed += 1
    except:
        print("[FAILED] - Logo image not found.")

    # 2. Title text
    total_tests += 1
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h2.brand-title").text
        if title.strip() == "OnlyCelebs":
            print("[PASSED] - Title is correct.")
            tests_passed += 1
        else:
            print("[FAILED] - Title text is incorrect.")
    except:
        print("[FAILED] - Title not found.")

    # 3. Intro Message
    total_tests += 1
    try:
        copy = driver.find_element(By.CSS_SELECTOR, "p.text-muted").text
        if copy.strip() == "Exclusive community for stars and fans ✨":
            print("[PASSED] - Intro message is correct.")
            tests_passed += 1
        else:
            print("[FAILED] - Intro message is incorrect.")
    except:
        print("[FAILED] - Intro message not found.")

    # 4. Form exists
    total_tests += 1
    try:
        form = driver.find_element(By.TAG_NAME, "form")
        print("[PASSED] - Form found.")
        tests_passed += 1
    except:
        print("[FAILED] - Form not found.")

    # 5. Username input
    total_tests += 1
    try:
        username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        print("[PASSED] - Username input found.")
        tests_passed += 1
    except:
        print("[FAILED] - Username input not found.")

    # 6. Password input
    total_tests += 1
    try:
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        print("[PASSED] - Password input found.")
        tests_passed += 1
    except:
        print("[FAILED] - Password input not found.")

    # 7. Login button
    total_tests += 1
    try:
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        print("[PASSED] - Login button found.")
        tests_passed += 1
    except:
        print("[FAILED] - Login button not found.")

    # 8. Create button
    total_tests += 1
    try:
        create_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Create']")
        print("[PASSED] - Create button found.")
        tests_passed += 1
    except:
        print("[FAILED] - Create button not found.")

    # 9. Form method is POST
    total_tests += 1
    try:
        if form.get_attribute("method").lower() == "post":
            print("[PASSED] - Form method is POST.")
            tests_passed += 1
        else:
            print("[FAILED] - Form method is not POST.")
    except:
        print("[FAILED] - Could not verify form method.")

    # 10. Form action is /login
    total_tests += 1
    try:
        if form.get_attribute("action").endswith("/login"):
            print("[PASSED] - Form action is '/login'.")
            tests_passed += 1
        else:
            print("[FAILED] - Form action is not '/login'.")
    except:
        print("[FAILED] - Could not verify form action.")

except Exception as e:
    print("Error:", e)

finally:
    print("--= Ending Tests =--")
    print(f"{total_tests} Tests Ran: {tests_passed} Tests Passed")
    driver.quit()

