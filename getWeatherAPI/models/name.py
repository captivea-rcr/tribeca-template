# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.


from odoo.models import *
from datetime import datetime
import requests
_logger = logging.getLogger(__name__)

class weatherModule(Model):
    @api.model
    def getWeather(self,zipcode,date_time=None):
        # Enter your API key here
        api_key = "4a8319f9023e1cbf1f38ed381b532dd7"
        if date_time:
            if datetime.now().date()>date_time.date():return "Invalid date"
            # base_url variable to store url
            base_url = "http://api.openweathermap.org/data/2.5/forecast?"
        else:
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
        # complete url address
        complete_url = base_url + "appid=" + api_key + "&zip=" + str(zipcode)+',us'+"&lang=en"
        # get method of requests module
        # return response object
        response = requests.get(complete_url)
        json_data = response.json()
        if json_data['cod']!=200:return "Not Found"
        if date_time:
            location_data = {
                'city': json_data['city']['name'],
                'country': json_data['city']['country']
            }
            json_data['list'].sort(key=lambda x:abs(datetime.strptime(x['dt_txt'],'%Y-%m-%d %X')-date_time))
            item = json_data['list'][0]
            time = item['dt_txt']
        else:
            item=json_data
            time=datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %X')
            location_data = {
                'city': item['name'],
                'country': item['sys']['country']
            }
        # Temperature is measured in Kelvin
        temperature = item['main']['temp']
        temperature= '%.2f' % (temperature * 9/5 - 459.67)+'°F'
        weather = item['weather'][0]['main']
        description = item['weather'][0]['description']
        return {"Time":time,"Weather":weather,"Description":description,"Temperature":temperature,"Location":location_data}
