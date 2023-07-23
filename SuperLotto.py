import requests
from LottoBase import Lotto
from bs4 import BeautifulSoup
from datetime import datetime

class SuperLotto(Lotto):
    def __init__(self):
        super().__init__('https://www.taiwanlottery.com.tw/lotto/superlotto638/history.aspx')
        self.default_filename = 'SuperLotto.json'

    def crawlPage(self, year, month):
        print(f'Crawl {year}/{month}')

        if year < 103 or year > datetime.now().year or month < 1 or month > 12:
            return None

        res = requests.get(self.pageURL)
        soup = BeautifulSoup(res.text, 'html.parser')

        payload = {
            'SuperLotto638Control_history1$chk': 'radYM',
            'SuperLotto638Control_history1$dropYear': year,
            'SuperLotto638Control_history1$dropMonth': month,
            'SuperLotto638Control_history1$btnSubmit': '查詢'
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

        drawCount = len(data.select(".td_w.font_red14b_center")) / 2

        for i in range(0, int(drawCount)):
            draw_numbers = []
            size_numbers = []

            drawID = data.select(f'#SuperLotto638Control_history1_dlQuery_DrawTerm_{i}')[0].text
            date = data.select(f'#SuperLotto638Control_history1_dlQuery_Date_{i}')[0].text
            price = data.select(f'#SuperLotto638Control_history1_dlQuery_Total_{i}')[0].text
            specialNum = data.select(f'#SuperLotto638Control_history1_dlQuery_No7_{i}')[0].text

            for j in range(0, 6): # 6 numbers
                ballNums = data.select(f'#SuperLotto638Control_history1_dlQuery_SNo{j + 1}_{i}')
                draw_numbers.append(ballNums[0].text)

                ballNums = data.select(f'#SuperLotto638Control_history1_dlQuery_No{j + 1}_{i}')
                size_numbers.append(ballNums[0].text)
            
            # print(f'第 {drawID} 期, {date} 獎金 {price}， 號碼: {numbers}，特別號: {specialNum}')

            self.draws[drawID] = {
                'draw'      : drawID,
                'date'      : date,
                'year'      : int(date.split('/')[0]),
                'month'     : int(date.split('/')[1]),
                'day'       : int(date.split('/')[2]),
                'price'     : price,
                'draw_order_nums'   : [int(n) for n in draw_numbers],
                'size_order_nums'   : [int(n) for n in size_numbers],
                'bonus_num':  int(specialNum)
            }

            # print(self.draws[drawID])

if __name__ == "__main__":
    superLotto = SuperLotto()
    superLotto.load()
    superLotto.crawl()
    superLotto.save()