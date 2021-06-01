from odoo import api, models


class ReportGiroTemp(models.AbstractModel):
    _name = 'report.report_giro.report_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'type': data['type'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('report_giro.report_temp', docargs)
