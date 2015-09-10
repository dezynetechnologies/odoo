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

from openerp.osv import fields, osv
from openerp import tools


class project_profitability_report(osv.osv):
    _name = "project.profitability.report"
    _description = "Project Profitability"
    _auto = False
    #_rec_name = 'date'

    _columns = {
        'name': fields.char("Name", required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'employee_no': fields.char('Employee No'),
        'doj': fields.date("Date of Joining"),
        'department_id':fields.many2one('hr.department','Department',readonly=True),
        'date_from': fields.date('Date from',readonly=True,),
        'date_to': fields.date('Date to',readonly=True),
        'project_id': fields.many2one('project.project','Project'),
        'geography':fields.selection([('onsite','onsite'),('offshore','offshore')],'Geography'),
        'billed_status':fields.selection([('billed','billed'),('unbilled','unbilled')],'Billing Status'),
        'project_role' : fields.char('Project Role'),
        'billing_perc': fields.integer('Billing',help="Billing percentage (0 to 100)"),
        'allocation_perc': fields.integer('Allocation',help="Allocation percentage (0 to 100) for the period"),
        'pay' : fields.integer('Pay(cost)'),
        'profit' : fields.integer('Gross Profit'),
        'profit_percentage' : fields.float('Profit Percentage'),
        'state' : fields.selection([
            ('new', 'New'),
            ('draft','Draft'),
            ('confirm','Confirmed'),
            ('done','Done')], 'Status', readonly=True),
        }
    _order = 'name asc'

    def _select(self):
        select_str = """
             SELECT min(e.id) as id,
                    e.name_related as name,
                    e.id as employee_id,
                    e.employee_no as employee_no,
                    e.doj as doj,
                    t.department_id as department_id,
                    t.date_from as date_from,
                    t.date_to as date_to,
                    t.project_id as project_id,
                    t.geography as geography,
                    t.billed_status as billed_status,
                    t.project_role as project_role,
                    t.billing_perc as billing_perc,
                    t.allocation_perc as allocation_perc,
                    ( t.date_to - t.date_from + 1) as num_of_days,
                    date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) as total_days,
                    ((p.basic_pay * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )as pay,
                    ((t.monthly_billing_rate * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) ) as billing,
                    ( (((t.monthly_billing_rate * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )) - (((p.basic_pay * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )) ) as profit,
                    ((( (((t.monthly_billing_rate * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )) - (((p.basic_pay * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )) )
)*100/(((t.monthly_billing_rate * ( t.date_to - t.date_from + 1))/ date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) )) ) as profit_percentage
        """
        return select_str

    def _from(self):
        from_str = """
                hr_employee e
                    left join hr_timesheet_sheet_sheet t on e.id=t.employee_id
                    left join public.hr_payslip p on
                        t.employee_id = p.employee_id  and t.date_from = p.date_from
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY e.id,
                    t.date_from,
                    t.date_to,
                    t.department_id,
                    t.geography,
                    t.billed_status,
                    t.project_id,
                    t.project_role,
                    t.billing_perc,
                    t.allocation_perc,
                    p.basic_pay,
                    t.monthly_billing_rate

        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        print("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: