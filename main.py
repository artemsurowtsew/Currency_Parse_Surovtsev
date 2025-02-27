from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6 import uic
import sys
import requests
from bs4 import BeautifulSoup


urls = {
    "minfin": "https://minfin.com.ua/ua/company/ukrsibbank/currency/",
    "monobank": "https://api.monobank.ua/bank/currency",
    "privatbank": "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
}


def parse_minfin():
    response = requests.get(urls["minfin"])
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = {}


    allowed_currencies = ["USD", "EUR"]

    for row in soup.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) > 2:
            currency = columns[0].text.strip()


            if currency in allowed_currencies:
                buy_rate = columns[1].text.strip()
                sell_rate = columns[2].text.strip()
                rates[currency] = {"buy": buy_rate, "sell": sell_rate}

    return rates


def parse_monobank():
    response = requests.get(urls["monobank"])
    data = response.json()
    rates = {}

    allowed_currencies = {840: "USD", 978: "EUR"}

    for item in data:
        if item["currencyCodeA"] in allowed_currencies and item["currencyCodeB"] == 980:  # 980 - UAH
            currency = allowed_currencies[item["currencyCodeA"]]
            buy_rate = str(item.get("rateBuy", "N/A"))
            sell_rate = str(item.get("rateSell", "N/A"))
            rates[currency] = {"buy": buy_rate, "sell": sell_rate}

    return rates


def parse_privatbank():
    response = requests.get(urls["privatbank"])
    data = response.json()
    rates = {}
    for item in data:
        currency = item['ccy']
        buy_rate = item['buy']
        sell_rate = item['sale']
        rates[currency] = {"buy": buy_rate, "sell": sell_rate}
    return rates



def get_exchange_rates():
    rates = {}
    rates['minfin'] = parse_minfin()
    rates['monobank'] = parse_monobank()
    rates['privatbank'] = parse_privatbank()
    return rates


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)  # Load the .ui file


        self.table = self.tableWidget  # Reference the QTableWidget from the .ui file


        self.table.setRowCount(7)  # 7 rows
        self.table.setColumnCount(4)  # 4 columns (Source, Currency, Buy Rate, Sell Rate)

        # Set header labels
        self.table.setHorizontalHeaderLabels(['Source', 'Currency', 'Buy Rate', 'Sell Rate'])

        # Set up the button and connect it to the data loading function
        self.pushButton.clicked.connect(self.load_data)

    def load_data(self):
        # Get exchange rates from the websites
        exchange_rates = get_exchange_rates()


        data = []


        for source, rates in exchange_rates.items():
            for currency, rate in rates.items():
                buy_rate = rate['buy']
                sell_rate = rate['sell']
                data.append((source, currency, buy_rate, sell_rate))

        # Populate the table with the fetched data
        for row, (source, currency, buy_rate, sell_rate) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(source))
            self.table.setItem(row, 1, QTableWidgetItem(currency))
            self.table.setItem(row, 2, QTableWidgetItem(buy_rate))
            self.table.setItem(row, 3, QTableWidgetItem(sell_rate))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
