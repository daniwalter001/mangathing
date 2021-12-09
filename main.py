import bs4
import cfscrape
import time
import json
import os

host = ''

host = "mangas-origines.fr"
# host = "x.mangas-origines.fr"

headers_g = {
    "Host": host,
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}


cf = cfscrape.create_scraper()


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

    if start >= 0 and end and start < end:
        for i in range(start, end+1):
            data["page"] = str(i-1)
            req = cf.post(url, data, headers=headers_c)
            print("Fetching page {}...".format(str(i)))
            time.sleep(2)
            list_.extend(get_data(req))
    else:
        data["page"] = str(start-1)
        req = cf.post(url, data, headers=headers_c)
        print("Fetching page {}...".format(str(start)))
        list_.extend(get_data(req))
        list_.extend(get_search_data(req))

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

    catalogue_request = cf.get(link, headers=headers_g)
    print("Getting Catalogue Default Content...")
    return get_data(catalogue_request)


def search(keyword):
    link = "https://mangas-origines.fr/wp-admin/admin-ajax.php"
    request = cf.post(
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
    while True:
        data_["page"] = str(i)
        data_["vars[s]"] = str(keyword)
        data_["vars[meta_query][0][s]"] = str(keyword)
        time.sleep(2)
        req = cf.post(url, data_, headers=headers_c)
        print("Fetching page {}...".format(str(i+1)))
        time.sleep(2)
        list_temp = get_search_data(req)

        if len(list_temp) != 0:
            list_.extend(get_search_data(req))
            # print(get_search_data(req))
            i = i+1
        else:
            break
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


def download(data):
    pass


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
                    option = int(input('Enter your choice: '))
                    if int(option) == 0:
                        clear()
                        break
                    elif int(option) in range(1, len(chapters)+1):
                        print(chapters[option-1])
                    else:
                        print("You have {} elements displayed. You must know the range".format(
                            str(len(chapters))))
                except:
                    print('Wrong input. Please enter a number ...')
    return inner


@select_chapter
def get_chapters(data):
    list_ = []
    try:
        link = data["link"]
        name = data["name"]

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
    2: 'Get Catalogue on a certain page',
    3: 'Get Catalogue on a certain range',
    4: 'Looking for a certain scan',
    5: 'Looking for a certain scan - Deep Search',
    6: 'Exit',
}


def print_menu():
    for key in menu_options.keys():
        print(key, '--', menu_options[key])


def option1():
    list_ = []
    list_.extend(get_catalogue())
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
                print(list_[option1-1])
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
                        print(list_[option1-1])
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
                        print(list_[option1-1])
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
                    # print(search_results[option-1])
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


if __name__ == "__main__":
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
            elif option == 6 or option == 0:
                print('Bye...')
                print('Bye...')
                exit()
            else:
                print('Invalid option. Please enter a number between 1 and 4.')

    except KeyboardInterrupt:
        print('\nProgram exited')
