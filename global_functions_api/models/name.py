# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.


from odoo.models import *
from datetime import datetime
import requests


class BaseModelExtend(AbstractModel):


    _inherit = 'base'

    @api.model
    def encode(self,string,SHA=256):
        import hashlib
        if SHA == 512:result = hashlib.sha512(string.encode())
        elif SHA == 384:result = hashlib.sha384(string.encode())
        elif SHA == 256:result = hashlib.sha256(string.encode())
        elif SHA == 224:result = hashlib.sha224(string.encode())
        else:result = hashlib.sha1(string.encode())
        return (result.hexdigest())


    @api.model
    def regex(self,pattern,string,method='f',replace=''):
        import re
        if method == 'r' or method =='replace' or method =='sub':
            return re.sub(pattern,replace,string)
        elif method =='s' or method =='split':
            return re.split(pattern,string)
        else:
            return re.findall(pattern,string)

    @api.model
    def evaluate(self,computation):
        try:return eval(computation)
        except Exception as e:return (e.args[0])

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
        try:
            error_message=json_data['message']
            if error_message:
                return error_message
        except:pass
        # if json_data['cod']!=200:return "Not Found"
        if date_time:
            location_data = {
                'city': json_data['city']['name'],
                'country': json_data['city']['country']
            }
            json_data['list'].sort(key=lambda x:abs(datetime.strptime(x['dt_txt'],'%Y-%m-%d %H:%M:%S')-date_time))
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
