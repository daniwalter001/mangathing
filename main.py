import bs4
import cfscrape
import os
import time


headers_g = {
    "Host": "mangas-origines.fr",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}


cf = cfscrape.create_scraper()


def clear():
    os.system('cls||clear')


def getInfos(node):

    list_manga_pic_node = node.select(
        "div.item-thumb.hover-details.c-image-hover > a")
    infos = {
        "name": list_manga_pic_node[0].attrs['title'],
        "link": list_manga_pic_node[0].attrs["href"]
    }
    return infos


def getMorePage(start=1, end=1):

    list = []
    url = "https://mangas-origines.fr/wp-admin/admin-ajax.php"

    headers_c = {
        "Host": "mangas-origines.fr",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "mangas-origines.fr",
        "Origin": "https://mangas-origines.fr",
        "Referer": "https://mangas-origines.fr/catalogue/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Alt-Used": "mangas-origines.fr",
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
            data["page"] = str(i)
            req = cf.post(url, data, headers=headers_c)
            print("Fetching page {}...\n ".format(str(i)))
            time.sleep(2)
            list.extend(getData(req))
    else:
        data["page"] = str(start)
        req = cf.post(url, data, headers=headers_c)
        print("Fetching page {}...".format(str(start)))
        list.extend(getData(req))

    return list


def getData(req):
    soup = bs4.BeautifulSoup(req.content, 'lxml')
    req_result = soup.select(
        "div.col-12.col-md-4.badge-pos-1 > div.page-item-detail.manga")

    list = []
    for node in req_result:
        list.append(getInfos(node))

    return list


def getCatalogue():
    link = "https://mangas-origines.fr/catalogue/"

    catalogue_request = cf.get(link, headers=headers_g)
    print("Getting Catalogue Default Content...")
    return getData(catalogue_request)

# ---------------------------------LET S GO------------------------


menu_options = {
    1: 'Get default Catalogue',
    2: 'Get Catalogue on a certain page',
    3: 'Get Catalogue on a certain range',
    4: 'Exit',
}


def print_menu():
    for key in menu_options.keys():
        print(key, '--', menu_options[key])


def option1():
    list = []
    list.extend(getCatalogue())
    for i, el in enumerate(list):
        print("{}- {}".format(i+1, el['name']))
    print('------')
    while(True):
        option1 = ''
        try:
            option1 = int(input('Enter your choice: '))
            if option1 == 0:
                clear()
                break
            elif option1 in range(1, len(list)+1):
                print(list[option1-1])
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
        list = []
        try:
            print("Enter 0 to exit")
            start = int(input("Which page? : "))
            if start == 0:
                break

            list.extend(getCatalogue())
            list.extend(getMorePage(start))

            for i, el in enumerate(list):
                print("{}- {}".format(i+1, el['name']))
            print('------')
            while(True):
                option1 = ''
                try:
                    option1 = int(input('Enter your choice: '))
                    if option1 == 0:
                        clear()
                        break
                    elif option1 in range(1, len(list)+1):
                        print(list[option1-1])
                    else:
                        print("You have {} elements displayed. You must know the range".format(
                            str(len(list))))
                except:
                    print('Wrong input. Please enter a number ...')
        except ValueError:
            print('Start and End must be integers\n')
            clear()
            continue


def option3():
    print("""
    * <<start>> and <<end>> is extrems of the range.
    *If <<end>> is not entered, the (start)th page catalogue will be 
    displayed
        
    """)

    while True:
        list = []
        try:
            print("Enter 0 to exit")
            start = int(input("Start: "))
            if start == 0:
                break
            end = int(input("End: "))

            list.extend(getCatalogue())
            list.extend(getMorePage(start, end))

            for i, el in enumerate(list):
                print("{}- {}".format(i+1, el['name']))
            print('------')
            while(True):
                option1 = ''
                try:
                    option1 = int(input('Enter your choice: '))
                    if option1 == 0:
                        clear()
                        break
                    elif option1 in range(1, len(list)+1):
                        print(list[option1-1])
                    else:
                        print("You have {} elements displayed. You must know the range".format(
                            str(len(list))))
                except:
                    print('Wrong input. Please enter a number ...')
        except ValueError:
            print('Start and End must be integers\n')
            clear()
            continue


if __name__ == "__main__":
    try:
        clear()

        while(True):
            print_menu()
            option = ''
            try:
                option = int(input('Enter your choice: '))
            except:
                print('Wrong input. Please enter a number ...')
            if option == 1:
                option1()
            elif option == 2:
                option2()
            elif option == 3:
                option3()
            elif option == 4:
                print('Bye...')
                exit()
            else:
                print('Invalid option. Please enter a number between 1 and 4.')

    except KeyboardInterrupt:
        print('\nProgram exited')
