

from posixpath import join
import bs4
import cfscrape
import time
import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import pickle


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


host = ''
history = None

#host = "mangas-origines.fr"
host = "x.mangas-origines.fr"

current_manga = ""
current_chapter = ""
home = os.getenv("HOME")
root_dir = os.path.join(home, "Mangas")
history_path = os.path.join(root_dir, "history")

if not os.path.exists(root_dir):
    os.mkdir(root_dir)

if os.path.exists(history_path):
    with open(history_path, 'rb') as f:
        history = pickle.load(f)
else:
    history = []


headers_g = {
    "Host": host,
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}

cf2 = requests_retry_session(session=cfscrape.create_scraper())


def clear():
    os.system('cls||clear')


def get_infos(node):

    list_manga_pic_node = node.select(
        "div.item-thumb.hover-details.c-image-hover > a")
    infos = {
        "name": list_manga_pic_node[0].attrs['title'],
        "link": list_manga_pic_node[0].attrs["href"]
    }
    return infos


def get_search_result_infos(node):
    list_manga_pic_node = node.select(
        "div.tab-thumb.c-image-hover > a")
    infos = {
        "name": list_manga_pic_node[0].attrs['title'],
        "link": list_manga_pic_node[0].attrs["href"]
    }
    return infos


def get_more_page(start=1, end=1):

    list_ = []
    url = "https://"+host+"/wp-admin/admin-ajax.php"

    headers_c = {
        "Host": host,
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": host,
        "Referer": "https://"+host+"/catalogue/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Alt-Used": host,
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "action": "madara_load_more",
        # "page": str(start),
        "template":	"madara-core/content/content-archive",
        "vars[paged]": "1",
        "vars[orderby]": "meta_value_num",
        "vars[template]": "archive",
        "vars[sidebar]": "full",
        "vars[post_type]": "wp-manga",
        'vars[post_status]': "publish",
        'vars[meta_key]': "_latest_update",
        'vars[order]': "desc",
        'vars[meta_query][0][0][key]': "manga_adult_content",
        'vars[meta_query][0][0][value]': "",
        'vars[meta_query][0][s]': "ka",
        'vars[meta_query][0][paged]': "1",
        'vars[meta_query][0][orderby]': "meta_value_num",
        'vars[meta_query][0][template]': "archive",
        'vars[meta_query][0][sidebar]': "full",
        'vars[meta_query][0][post_type]': "wp-manga",
        'vars[meta_query][0][post_status]': "publish",
        'vars[meta_query][0][meta_key]': "_latest_update",
        'vars[meta_query][0][order]': "desc",
        'vars[meta_query][relation]': "AND",
        'vars[manga_archives_item_layout]': "default"
    }

    cf_ = cfscrape.create_scraper()

    if start >= 0 and end and start < end:
        for i in range(start, end+1):
            data["page"] = str(i-1)
            req = cf_.post(url, data, headers=headers_c)
            print("Fetching page {}...".format(str(i)))
            time.sleep(2)
            list_.extend(get_data(req))
    else:
        data["page"] = str(start-1)
        req = cf_.post(url, data, headers=headers_c)
        print("Fetching page {}...".format(str(start)))
        list_.extend(get_data(req))
        list_.extend(get_search_data(req))
    cf_.close()
    return list_


def get_data(req):
    soup = bs4.BeautifulSoup(req.content, 'lxml')
    req_result = soup.select(
        "div.col-12.col-md-4.badge-pos-1 > div.page-item-detail.manga")
    list_ = []
    for node in req_result:
        list_.append(get_infos(node))

    return list_


def get_search_data(req):
    soup = bs4.BeautifulSoup(req.content, 'lxml')
    req_result = soup.select(
        "div.row.c-tabs-item__content")

    list_ = []
    for node in req_result:
        list_.append(get_search_result_infos(node))

    return list_


def get_catalogue():
    link = "https://"+host+"/catalogue/"
    cf_ = cfscrape.create_scraper()
    catalogue_request = cf_.get(link, headers=headers_g)
    print("Getting Catalogue Default Content...")
    cf_.close()
    return get_data(catalogue_request)


def search(keyword):
    link = "https://mangas-origines.fr/wp-admin/admin-ajax.php"
    cf_ = cfscrape.create_scraper()
    request = cf_.post(
        link, {"action": "wp-manga-search-manga", "title": str(keyword)}, headers=headers_g)
    res = json.loads(request.content)['data']
    list_ = []

    for item in res:
        if item:
            try:
                item["error"]
                print(item["message"])
                break
            except KeyError:
                list_.append(
                    {
                        "name": item['title'],
                        "link": item['url']
                    }
                )
    cf_.close()
    return list_


def deep_search(keyword=''):
    list_ = []
    url = "https://"+host+"/wp-admin/admin-ajax.php"

    headers_c = {
        "Host": host,
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": host,
        "Referer": "https://"+host+"/catalogue/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Alt-Used": host,
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data_ = {
        "action":	"madara_load_more",
        "template":	"madara-core/content/content-search",
        "vars[orderby]":	"",
        "vars[paged]": "1",
        "vars[template]":	"search",
        "vars[meta_query][0][0][key]":	"manga_adult_content",
        "vars[meta_query][0][0][value]":	"",
        "vars[meta_query][0][orderby]":	"",
        "vars[meta_query][0][paged]": "1",
        'vars[meta_query][0][template]': "search",
        "vars[meta_query][0][meta_query][relation]":	"AND",
        "vars[meta_query][0][post_type]":	"wp-manga",
        "vars[meta_query][0][post_status]": "publish",
        "vars[meta_query][relation]":	"AND",
        "vars[post_type]":	"wp-manga",
        "vars[post_status]": "publish",
        "vars[manga_archives_item_layout]":	"default",
    }

    i = 0
    cf_ = cfscrape.create_scraper()

    while True:
        data_["page"] = str(i)
        data_["vars[s]"] = str(keyword)
        data_["vars[meta_query][0][s]"] = str(keyword)
        time.sleep(2)
        req = cf_.post(url, data_, headers=headers_c)
        print("Fetching page {}...".format(str(i+1)))
        time.sleep(2)
        list_temp = get_search_data(req)

        if len(list_temp) != 0:
            list_.extend(get_search_data(req))
            # print(get_search_data(req))
            i = i+1
        else:
            break
    cf_.close()
    return list_


def get_chapters_data(node):

    chapter_data_node = node.select("a")
    # print(chapter_data_node)
    a = "abc"
    infos = {
        "name": chapter_data_node[0].get_text().strip("\n"),
        # "name": chapter_data_node[0].attrs['title'],
        "link": chapter_data_node[0].attrs['href']
    }

    return infos


def get_pages_link(request):

    soup = bs4.BeautifulSoup(request.content, "lxml")
    pages_nodes = soup.select("img.wp-manga-chapter-img")
    list_ = []
    for el in pages_nodes:
        page = {
            "name": el.attrs['data-src'].split("/")[-1],
            "link": el.attrs['data-src'].strip()
        }
        list_.append(page)
    return list_


def size_to_KB(size):
    print(size)
    return True


def download(data):
    current_chapter = data["name"]
    link = "{}?style=list".format(data["link"])
    cf_ = cfscrape.create_scraper()
    request = cf_.get(link)
    pages = get_pages_link(request)
    current_chapter_path = os.path.join(
        root_dir, current_manga, current_chapter)
    if not os.path.exists(current_chapter_path):
        os.makedirs(current_chapter_path)

    count = 0
    print(current_manga)
    print(current_chapter)

    for el in pages:
        current_file_path = os.path.join(
            root_dir, current_manga, current_chapter, el['name'])
        try:
            file = cf2.get(el["link"], headers=headers_g, timeout=5)
            if file.status_code == 200:
                # file.raw.decode_content = True
                if (not os.path.exists(current_file_path)):
                    with open(current_file_path, 'wb') as f:
                        # shutil.copyfileobj(file.raw, f)
                        f.write(file.content)
                else:
                    print("{}...".format(el['name']), end='')
                    print("pass")
                    continue

                print("{}...".format(el['name']), end='')
                print("ok")
                count = count+1
            else:
                print("{}...".format(el['name']), end='')
                print("failed")

        except Exception as x:
            print('It failed :(', x.__class__.__name__)
            continue
        # else:
            # print('It eventually worked', file.status_code)

    print("Download complete: {}/{}\n".format(count, len(pages)))
    cf_.close()
    return None


def select_chapter(func):
    def inner(data):
        chapters = func(data)

        if len(chapters) != 0:
            for i, chapter in enumerate(chapters):
                print("{}- {}".format(str(i+1).zfill(3), chapter['name']))
            print('-----')
            while(True):
                option = ''
                try:
                    print("""
* 'a b' to download a range from a to b chapters
* 'a' to download ath chapter
* 'all' to download all chapter
                    """)
                    option = input('Enter your choice: ')
                    if str(option) == "0":
                        clear()
                        break
                    elif option == "all":
                        for el in chapters:
                            download(el)
                            break
                    else:
                        start = 1
                        end = 1
                        try:
                            list_option = option.split(" ")
                            if len(list_option) != 0:
                                start = int(list_option[0])
                                end = int(list_option[-1])
                                for i in range(start, end+1):
                                    print("ok")
                                    # download(chapters[i])
                                    if i in range(1, len(chapters)+1):
                                        download(chapters[i-1])
                                        continue
                                    else:
                                        print("{}th element is not in the range".format(
                                            str(len(chapters))))
                                        break
                            else:
                                print("Invalid entry")
                        except ValueError:
                            clear()
                            print("Follow what is written please !")

                except ValueError:
                    print('Wrong input. Please enter a number ...')
    return inner


@ select_chapter
def get_chapters(data):
    global current_manga
    list_ = []
    cf = cfscrape.create_scraper()
    history.append(data)
    try:
        link = data["link"]
        current_manga = data["name"]

        req = cf.post(link+"ajax/chapters/", {}, headers=headers_g)
        soup = bs4.BeautifulSoup(req.content, 'lxml')
        req_result = soup.select(
            "li.wp-manga-chapter")
        for node in req_result:
            list_.append(get_chapters_data(node))

    except KeyError:
        print("Données invalides")

    list_.reverse()

    return list_


# ---------------------------------LET S GO------------------------
menu_options = {
    1: 'Get default Catalogue',
    2: 'Get Catalogue on a certain page of the catalogue',
    3: 'Get Catalogue on a certain range of pages',
    4: 'Looking for a certain scan',
    5: 'Looking for a certain scan - Deep Search',
    6: 'History',
    7: 'Exit',
}


def print_menu():
    for key in menu_options.keys():
        print(key, '--', menu_options[key])


def option1():
    list_ = []
    list_.extend(get_catalogue())
    while(True):
        for i, el in enumerate(list_):
            print("{}- {}".format(i+1, el['name']))
        print('------')
        option1 = ''
        try:
            option1 = int(input('Enter your choice: '))
            if option1 == 0:
                clear()
                break
            elif option1 in range(1, len(list_)+1):
                get_chapters(list_[option1-1])
        except:
            print('Wrong input. Please enter a number ...')


def option2():

    print("""
    * Enter the page's catalogue you want to be displayed.
    * If not entered, the first page catalogue will be
      displayed

    """)

    start = 1

    while True:
        list_ = []
        try:
            print("Enter 0 to exit")
            start = int(input("Which page? : "))
            if start == 0:
                break

            # list_.extend(get_catalogue())
            list_.extend(get_more_page(start))

            for i, el in enumerate(list_):
                print("{}- {}".format(i+1, el['name']))
            print('------')
            while(True):
                option1 = ''
                try:
                    option1 = int(input('Enter your choice: '))
                    if option1 == 0:
                        clear()
                        break
                    elif option1 in range(1, len(list_)+1):
                        get_chapters(list_[option1-1])
                    else:
                        print("You have {} elements displayed. You must know the range".format(
                            str(len(list_))))
                except:
                    print('Wrong input. Please enter a number ...')
        except ValueError:
            print('Start and End must be integers\n')
            clear()
            continue


def option3():
    print("""
    *<<Start>> and <<end>> is extrems of the range.
    *If <<End>> is not entered, the (start)th page catalogue will be
    displayed

    """)

    while True:
        list_ = []
        try:
            print("Enter 0 to exit")
            start = int(input("Start: "))
            if start == 0:
                break
            end = int(input("End: "))

            # list_.extend(get_catalogue())
            list_.extend(get_more_page(start, end))

            for i, el in enumerate(list_):
                print("{}- {}".format(i+1, el['name']))
            print('------')
            while(True):
                option1 = ''
                try:
                    option1 = int(input('Enter your choice: '))
                    if option1 == 0:
                        clear()
                        break
                    elif option1 in range(1, len(list_)+1):
                        get_chapters(list_[option1-1])
                    else:
                        print("You have {} elements displayed. You must know the range".format(
                            str(len(list_))))
                except:
                    print('Wrong input. Please enter a number ...')
        except ValueError:
            print('Start and End must be integers\n')
            clear()
            continue


def option4():
    clear()
    print("U want to search? Interesting...\n")
    while True:
        # clear()
        print("Enter 0 to quit")
        keyword = str(input("Enter the keyword: "))
        if keyword == str(0):
            clear()
            break
        if keyword == 'clear':
            clear()
            continue
        print("Results for {}...".format(keyword))
        search_results = search(str(keyword))

        while True:
            for i, el in enumerate(search_results):
                print("{}- {}".format(i+1, el["name"]))

            print('------')
            option = ''
            try:
                print("Enter 0 to back")
                option = int(input('Enter your choice: '))
                if option == 0:
                    clear()
                    break
                elif option in range(1, len(search_results)+1):
                    get_chapters(search_results[option-1])
                else:
                    print("You have {} elements displayed. You must know the range".format(
                        str(len(search_results))))
            except ValueError:
                print('Wrong input. Please enter a number ...')


def option5():
    clear()
    print("U want to search? Interesting...\n")
    while True:
        # clear()
        print("Enter 0 to quit")
        keyword = str(input("Enter the keyword: "))
        if keyword == str(0):
            clear()
            break
        if keyword == 'clear':
            clear()
            continue
        print("Results for {}...".format(keyword))

        search_results = deep_search(str(keyword))

        while True:
            for i, el in enumerate(search_results):
                print("{}- {}".format(i+1, el["name"]))

            print('------')
            option = ''
            try:
                print("Enter 0 to back")
                option = int(input('Enter your choice: '))
                if option == 0:
                    clear()
                    break
                elif option in range(1, len(search_results)+1):
                    get_chapters(search_results[option-1])
                else:
                    print("You have {} elements displayed. You must know the range".format(
                        str(len(search_results))))
            except ValueError:
                print('Wrong input. Please enter a number ...')


def option6():
    while True:
        for i, el in enumerate(history[:30]):
            print("{}- {}".format(i+1, el["name"]))

        print('------')
        option = ''
        try:
            print("Enter 0 to back")
            option = int(input('Enter your choice: '))
            if option == 0:
                clear()
                break
            elif option in range(1, len(history)+1):
                get_chapters(history[option-1])
            else:
                print("You have {} elements displayed. You must know the range".format(
                    str(len(history))))
        except ValueError:
            print('Wrong input. Please enter a number ...')


def origin():
    try:
        clear()

        while(True):
            print_menu()
            option = ''
            try:
                option = int(input('Enter your choice: '))
                clear()
            except:
                print('Wrong input. Please enter a number ...')
            if option == 1:
                option1()
            elif option == 2:
                option2()
            elif option == 3:
                option3()
            elif option == 4:
                option4()
            elif option == 5:
                option5()
            elif option == 6:
                option6()
            elif option == 7 or option == 0:
                print("Saving history...\n", end="")
                with open(history_path, 'wb') as f:
                    pickle.dump(history, f)
                break
            else:
                print('Invalid option. Please enter a number between 1 and 4.')

    except KeyboardInterrupt:
        print('\nProgram exited')
