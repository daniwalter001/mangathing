import bs4
import cfscrape


headers_g = {
    "Host": "mangas-origines.fr",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}

# vdisplay = Display(visible=0, size=(1024, 768))
# vdisplay.start() #to not display any browser
cf = cfscrape.create_scraper()


def getInfos(node):

    list_manga_pic_node = node.select(
        "div.item-thumb.hover-details.c-image-hover > a")
    infos = {
        "name": list_manga_pic_node[0].attrs['title'],
        "link": list_manga_pic_node[0].attrs["href"]
    }
    return infos


def getMore():
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
        "page": "3",
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
    req = cf.post(
        "https://mangas-origines.fr/wp-admin/admin-ajax.php", data, headers=headers_c)

    return req


def getCatalogue():

    link = "https://mangas-origines.fr/catalogue/"

    # btn btn-default load-ajax

    catalogue_request = cf.get(link, headers=headers_g)
    # print(catalogue_request.headers)
    catalogue_request = getMore()

    soup = bs4.BeautifulSoup(catalogue_request.content, 'lxml')
    req_result = soup.select(
        "div.col-12.col-md-4.badge-pos-1 > div.page-item-detail.manga")

    list = []
    for node in req_result:
        list.append(getInfos(node))

    for i in list:
        print(i)
    print("nbre d'elements:", len(list))


if __name__ == "__main__":
    getCatalogue()
