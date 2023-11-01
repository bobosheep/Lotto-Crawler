import requests
from LottoBase import Lotto
from datetime import datetime
from bs4 import BeautifulSoup

class DailyCash(Lotto):
    def __init__(self):
        super().__init__('https://www.taiwanlottery.com.tw/lotto/DailyCash/history.aspx')
        self.default_filename = 'DailyCash.json'

    def crawlPage(self, year, month):
        print(f'Crawl {year}/{month}')

        if year < 103 or year > datetime.now().year or month < 1 or month > 12:
            return None

        res = requests.get(self.pageURL)
        soup = BeautifulSoup(res.text, 'html.parser')

        payload = {
            'D539Control_history1$chk': 'radYM',
            'D539Control_history1$dropYear': year,
            'D539Control_history1$dropMonth': month,
            'D539Control_history1$btnSubmit': '查詢'
        }
        payload["__VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
        payload["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        payload["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]

        res = requests.post(self.pageURL, data=payload)
        
        return res.text 

    def parse(self, html_body):
        if html_body == None  or type(html_body) != type(''):
            print(type(html_body))
            return
        data = BeautifulSoup(html_body, "html.parser")

        drawCount = len(data.select(".table_org.td_hm")) + len(data.select(".table_gre.td_hm"))

        for i in range(0, int(drawCount)):
            draw_numbers = []
            size_numbers = []

            drawID = data.select(f'#D539Control_history1_dlQuery_D539_DrawTerm_{i}')[0].text
            date = data.select(f'#D539Control_history1_dlQuery_D539_DDate_{i}')[0].text
            price = data.select(f'#D539Control_history1_dlQuery_D539_CategA1_{i}')[0].text

            for j in range(0, 5): # 5 numbers
                ballNums = data.select(f'#D539Control_history1_dlQuery_SNo{j + 1}_{i}')
                draw_numbers.append(ballNums[0].text)

                ballNums = data.select(f'#D539Control_history1_dlQuery_No{j + 1}_{i}')
                size_numbers.append(ballNums[0].text)
            
            # print(f'第 {drawID} 期, {date} 獎金 {price}， 號碼: {ballNums}') 

            self.draws[drawID] = {
                'draw'      : drawID,
                'date'      : date,
                'year'      : int(date.split('/')[0]),
                'month'     : int(date.split('/')[1]),
                'day'       : int(date.split('/')[2]),
                'price'     : price,
                'draw_order_nums'   : [int(n) for n in draw_numbers],
                'size_order_nums'   : [int(n) for n in size_numbers]
            }
            # print(self.draws[drawID])

if __name__ == "__main__":
    dailyCash = DailyCash()
    dailyCash.load()
    dailyCash.crawl()
    dailyCash.save()