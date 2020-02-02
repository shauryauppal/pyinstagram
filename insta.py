from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep, strftime
from random import randint, shuffle
import pandas as pd
import pathlib
import logging
import argparse
import subprocess

logging.basicConfig(filename="pyinsta.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Instagram Credentials')
parser.add_argument('--userId', action='store', type=str, help='Instagram UserID', required=True)
parser.add_argument('--password', action='store', type=str, help='Instagram Password', required=True)
parser.add_argument('--headless', action='store', type=str, help='HeadlessFlag', required=False, default = 'True')
parser.add_argument('--remove_cache', action='store', type=str, help='RemoveCacheFlag', required=False, default = 'False')
args = parser.parse_args()

print("ARGS passed: {} {}".format(args.headless, args.remove_cache))

cachePath = "/Users/shaurya/Desktop/Shaurya/pyinstagram/cache"
if args.remove_cache == 'True':
    try:
        subprocess.run(["rm","-rf", cachePath])
    except Exception as e:
        print(e)
def login_code(cachePath, userId, password):
    global webdriver
    file = pathlib.Path(cachePath)
    flag = file.exists()
    chrome_options = Options()
    chromedriver_path = '/Users/shaurya/Desktop/Shaurya/pyinstagram/webdriver/chromedriver'
    chrome_options.add_argument('--user-data-dir={}'.format(cachePath))
    if args.headless == 'True':
        chrome_options.add_argument("--headless")
    webdriver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    sleep(2)
    print(flag)
    if flag == False:
        print('Cache Doesnot exist')
        webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)
        webdriver.maximize_window()
        logger.info("Not Cached: Instagram Site Open")

        username = webdriver.find_element_by_name('username')
        username.send_keys(userId)
        p_word = webdriver.find_element_by_name('password')
        p_word.send_keys(password)
        logger.info("Id {}, Password Entered".format(userId))

        button_login = webdriver.find_element_by_css_selector(
            '#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(4)')
        button_login.click()
        sleep(3)
    else:
        webdriver.get('https://www.instagram.com')
        sleep(3)
        webdriver.maximize_window()
        logger.info("Cached: Instagram Site Open")

    return webdriver

def master_code(webdriver, hashtag_list, iteration_ct):
        try:
            notnow = webdriver.find_element_by_css_selector(
                'body > div.RnEpo.Yx5HN > div > div > div.mt3GC > button.aOOlW.HoLwm')
            notnow.click()  # comment these last 2 lines out, if you don't get a pop up asking about notifications
        except:
            pass

        prev_user_list = []  # if it's the first time you run it, use this line and comment the two below
        # prev_user_list = pd.read_csv('20181203-224633_users_followed_list.csv', delimiter=',').iloc[:,1:2] # useful to build a user log
        # prev_user_list = list(prev_user_list['0'])

        new_followed = []
        tag = -1
        followed = 0
        likes = 0
        comments = 0

        for hashtag in hashtag_list:
            tag += 1
            webdriver.get('https://www.instagram.com/explore/tags/' + hashtag_list[tag] + '/')
            sleep(5)
            first_thumbnail = webdriver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')

            first_thumbnail.click()
            sleep(randint(1, 2))
            # try:
            for x in range(1, iteration_ct):
                try:
                    username = webdriver.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text

                    if username not in prev_user_list:
                        # If we already follow, do not unfollow | go in loop based on probability
                        follow_prob = randint(1, 10)
                        if webdriver.find_element_by_xpath(
                                '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').text == 'Follow' and follow_prob > 3:

                            if randint(1,10) > 4: # follow probability
                                webdriver.find_element_by_xpath(
                                    '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').click()
                                new_followed.append(username)
                                followed += 1

                            # Liking the picture
                            button_like = webdriver.find_element_by_css_selector(
                                'body > div._2dDPU.vCf6V > div.zZYga > div > article > div.eo2As > section.ltpMr.Slqrh > span.fr66n > button > svg')

                            button_like.click()
                            likes += 1
                            sleep(randint(18, 25))

                            # Comments and tracker
                            comm_prob = randint(1, 10)
                            print('{}_{}: {}'.format(hashtag, x, comm_prob))
                            if comm_prob > 4:
                                comments += 1
                                webdriver.find_element_by_xpath(
                                    '/html/body/div[4]/div[2]/div/article/div[2]/section[3]').click()
                                comment_box = webdriver.find_element_by_xpath(
                                    '/html/body/div[4]/div[2]/div/article/div[2]/section[3]/div/form/textarea')
                                comment_list = ['Really Cool!', 'Nice work :)', 'Nice gallery!!', 'So cool! :)',
                                                'Great Click']
                                comment_box.send_keys(comment_list[int(comm_prob % len(comment_list))])
                                # Enter to post comment
                                comment_box.send_keys(Keys.ENTER)
                                sleep(randint(22, 28))
                        # Next picture
                        webdriver.find_element_by_link_text('Next').click()
                        sleep(randint(25, 29))
                    else:
                        webdriver.find_element_by_link_text('Next').click()
                        sleep(randint(20, 26))
                except:
                    pass
        for n in range(0, len(new_followed)):
            prev_user_list.append(new_followed[n])

        updated_user_df = pd.DataFrame(prev_user_list)
        updated_user_df.to_csv('{}_users_followed_list.csv'.format(strftime("%Y%m%d-%H%M%S")))
        print('Liked {} photos.'.format(likes))
        print('Commented {} photos.'.format(comments))
        print('Followed {} new people.'.format(followed))
        return [likes, comments, followed]

def follow_person(followlink, browser, follow_count):
    browser.get(followlink)
    sleep(3)
    x = randint(1,10)
    if x%2==0:
        browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()
    else:
        browser.find_element_by_css_selector('#react-root > section > main > div > header > section > ul > li:nth-child(2) > a').click()
    sleep(4)
    for i in range(1,follow_count):
        try:
            path = "body > div.RnEpo.Yx5HN > div > div.isgrP > ul > div > li:nth-child({}) > div > div.Igw0E.rBNOH.YBx95.ybXk5._4EzTm.soMvl > button".format(i)
            button = browser.find_element_by_css_selector(path)
            if button.text == "Follow":
                button.click()
            else:
                pass
            sleep(randint(10, 26))
        except:
            sleep(randint(20, 35))

webdriver = login_code(cachePath, args.userId, args.password)

likes = 0
comments = 0
followed = 0

hashtag_list = ['eating', 'hungry', 'delhifood', 'foods', 'burger', 'eat', 'delhifoodie', 'delhifoodblogger', 'foodpics', 'indianfood', 'foodtalkindia', 'foodgasm', 'dessert', 'bacon', 'tasty', 'cheese', 'icecream', 'delish', 'dinner', 'yum', 'foodmaniacindia', 'ifoundawesome', 'chocolate', 'lunch', 'indiancuisine', 'burgerporn', 'sodelhi', 'delhidiaries', 'delhi_igers', 'foodinstagram', 'delhifoodguide', 'dfordelhi', 'cheeseburger', 'foodlover', 'pizza', 'desserts', 'hamburger', 'instadelhi', 'burgers', 'dessertporn', 'delhihai', 'beef', 'saadidilli', 'cheesy', 'sweettooth', 'cupcake', 'meat', 'delhiwale', 'delhigram', 'fries', 'desifood', 'foodpic', 'streetfood', 'fruit', 'burgertime', 'videos', 'cake', 'gelato', 'tutorial', 'mozzarella', 'instaburger', 'tomato', 'indiagram', 'italianfood', 'indianfoodbloggers', 'inlove', 'pasta', 'fresh', 'eggs', 'bread', 'parmesan', 'delhincr', 'cheddar', 'burgerlovers', 'fooddiaries', 'southindianfood', 'indiancooking', 'nutella', 'breakfast', 'icecreamlover', 'sweets', 'mumbaifoodie', 'fastfood', 'mumbaifood', 'northindian', 'tasteofindia', 'southindian', 'curry', 'strawberry', '아이스크림', 'ice', 'foodphotography', 'delhiblogger', 'vanilla', 'bestburger','burguer', 'softserve', 'cookies', 'nomnom', 'cheatmeal', 'foodblogger', 'burgerlove', 'eeeeeats', 'hamburguesa', 'アイスクリーム', 'foodbeast', 'cooking', 'homemade', 'bbq', 'helado', 'foodphoto', 'fo', 'foodlovers', 'pommes', 'grill', 'burgraphy', 'delhi', 'steak', 'eatfamous', 'frenchfries', 'zomato', 'foodtruck', 'innout', 'burgerlife', 'shareyourburger']
shuffle(hashtag_list)
try:
    status1 = master_code(webdriver, hashtag_list[:5], randint(15, 42))
except Exception as e:
    print(e)
    sleep(10000)
    pass

profile_list = ['onmytable_5', 'diggin_sleep_repeat','forkkintheroad_','foodzpah','spiceitupwithsam','thegreatindianfoodie']
shuffle(profile_list)
try:
    followlink = "https://www.instagram.com/{}/".format(profile_list[0])
    follow_person(followlink, webdriver, randint(13,20))
except Exception as e:
    print(e)
    sleep(10000)
    pass

try:
    status2 = master_code(webdriver, hashtag_list[-5:],randint(10, 36))
except Exception as e:
    print(e)
    sleep(10000)
    pass

likes = status1[0] + status2[0]
comments = status1[1] + status2[1]
followed = status1[2] + status2[2] + randint(13,20)
subprocess.run(["sh", "-c", "osascript -e 'display notification \"%s\" with title \"%s\"'" % ('Instagram BOT Complete', 'Time Taken {} Likes {} Follow {}'.format(likes, comments, followed))])
webdriver.close()
