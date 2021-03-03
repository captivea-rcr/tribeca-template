# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

{
    'name': "Global Functions",
    'version': "14.0",
    'author': "Captivea",
    'summary': """Functions: 
    model.regex(pattern,string,method='f',replace='') --> regular expression functionality,
    model.getWeather(zipcode,date_time=None) --> Get Weather fom zipcode and time,
    model.evaluate(string_of_math) --> evaluate math equation from string,
    model.encode(string,SHA=256) --> encodes string to secure SHA mapping""",
    'depends': ['base'],
    'data': [],
    'installable': True,
}
