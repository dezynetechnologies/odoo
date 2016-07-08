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
        'project_id': fields.many2one('project.project','Project'),
        'department_id': fields.many2one('hr.department','Business Unit(Project)',readonly=True),
        'res_department_id': fields.many2one('hr.department','Business Unit(Resource)',readonly=True),
        'department_name' : fields.char('Business Unit'),
        'nti_unit' : fields.many2one('hr.department','NTI Unit',readonly=True),
        'sap_project_code' : fields.char('SAP Project Code'),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'employee_no': fields.char('Employee No'),
        'revenue_inr' : fields.float('Revenue(INR)',digits=(32,0)),
        'direct_cost_inr' : fields.float('Direct Cost(INR)',digits=(32,0)),
        'direct_cost_inr_tot' : fields.float('Direct Cost Total(INR)',digits=(32,0)),
        'other_direct_cost_inr' : fields.float('Other Direct Cost(INR)',digits=(32,0)),
        'other_direct_cost_inr_tot' : fields.float('Other Direct Cost Total(INR)',digits=(32,0)),
        'gross_profit_inr': fields.float('Gross Profit(INR)',digits=(32,0)),
        'sga_inr' : fields.float('SGA(INR)',digits=(32,0)),
        'sga_inr_tot' : fields.float('SGA Total(INR)',digits=(32,0)),
        'operating_profit_inr' : fields.float('Operating Profit(INR)',digits=(32,0)),
        'gross_profit_perc' : fields.float('Gross Profit(%)',group_operator = 'sum'),
        'oper_profit_perc' : fields.float('Operating Profit(%)',group_operator = 'sum'),
        'date': fields.date('Month',readonly=True),
        'offshore_mm' : fields.float('Offshore mm'),
        'offon_mm' : fields.float('Offon mm'),
        'total_mm' : fields.float('Total mm',group_operator = 'avg'),
        'total_offshore_mm': fields.float('Total Offshore mm',group_operator = 'avg'),
        'total_offon_mm' : fields.float('Total Offon mm',group_operator = 'avg'),
        'geography':fields.selection([('offon','offon'),('offshore','offshore')],'Geography'),
        'expense_category':fields.char('Expense Category')
        }
    _order = 'sap_project_code asc'

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False,lazy=True):
        if context is None:
            context = {}
        #print "read_group() called"
        ret_val =  super(project_profitability_report, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby,lazy)
        for retv in ret_val:
            #print retv
            retv['gross_profit_inr'] = retv['revenue_inr'] - retv['direct_cost_inr'] - retv['other_direct_cost_inr']
            retv['operating_profit_inr'] = retv['revenue_inr'] - retv['direct_cost_inr']- retv['other_direct_cost_inr'] - retv['sga_inr']
            if retv['revenue_inr'] == 0:
                retv['gross_profit_perc'] = 0
                retv['oper_profit_perc']  = 0
            else:
                retv['gross_profit_perc'] = (retv['gross_profit_inr']/retv['revenue_inr'])*100
                retv['oper_profit_perc'] = (retv['operating_profit_inr']/retv['revenue_inr'])*100

        return ret_val

    def _select(self):
        select_str = """
        SELECT row_number() OVER() AS id,
        BIG.employee_id as employee_id,
        BIG.employee_no as employee_no,
        BIG.project_id as project_id,
        BIG.sap_project_code as sap_project_code,
        (case when (select department_id from project_project where id = project_id) is null then (case when employee_id is null then null else (BIG.res_department_id) end) else (select department_id from project_project where id = project_id) end) as department_id,
        BIG.res_department_id as res_department_id,
        (SELECT name from hr_department where id = (case when employee_id is null then (select department_id from project_project where id = project_id) else (BIG.res_department_id) end)) as department_name,
        (case when (select department_id from project_project where id = project_id) is null then (case when (select parent_id from hr_department where id = (BIG.res_department_id) ) is null then (BIG.res_department_id) else (select parent_id from hr_department where id = (BIG.res_department_id)) end )
            else (case when (select parent_id from hr_department where id = (select department_id from project_project where id = BIG.project_id) ) is null then (select department_id from project_project where id = BIG.project_id) else (select parent_id from hr_department where id = (select department_id from project_project where id = BIG.project_id) ) end )  end) as nti_unit,
        SUM(revenue_inr) as revenue_inr,
        SUM(direct_cost_inr) as direct_cost_inr,
        SUM(BIG.direct_cost_inr_tot) as direct_cost_inr_tot,
        SUM(BIG.other_direct_cost_inr) as other_direct_cost_inr,
        SUM(BIG.other_direct_cost_inr_tot) as other_direct_cost_inr_tot,
        SUM(revenue_inr - direct_cost_inr - other_direct_cost_inr) as gross_profit_inr,
        SUM(sga_inr) as sga_inr,
        SUM(BIG.sga_inr_tot) as sga_inr_tot,
        SUM(revenue_inr - direct_cost_inr - other_direct_cost_inr - sga_inr) as operating_profit_inr,
        AVG(case when revenue_inr !=0 then ((revenue_inr - direct_cost_inr - other_direct_cost_inr)*100)/(revenue_inr) else 0::numeric end) as gross_profit_perc,
        AVG(case when revenue_inr !=0 then ((revenue_inr - direct_cost_inr - other_direct_cost_inr-sga_inr)*100)/(revenue_inr) else  0::numeric end) as oper_profit_perc,
        date,
        SUM(offshore_mm) as offshore_mm,
        SUM(offon_mm) as offon_mm,
        SUM(total_mm) as total_mm,
        SUM(total_offshore_mm) as total_offshore_mm,
        SUM(total_offon_mm) as total_offon_mm,
        geography,
        expense_category
        """
        return select_str

    def _from(self):
        from_str = """
                    (SELECT employee_id,
                    employee_no,
                    project_id,
                    res_department_id,
                    sap_project_code,
                    SUM(revenue_inr) as revenue_inr,
                    SUM(direct_cost_inr) as direct_cost_inr,
                    date,
                    SUM(sga_inr) as sga_inr,
                    SUM(sga_inr_tot) as sga_inr_tot,
                    SUM(direct_cost_inr) as direct_cost_inr_tot,
                    SUM(other_direct_cost_inr) as other_direct_cost_inr,
                    SUM(other_direct_cost_inr_tot) as other_direct_cost_inr_tot,
                    SUM(offshore_mm) as offshore_mm,
                    SUM(offon_mm) as offon_mm,
                    SUM(total_mm) as total_mm,
                    SUM(total_offshore_mm) as total_offshore_mm,
                    SUM(total_offon_mm) as total_offon_mm,
                    geography,
                    expense_category

                FROM (
                SELECT employee_id, employee_no,project_id,res_department_id,sap_project_code,billable_cost as revenue_inr,exp_cost as direct_cost_inr,date, 0 as sga_inr,
                       0 as sga_inr_tot,
                       exp_cost as direct_cost_inr_tot,
                       0 as other_direct_cost_inr,
                       0 as other_direct_cost_inr_tot,
                       0 as offshore_mm,
                       0 as offon_mm,
                       0 as total_mm,
                       0 as total_offshore_mm,
                       0 as total_offon_mm,
                       'offshore' as geography,
                       'non-salary' as expense_category

                FROM (

                SELECT null as employee_id,'' as employee_no,project_id,null as res_department_id,sap_project_code,exp_cost,billable_cost,date,category  from project_specific_expenses

                UNION ALL

                SELECT employee_id,employee_no,project_id,res_department_id,sap_project_code,exp_cost,billable_cost,date,category  from project_employee_expenses

                ) AS ASD
                UNION ALL
            (SELECT

                employee_id,
                employee_no,
                project_id,
		res_department_id,
                sap_project_code,
                SUM(revenue_inr) as revenue_inr,
                SUM(case when total_offon_mm = 0 then
	(case when total_offshore_mm = 0 then
		(case when geography::text = 'offon' then
			case when total_offshore_entries = 0 then
			(onsite_allowance + offshore_salary)/total_offon_entries
			else
			(onsite_allowance)/total_offon_entries
			end
		else
			case when total_offon_entries = 0 then
			(offshore_salary + onsite_allowance)/total_offshore_entries
			else
			(offshore_salary)/total_offshore_entries
			end
		end)
	else
		(case when geography::text = 'offon' then
			(onsite_allowance)/total_offon_entries
		else
			case when total_offon_entries = 0 then
			((offshore_salary+onsite_allowance)*offshore_mm)/total_mm
			else
			(offshore_salary*offshore_mm)/total_mm
			end
		end)

	end)
else
	(case when total_offshore_mm = 0 then
		(case when geography::text = 'offon' then
			case when total_offshore_entries = 0 then
			((onsite_allowance + offshore_salary)*offon_mm)/total_offon_mm
			else
			(offon_mm/total_offon_mm)*onsite_allowance + (offon_mm/total_mm)*offshore_salary
			end
		else
			0::numeric
		end)
	else
		(case when geography::text = 'offon' then
			(offon_mm/total_offon_mm)*onsite_allowance + (offon_mm/total_mm)*offshore_salary
		else
			(offshore_mm/total_mm)*offshore_salary
		end)

	end)

end) as direct_cost_inr,
                date,
                SUM(case when total_mm = 0 then 0 else (case when geography::text = 'offon' then (offon_mm/total_unit_mm)*sga_inr else (offshore_mm/total_unit_mm)*sga_inr end) end) as sga_inr,
                SUM(sga_inr) as sga_inr_tot,
                SUM(onsite_allowance + offshore_salary) as direct_cost_inr_tot,
                SUM(case when total_mm = 0 then 0 else (case when geography::text = 'offon' then (offon_mm/total_unit_mm)*direct_cost_inr else (offshore_mm/total_unit_mm)*direct_cost_inr end) end) as other_direct_cost_inr,
                SUM(direct_cost_inr) as other_direct_cost_inr_tot,
                SUM(offshore_mm) as offshore_mm,
                SUM(offon_mm) as offon_mm,
                SUM(total_mm) as total_mm,
                SUM(total_offshore_mm) as total_offshore_mm,
                SUM(total_offon_mm) as total_offon_mm,
                geography as geography,
                'salary' as expense_category
                FROM

                (
                SELECT

                t.employee_id,t.employee_no,t.project_id,t.department_id as res_department_id,t.sap_project_code,t.revenue_inr,t.geography as geography,date_trunc('month',t.date_from)::date as date,

                    case when t.geography::text = 'offshore' then ( ((t.date_to - t.date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) < 30 then 28::numeric else 30::numeric end)*100) ) else 0::numeric end as offshore_mm,

                    case when t.geography::text = 'offon' then ( ((t.date_to - t.date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)) < 30 then 28::numeric else 30::numeric end)*100) ) else 0::numeric end as offon_mm,

                total_unit_mm,total_mm,total_offshore_mm,total_offon_mm,total_offon_entries,total_offshore_entries, ps.offshore_salary, ps.onsite_allowance,pps.amount as sga_inr,pps1.amount as direct_cost_inr

                FROM

                hr_timesheet_sheet_sheet t

                left join


                (SELECT SUM(total_mm) as total_unit_mm, nti_unit , date FROM

                (

                SELECT employee_id,project_id,sap_project_code,revenue_inr,geography,date_trunc('month',date_from)::date as date,

                    ((date_to - date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to)) < 30 then 28::numeric else 30::numeric end)*100) as total_mm,
		            (case when (SELECT parent_id FROM hr_department WHERE id= (department_id)) is null then (SELECT id FROM hr_department WHERE id= (department_id)) else (SELECT parent_id FROM hr_department WHERE id= (department_id)) end) as nti_unit

                FROM hr_timesheet_sheet_sheet ) AS ss GROUP BY nti_unit,date ) as tpp on tpp.nti_unit = (case when (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) is null then (SELECT id FROM hr_department WHERE id= (t.department_id)) else (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) end) and tpp.date=date_trunc('month',t.date_from)::date

                left join

                (SELECT employee_id,SUM(total_offshore_mm) as total_offshore_mm,SUM(total_offon_mm) as total_offon_mm,SUM(total_mm) as total_mm,date, SUM(total_offshore_entries) as total_offshore_entries, SUM(total_offon_entries) as total_offon_entries FROM

                (

                SELECT employee_id,project_id,sap_project_code,revenue_inr,geography,date_trunc('month',date_from)::date as date,

                	(case when geography::text = 'offshore' then 1::numeric else 0::numeric end) as total_offshore_entries,
		            (case when geography::text = 'offon' then 1::numeric else 0::numeric end) as total_offon_entries,

                    ((date_to - date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to)) < 30 then 28::numeric else 30::numeric end)*100) as total_mm,

                    case when geography::text = 'offshore' then ( ((date_to - date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to)) < 30 then 28::numeric else 30::numeric end)*100) ) else 0::numeric end as total_offshore_mm,

                    case when geography::text = 'offon' then ( ((date_to - date_from + 1)*allocation_perc)/((case when date_part('days',date_trunc('month',date_to) + '1 month'::interval - date_trunc('month',date_to)) < 30 then 28::numeric else 30::numeric end)*100) ) else 0::numeric end as total_offon_mm

                FROM hr_timesheet_sheet_sheet ) AS ss GROUP BY employee_id,date ) as tp on tp.employee_id=t.employee_id and tp.date=date_trunc('month',t.date_from)::date

		left join

                hr_payslip_nec as ps on tp.employee_id=ps.employee_id and tp.date=date_trunc('month',ps.date_from)::date

		left join

		project_expenses as pps on date_trunc('month',t.date_from)::date = date_trunc('month',pps.date_from)::date and pps.nti_unit = (case when (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) is null then (SELECT id FROM hr_department WHERE id= (t.department_id)) else (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) end) and pps.category = 'sga'

		left join

                project_expenses as pps1 on date_trunc('month',t.date_from)::date = date_trunc('month',pps1.date_from)::date and pps1.nti_unit = (case when (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) is null then (SELECT id FROM hr_department WHERE id= (t.department_id)) else (SELECT parent_id FROM hr_department WHERE id= (t.department_id)) end) and pps1.category = 'direct_cost'



                ) AS FOO GROUP BY employee_id,employee_no,project_id,res_department_id,date,sap_project_code,geography

                )

                ) AS BIGG GROUP BY employee_id,employee_no,project_id,res_department_id,date,sap_project_code,geography,expense_category) AS BIG
        """
        return from_str

    def _group_by(self):
        group_by_str = """
        GROUP BY BIG.employee_id,
                 BIG.employee_no,
                 BIG.project_id,
                 BIG.date,
                 department_id,
                 res_department_id,
                 department_name,
                 BIG.sap_project_code,
                 BIG.geography,
                 BIG.expense_category
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
