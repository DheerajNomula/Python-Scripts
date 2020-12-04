from selenium import webdriver
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome(ChromeDriverManager().install())
url = 'https://www.amazon.in/b?node=6648217031'
driver.get(url)
# waiting for the page to load
temp = driver.find_element_by_id("nav-subnav")  # nav bar
output = []
categoriesCompleted = []
output1 = []
womenId = 'nav-flyout-aj:https://images-eu.ssl-images-amazon.com/images/G/31/img16/wayfinding/json/subnavmay18.json:subnav-sl-megamenu-1:0'
menId = 'nav-flyout-aj:https://images-eu.ssl-images-amazon.com/images/G/31/img16/wayfinding/json/subnavmay18.json:subnav-sl-megamenu-2:0'
kidsId = 'nav-flyout-aj:https://images-eu.ssl-images-amazon.com/images/G/31/img16/wayfinding/json/subnavmay18.json:subnav-sl-megamenu-3:0'
temp = [womenId, menId, kidsId]
count = 0


def getBrandsWithoutLoad(categoryData, ulTag):
    ulTag.find_elements_by_tag_name('a')[0].click()
    brands = str(ulTag.text).split('\n')
    categoryData['brands'] = ""
    for brand in brands:
        categoryData['brands'] += brand + '\n'
        output1.append({'category': categoryData['category'], 'gender': categoryData['gender'], 'brand': brand})

def directlyById(categoryData):
    try:
        aTags = driver.find_element_by_id('brandsRefinements').find_elements_by_tag_name('a')
        aTags[len(aTags)-1].click()
        brands = str(driver.find_element_by_id('brandsRefinements').text).split('\n')
        categoryData['brands'] = ""
        for brand in brands:
            categoryData['brands'] += brand + '\n'
            output1.append({'category': categoryData['category'], 'gender': categoryData['gender'], 'brand': brand})
    except:
        return

for aTag in driver.find_element_by_id('nav-subnav').find_elements_by_tag_name('a'):
    if aTag.text != 'Women' and aTag.text != 'Men' and aTag.text != 'Kids':
        continue
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    hover = ActionChains(driver).move_to_element(aTag).perform()
    WebDriverWait(driver, 10)  # wait till below class appears
    subCategoriesDiv = driver.find_element_by_id(temp[count]).find_element_by_css_selector(
        '.nav-template.nav-flyout-content').find_element_by_class_name('mega-menu').find_elements_by_class_name(
        'mm-column')
    for subCategoryDiv in subCategoriesDiv:
        h4Tags = subCategoryDiv.find_elements_by_tag_name('h3')
        for h4Tag in h4Tags:
            categoryData = {}
            try:
                categoryData['url'] = h4Tag.find_element_by_tag_name('a').get_attribute('href')
                categoryData['category'] = str(h4Tag.text)
                if count == 0:
                    categoryData['gender'] = 'Women'
                elif count == 1:
                    categoryData['gender'] = 'Men'
                else:
                    categoryData['gender'] = 'Kids'
                output.append(categoryData)
            except:
                continue
    count += 1

for categoryData in output:
    if categoryData['category'] != 'CLOTHING' and categoryData['category'] != 'ALL CLOTHING':
        continue
    driver.get(categoryData['url'])
    WebDriverWait(driver, 10)  # wait till below class appears
    try:
        leftNav = driver.find_element_by_id('leftNav')
    except:
        directlyById(categoryData)
        continue

    h4Tags = leftNav.find_elements_by_tag_name('h4')
    ulTags = leftNav.find_elements_by_tag_name('ul')
    count = 0
    for h4Tag in h4Tags:
        count += 1
        if h4Tag.text != 'Brands':
            continue
        ulTagsUrls = []
        for ulTag in leftNav.find_elements_by_tag_name('ul')[count:]:
            try:
                urlTemp = ulTag.find_element_by_tag_name('a').get_attribute('href')
                if 'http' not in urlTemp:
                    getBrandsWithoutLoad(categoryData, ulTag)
                    break
                ulTagsUrls.append(urlTemp)
            except:
                continue
        for ulTagsUrl in ulTagsUrls:
            categoryData['url'] = ulTagsUrl
            driver.get(categoryData['url'])
            WebDriverWait(driver, 10)  # wait till below class appears
            try:
                if 'Brands' not in str(driver.find_element_by_id('center').text):
                    continue
            except:
                continue

            linkElements = driver.find_element_by_id('indexBarHeader').find_elements_by_class_name('pagnLink')
            links = []
            for linkElement in linkElements:
                if linkElement.text >= 'A' and linkElement.text <= 'Z':
                    links.append(linkElement.find_element_by_tag_name('a').get_attribute('href'))
            for link in links:
                driver.get(link)
                categoryData['brands'] = ''
                brands = str(driver.find_element_by_id('refinementList').text).split('\n')
                for brand in driver.find_element_by_id('refinementList').find_elements_by_tag_name('li'):
                    brandName = str(brand.text)
                    first_brac = brandName.find('(')
                    brandName = brandName[:first_brac]
                    url = brand.find_element_by_tag_name('a').get_attribute('href')
                    categoryData['brands'] += brandName + '\n'
                    output1.append(
                        {'category': categoryData['category'], 'gender': categoryData['gender'], 'brand': brandName,
                         'url': url})
                    df = pd.DataFrame(output1)
                    # writing to a file
                    df.to_csv('brands.csv', index=False)
            break
        break

