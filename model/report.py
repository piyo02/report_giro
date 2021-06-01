from odoo import api, fields, models
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class ReportGiro(models.TransientModel):
    _name = "report.giro"

    giro_type = fields.Selection([
        ('receipt', 'Penerimaan'),
        ('payment', 'Tagihan')
    ], string='Tipe Giro', default='receipt', required=True)
    customers = fields.Many2many('res.partner', string='Pelanggan', required=False)
    is_open = fields.Boolean(string='Giro Open', required=False)

    @api.multi
    def print_report_giro(self):
        groupby_dict = {}

        state = 'close'
        if self.is_open:
            state = 'open'

        if len(self.customers) == 0:
            self.customers = self.env['res.partner'].search([
                ('customer', '=', True)
            ],
            order='name asc')

        for customer in self.customers:
            accounts = self.env['vit.giro'].search([
                ('partner_id', '=', customer.id),
                ('type', '=', self.giro_type),
                ('state', '=', state)
            ])

            customer_invoices = []
            for account in accounts:
                customer_invoice = []
                customer_invoice.append(account.name)               #0
                customer_invoice.append(account.journal_id.name)    #1
                customer_invoice.append(account.due_date)           #2
                customer_invoice.append(account.receive_date)       #3
                customer_invoice.append(account.clearing_date)      #4
                customer_invoice.append(account.amount)             #5
                customer_invoice.append(
                    dict(account._fields['state'].selection).get(account.state)
                )                                                   #6

                invoice_lines = []
                for invoice in account.giro_invoice_ids:
                    invoice_line = []
                    invoice_line.append(invoice.invoice_id.number)
                    invoice_line.append(invoice.amount_invoice)
                    invoice_line.append(invoice.amount)
                    invoice_lines.append(invoice_line)
                
                customer_invoice.append(invoice_lines)

                customer_invoices.append(customer_invoice)
            
            if len(customer_invoices) > 0:
                groupby_dict[customer.display_name] = customer_invoices


        datas = {
            'ids': self.ids,
            'model': 'report.giro',
            'form': groupby_dict,
            'type': dict(self._fields['giro_type'].selection).get(self.giro_type),
        }
        return self.env['report'].get_action(self,'report_giro.report_temp', data=datas)

    
    def _prepare_report_account_receivable(self):
        self.ensure_one()
        return {
            'ids': self.ids,
            'model': 'report.giro',
            'data': groupby_dict,
            'giro_type': self.giro_type,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_account_receivable())
        return report.print_report(report_type)