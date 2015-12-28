#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval


class hr_payslip_nec(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _name = 'hr.payslip.nec'
    _description = 'Pay Slip'

    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr,uid,uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id


    _columns = {
        'onsite_allowance' : fields.integer('Onsite Allowance',required=True),
        'offshore_salary' : fields.integer('Offshore Salary',required=True),
        'currency_id' : fields.many2one('res.currency', "Currency", required=True, help="The currency the field is expressed in."),

    }
    _defaults = {

    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'onsite_allowance' in context:
            vals.update({'onsite_allowance': context.get('onsite_allowance')})
        if 'offshore_salary' in context:
            vals.update({'offshore_salary': context.get('offshore_salary')})
        if 'currency_id' in context:
            vals.update({'currency_id': context.get('currency_id')})
        vals.update({'state': 'draft'})
        vals.update({'basic_pay': 0})
        return super(hr_payslip_nec, self).create(cr, uid, vals, context=context)

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, context=None):
        #department_id = False
        empolyee_obj = self.pool.get('hr.employee')
        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        department_id = employee_id.department_id.id
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_id.company_id.id,
		    'department_id' : department_id
        })
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
