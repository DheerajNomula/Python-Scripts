import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(ChromeDriverManager().install())
url = 'https://www.flipkart.com/'
driver.get(url)
# waiting for the page to load
temp = driver.find_elements_by_class_name("_2I9KP_")  # nav bar
output = []
categoriesCompleted = []
output1 = []
type = 'Men'
for div in temp:
    if div.text != type:
        continue
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    hover = ActionChains(driver).move_to_element(div).perform()
    WebDriverWait(driver, 10)  # wait till below class appears
    # navbar's class
    categories = driver.find_elements_by_css_selector("._3QN6WI._1MMnri._32YDvl")
    categoryUrls = []

    # Iterating through each of the category and storing cateogry corresponding urls
    for category in categories:
        categoryUrls.append(str(category.get_attribute("href")))

    for categoryUrl in categoryUrls:
        category = categoryUrl.split('/')[3]
        if category in categoriesCompleted:
            continue
        categoriesCompleted.append(category)
        categoryData = {}
        driver.get(categoryUrl)
        WebDriverWait(driver, 10)  # wait till search bar appears

        # getting all the filters present on left side
        filters = driver.find_elements_by_css_selector('._167Mu3._2hbLCH')
        for filter in filters:
            if 'BRAND' not in str(filter.text).split('\n'):
                continue

            # clicking on the see more for brands
            try:
                filter.find_element_by_css_selector('.QvtND5._2w_U27').click()
            except:
                filter.find_element_by_css_selector('._3xglSm._1iMC4O').click()

            categoryData['category'] = category
            categoryData['brands'] = ''
            for brand in filter.find_elements_by_class_name('_38vbm7'):
                brandName = str(brand.text)
                categoryData['brands'] += brandName + '\n'
                output1.append({'category': category, 'brand': brandName, 'gender': type})
            break
        output.append(categoryData)
    break

driver.refresh()
df = pd.DataFrame(output1)
df.to_csv('flipkart_brands.csv')

webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

# searching for the brand and getting the number of products
file = pd.read_csv('flipkart_brands.csv')
brands = set()
existing_brands = set()
for index, row in file.iterrows():
    brands.add(row['gender'] + ' ' + row['category'] + ' ' + row['brand'])

for brand in brands:
    search_str = str(brand)
    #typing the search string in search bar
    tt = driver.find_element_by_class_name('O8ZS_U').find_element_by_tag_name('input')
    tt.send_keys(search_str)
    tt.submit()
    try:
        WebDriverWait(driver, 1000).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.t-0M7P._2doH3V')))  # wait till search bar appears
    except:
        continue
    x = 0
    row = {}
    #getting the number of products
    try:
        string = str(driver.find_element_by_class_name('_2yAnYN').text)
        if string[string.find("\""):] == "\"" + brand + "\"":
            x = string.split(' ')[5]
    except:
        x = 0
    row['no_of_products'] = x
    row['brand'] = brand;
    output1.append(row)
    driver.get(url)
    df = pd.DataFrame(output1)
    # writing to a file
    df.to_csv('output.csv', index=False)
