# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _name = "sale.report"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'name'

    _columns = {
        'name' : fields.char('Sales Order No.',readonly=True),
        'po_no': fields.char('PO Number',readonly=True),
        'po_name': fields.char('PO Name',readonly=True),
        'jbo_project_code' : fields.char('JBO Project Code'),
        'incharge_nti' : fields.char('In-charge NTI'),
        'incharge_client' : fields.char('In-charge Client'),
        'cp_number' : fields.char('CP Number'),
        'date_tax' : fields.date('Date of Tax Convention Number'),
        'jccc_resources' : fields.boolean('Has JCCC Resources '),
        'sales_loc': fields.char('Sales Location'),
        'delivery_due_date': fields.date('Delivery Due Date'),
        'actual_delivery_date': fields.date('Actual delivery Date'),
        'pre_po_date': fields.date('Pre-PO Date'),
        'pre_po_amount' : fields.integer('Pre-PO Amount') ,
        'date' : fields.date('PO Date'),
        'po_amount' : fields.integer('PO Amount'),
        'po_project_id': fields.many2one('project.project', string= "Project Description" ,readonly=True),
        'am_user_id' : fields.many2one('res.users','Account Manager'),
        'pm_user_id': fields.many2one('res.users','Project Manager'),
        'nti_bu' : fields.many2one('hr.department','NTI BU'),
        'sap_project_code': fields.char('SAP Project Code'),
        'partner_id' : fields.many2one('res.partner','Client'),
        'client_bu': fields.char('Client BU'),
        'client_div': fields.char('Client Division'),
        'po_start': fields.date('PO Start'),
        'po_end': fields.date('PO End'),
        'al_date': fields.date('AL Date'),
        'tax_category': fields.selection([
            ('WT', 'WT'),
            ('CT', 'CT')
            ], 'Tax Category'),
        'invoice_number' : fields.char('Invoice Number'),
        'invoice_date' : fields.date('Invoice Date'),
        'invoice_billed' : fields.integer('Invoice billed(JPY)'),
        'shipping_invoice_number' : fields.char('Shipping Invoice Number'),
        'payment_due_date': fields.date('Payment Due Date'),
        'payment_date': fields.date('Payment Date'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True)
    }
    _order = 'date desc'

    def _select(self):
        select_str = """
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                    SELECT r.currency_id, r.rate, r.name AS date_start,
                        (SELECT name FROM res_currency_rate r2
                        WHERE r2.name > r.name AND
                            r2.currency_id = r.currency_id
                         ORDER BY r2.name ASC
                         LIMIT 1) AS date_end
                    FROM res_currency_rate r
                )
             SELECT row_number() OVER() AS id, 
                    s.name as name,
                    s.po_no as po_no,
                    s.jbo_project_code as jbo_project_code,
                    s.incharge_nti as incharge_nti,
                    s.incharge_client as incharge_client,
                    s.cp_number as cp_number,
                    s.company_id as company_id,
                    s.date_tax as date_tax,
                    s.jccc_resources as jccc_resources,
                    s.po_name as po_name,
                    s.sales_loc as sales_loc,
                    s.delivery_due_date as delivery_due_date,
                    s.actual_delivery_date as actual_delivery_date,
                    s.pre_po_date as pre_po_date,
                    s.pre_po_amount as pre_po_amount,
                    s.po_date as date,
                    s.po_amount as po_amount,
                    s.po_project_id as po_project_id,
                    s.am_user_id as am_user_id,
                    s.pm_user_id as pm_user_id,
                    s.nti_bu as nti_bu,
                    s.sap_project_code as sap_project_code,
                    s.partner_id as partner_id,
                    s.client_bu as client_bu,
                    s.client_div as client_div,
                    s.po_start as po_start,
                    s.po_end as po_end,
                    s.al_date as al_date,
                    s.tax_category as tax_category,
                    si.number as invoice_number,
                    si.date as invoice_date,
                    si.amount as invoice_billed,
                    si.shipping_number as shipping_invoice_number,
                    s.payment_due_date as payment_due_date,
                    s.payment_date as payment_date

        """
        return select_str

    def _from(self):
        from_str = """
                      sale_order s
                      left join sale_invoice si on (s.id = si.order_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY s.name,
                     s.po_no,
                     s.po_name,
                     s.jbo_project_code,
                     s.incharge_nti,
                     s.incharge_client,
                     s.cp_number,
                     s.date_tax,
                     s.jccc_resources,
                     s.sales_loc,
                     s.delivery_due_date,
                     s.actual_delivery_date,
                     s.pre_po_date,
                     s.pre_po_amount,
                     s.po_date,
                     s.po_amount,
                     s.po_project_id,
                     s.am_user_id,
                     s.pm_user_id,
                     s.nti_bu,
                     s.sap_project_code,
                     s.partner_id,
                     s.client_bu,
                     s.client_div,
                     s.po_start,
                     s.po_end,
                     s.al_date,
                     s.tax_category,
                     si.number,
                     si.date,
                     si.amount,
                     si.shipping_number,
                     s.payment_due_date,
                     s.payment_date,
                     s.company_id

        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
