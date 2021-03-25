from odoo import http
from odoo.addons.web.controllers.main import DataSet


class DataSet(DataSet):

    @http.route(['/web/dataset/call_kw_survey', '/web/dataset/call_kw_survey/<path:path>'], type='json', auth="public")
    def call_kw_survey(self, model, method, args, kwargs, path=None):
        print("\n\n4444444444----->", model, method, args, kwargs)
        return self._call_kw(model, method, args, kwargs)
