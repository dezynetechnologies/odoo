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
        'project_id': fields.many2one('project.project','Project'),
        'sap_project_code' : fields.char('SAP Project Code'),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'employee_no': fields.char('Employee No'),
        'revenue_inr' : fields.float('Revenue(INR)'),
        'direct_cost_inr' : fields.float('Direct Cost(INR)'),
        'gross_profit_inr': fields.float('Gross Profit(INR)'),
        'sga_inr' : fields.float('SGA(INR)'),
        'operating_profit_inr' : fields.float('Operating Profit(INR)'),
        'gross_profit_perc' : fields.float('Gross Profit(%)'),
        'oper_profit_perc' : fields.float('Operating Profit(%)'),
        'date': fields.date('Month',readonly=True),
        }
    _order = 'sap_project_code asc'

    def _select(self):
        select_str = """
        SELECT row_number() OVER() AS id,
        BIG.employee_id as employee_id,
        BIG.employee_no as employee_no,
        BIG.project_id as project_id,
        BIG.sap_project_code as sap_project_code,
        SUM(revenue_inr) as revenue_inr,
        SUM(exp_cost + direct_cost_inr) as direct_cost_inr,
        SUM(revenue_inr - exp_cost - direct_cost_inr) as gross_profit_inr,
        SUM(sga_inr) as sga_inr,
        SUM(revenue_inr - exp_cost - direct_cost_inr - sga_inr) as operating_profit_inr,
        AVG(((revenue_inr - exp_cost - direct_cost_inr)*100)/(revenue_inr)) as gross_profit_perc,
        AVG(((revenue_inr - exp_cost - direct_cost_inr-sga_inr)*100)/(revenue_inr)) as oper_profit_perc,
        date
        """
        return select_str

    def _from(self):
        from_str = """
            (SELECT employee_id,employee_no, project_id,sap_project_code,SUM(revenue_inr) as revenue_inr,SUM(exp_cost) as exp_cost,date,SUM(sga_inr) as sga_inr,SUM(direct_cost_inr) as direct_cost_inr

                FROM (
                SELECT employee_id,employee_no,project_id,sap_project_code,billable_cost as revenue_inr,exp_cost,date, 0 as sga_inr, 0 as direct_cost_inr

                FROM (

                SELECT null as employee_id,'' as employee_no,project_id,sap_project_code,exp_cost,billable_cost,date,category  from project_specific_expenses

                UNION ALL

                SELECT employee_id,employee_no,project_id,sap_project_code,exp_cost,billable_cost,date,category  from project_employee_expenses

                ) AS ASD
                UNION ALL
            (SELECT

                employee_id,employee_no,project_id,sap_project_code,SUM(revenue_inr) as revenue_inr,

                SUM(case when geography::text = 'offon' then (offon_mm/total_offon_mm)*onsite_allowance + (offon_mm/total_mm)*offshore_salary else (offshore_mm/total_mm)*offshore_salary end) as exp_cost,date,
                SUM(case when geography::text = 'offon' then (offon_mm/total_mm)*sga_inr else (offshore_mm/total_mm)*sga_inr end) as sga_inr,
                SUM(case when geography::text = 'offon' then (offon_mm/total_mm)*direct_cost_inr else (offshore_mm/total_mm)*direct_cost_inr end) as direct_cost_inr

                FROM

                (

                SELECT

                t.employee_id,t.employee_no,t.project_id,t.sap_project_code,t.revenue_inr,t.geography,date_trunc('month',t.date_from)::date as date,

                    case when t.geography::text = 'offshore' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as offshore_mm,

                    case when t.geography::text = 'offon' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as offon_mm,

                total_mm,total_offshore_mm,total_offon_mm,offshore_salary,onsite_allowance,pps.amount as sga_inr,pps1.amount as direct_cost_inr

                FROM

                hr_timesheet_sheet_sheet t

                left join

                (SELECT employee_id,SUM(total_offshore_mm) as total_offshore_mm,SUM(total_offon_mm) as total_offon_mm,SUM(total_mm) as total_mm,date FROM

                (

                SELECT employee_id,project_id,sap_project_code,revenue_inr,geography,date_trunc('month',date_from)::date as date,

                    ((date_to - date_from + 1)*allocation_perc)/(date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to))*100) as total_mm,

                    case when geography::text = 'offshore' then ( (date_to - date_from + 1)*allocation_perc/(date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to))*100) ) else 0::numeric end as total_offshore_mm,

                    case when geography::text = 'offon' then ( (date_to - date_from + 1)*allocation_perc/(date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to))*100) ) else 0::numeric end as total_offon_mm

                FROM hr_timesheet_sheet_sheet ) AS ss GROUP BY employee_id,date ) as tp on tp.employee_id=t.employee_id and tp.date=date_trunc('month',t.date_from)::date

                left join

                hr_payslip_nec as ps on tp.employee_id=ps.employee_id and tp.date=date_trunc('month',ps.date_from)::date

                left join

                project_expenses as pps on date_trunc('month',ps.date_from)::date = date_trunc('month',pps.date_from)::date and pps.nti_unit = (SELECT parent_id FROM hr_department WHERE id=t.department_id) and category = 'sga'

                left join

                project_expenses as pps1 on date_trunc('month',ps.date_from)::date = date_trunc('month',pps1.date_from)::date and pps1.nti_unit = (SELECT parent_id FROM hr_department WHERE id=t.department_id) and pps1.category = 'direct_cost'

                ) AS FOO GROUP BY employee_id,employee_no,project_id,date,sap_project_code

                )

                ) AS BIGG GROUP BY employee_id,employee_no,project_id,date,sap_project_code) AS BIG

        """
        return from_str

    def _group_by(self):
        group_by_str = """
        GROUP BY BIG.employee_id,
                 BIG.employee_no,
                 BIG.project_id,
                 BIG.date,
                 BIG.sap_project_code
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        print("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
