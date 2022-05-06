from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from lxml import html
import requests
import configparser


class CommandHandlerService:
    @staticmethod
    def rate(update: Update, context: CallbackContext) -> None:
        exchange_rate = ExchangeRate()
        update.message.reply_text(f'Курс ЦБ: {exchange_rate.CB_USD_RUB} \n'
                                  f'Курс Aliexpress: {exchange_rate.ALI_USD_RUB}')


class Properties:
    BOT_TOKEN = ""
    URL_PRODUCT = ""
    __initialized = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Properties, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if self.__initialized: return

        config = configparser.ConfigParser()
        config.read('config/default_config.ini')
        config.read('config/my_config.ini')
        self.BOT_TOKEN = config.get('DEFAULT', 'BOT_TOKEN')
        self.URL_PRODUCT = config.get('DEFAULT', 'URL_PRODUCT')

        if self.BOT_TOKEN == "":
            raise RuntimeError('Incorrect value "BOT_TOKEN" in config')
        if self.URL_PRODUCT == "":
            raise RuntimeError('Incorrect value "URL_PRODUCT" in config')

        self.__initialized = True


class ExchangeRate:
    CB_USD_RUB = 0.0
    ALI_USD_RUB = 0.0

    def __init__(self):
        self.CB_USD_RUB = self.get_cb_usd_rub()
        self.ALI_USD_RUB = self.get_ali_usd_rub()

    @staticmethod
    def get_cb_usd_rub():
        return round(requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()['Valute']['USD']['Value'], 2)

    @staticmethod
    def get_ali_usd_rub():
        URL_PRODUCT = Properties().URL_PRODUCT
        XPATH_EXPRESSION = '//span[contains(@class, "product-price-current")]'

        cookies = {'aep_usuc_f': 'c_tp=USD'}
        tree = html.fromstring(requests.get(URL_PRODUCT, cookies=cookies).text)
        usd_price_text = tree.xpath(XPATH_EXPRESSION)[0].text
        usd_price = float(usd_price_text.split(" ")[1].replace("$", ""))

        cookies = {'aep_usuc_f': 'c_tp=RUB'}
        tree = html.fromstring(requests.get(URL_PRODUCT, cookies=cookies).text)
        rub_price_text = tree.xpath(XPATH_EXPRESSION)[0].text
        rub_price = float(rub_price_text.split(" ")[0].replace(",", "."))
        return round(rub_price / usd_price, 2)


if __name__ == '__main__':

    updater = Updater(Properties().BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('rate', CommandHandlerService.rate))

    updater.start_polling()
    updater.idle()
