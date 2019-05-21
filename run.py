import requests
import re

from bs4 import BeautifulSoup
from http.cookies import SimpleCookie

id_ = ""
authkey_ = ""
torrent_pass_ = ""
cookies_ = ''''''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 ",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"
}


class Snatchlist:
    def __init__(self, cookie, user_id, authkey, torrent_pass):
        self.cookie = self.cookies_raw2jar(cookie)
        self.id = user_id
        self.authkey = authkey
        self.torrent_pass = torrent_pass
        self.key = "&authkey={authkey}&torrent_pass={t_pass}".format(
            authkey=self.authkey,
            t_pass=self.torrent_pass
        )

    def get_page(self, page):
        url = "https://broadcasthe.net/snatchlist.php?type=ajax&id=" + self.id + "&sort=fid&page=" + page
        try:
            response = requests.request("GET", url, headers=headers, cookies=self.cookie, timeout=5)
        except TimeoutError:
            print("Request Timeout!")
        else:
            return response.text
    
    @staticmethod
    def extract_torrent(html):
        soup = BeautifulSoup(html, "lxml")
        table = soup.find_all('table')[2]

        inactive_row = []
        simple_table = []
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            status = row.find_all('td')[6].get_text()
            if status == "Inactive":
                for column in columns:
                    a = column.find_all("a")
                    if a and a[0]['href'] != "javascript:void(0);":
                        try:
                            e = column.find_all("a")[1]["href"]
                        except IndexError:
                            pass
                        else:
                            inactive_row.append(e)
                            inactive_row.append(status)
                    if inactive_row:
                        simple_table.append(inactive_row)
                    inactive_row = []
            else:
                continue
        return simple_table

    def get_link(self, table):
        base_url = "https://broadcasthe.net/torrents.php?action=download&id={tid}"
        regex = r"torrentid=(?P<tid>\d.*)"
        download_url = list()

        for item in table:
            test_str = item[0]
            matches = re.search(regex, test_str, re.MULTILINE)
            url = base_url.format(tid=matches.group("tid"))
            download_url.append(url+self.key)

        return download_url

    def out(self, page):
        html_ = self.get_page(page)
        table_ = self.extract_torrent(html_)
        return self.get_link(table_)

    @staticmethod
    def cookies_raw2jar(raw):
        if not raw:
            raise ValueError("The Cookies is not allowed to be empty.")

        cookie = SimpleCookie(raw)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies


s = Snatchlist(cookies_, id_, authkey_, torrent_pass_)
# Get Inactive torrents url from page 1 to page 198
for page_ in range(1, 119):
    p = s.out(str(page_))
    for item_ in p:
        print(item_)
