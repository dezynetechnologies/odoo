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
from openerp.osv import fields,osv

class hr_timesheet_utilisation_report(osv.osv):
    _name = "hr.timesheet.utilisation.report"
    #_inherit = "hr.timesheet.report"
    _description = "Resource Utilisation"
    _auto = False
    _rec_name = 'date'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'employee_no': fields.char('Employee No'),
        'offshore_billed_mm' : fields.float('Offshore Billed Man Months'),
        'offon_billed_mm' : fields.float('Offon Billed Man Months'),
        'total_billed_mm' : fields.float('Total Billed Man Months'),
        'total_offshore_mm' : fields.float('Total Offshore Man Months'),
        'total_offon_mm' : fields.float('Total Offon Man Months'),
        'total_mm' : fields.float('Total Man Months'),
        'offshore_billed_util' : fields.float('Offshore Billed Utilisation(%)',group_operator='sum'),
        'offon_billed_util' : fields.float('Offon Billed Utilisation(%)',group_operator='sum'),
        'combined_billed_util' : fields.float('Combined Billed Utilisation(%)',group_operator='sum'),
        'timed_utilisation' : fields.float('Timed Utilisation(%)'),
        'department_id': fields.many2one('hr.department','Business Unit',readonly=True),
        'department_name' : fields.char('Business Unit Name',readonly=True),
        'nti_unit' : fields.many2one('hr.department','NTI Unit',readonly=True),
        'project_id':  fields.many2one('project.project','Project'),
        'date' : fields.date('Date'),
        }
    _order = 'employee_no asc'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        print cr
        print uid
        print count
        for arg in args:
            print arg
        return super(hr_timesheet_utilisation_report, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,
            context=context, count=count)


    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False,lazy=True):
        if context is None:
            context = {}
        print "read_group() called"
        ret_val =  super(hr_timesheet_utilisation_report, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby,lazy)
        for retv in ret_val:
            print retv
            if retv['total_mm'] == 0:
                retv['timed_utilisation'] = retv['timed_utilisation']
            else:
                retv['timed_utilisation'] = (retv['total_billed_mm']/retv['total_mm'])*100

            if retv['total_mm'] == 0:
                retv['combined_billed_util'] = retv['combined_billed_util']
            else:
                retv['combined_billed_util'] = (retv['total_billed_mm']/retv['total_mm'])*100

            if retv['total_offshore_mm'] == 0:
                retv['offshore_billed_util'] = retv['offshore_billed_util']
            else:
                retv['offshore_billed_util'] = (retv['offshore_billed_mm']/retv['total_offshore_mm'])*100

            if retv['total_offon_mm'] == 0:
                retv['offon_billed_util'] = retv['offon_billed_util']
            else:
                retv['offon_billed_util'] = (retv['offon_billed_mm']/retv['total_offon_mm'])*100

        return ret_val


    def _select(self):
        select_str = """
        SELECT ss.id as id,
               ss.employee_id as employee_id,
               ss.employee_no as employee_no,
               ss.department_id as department_id,
               (SELECT name from hr_department where id = department_id) as department_name,
               (case when ss.parent_deptt_id is null then ss.department_id else ss.parent_deptt_id end) as nti_unit,
               ss.date as date,
               ss.project_id as project_id,
               SUM (ss.offshore_billed_mm) as offshore_billed_mm,
               SUM (ss.offon_billed_mm) as offon_billed_mm,
               SUM (ss.total_billed_mm) as total_billed_mm,
               SUM (ss.total_offshore_mm) as total_offshore_mm,
               SUM (ss.total_offon_mm) as total_offon_mm,
               SUM (ss.total_mm) as total_mm,
               case when sum(ss.total_mm) = 0 then 0::numeric else sum(ss.offshore_billed_util * ss.total_mm) / sum(ss.total_mm) end as offshore_billed_util,
               case when sum(ss.total_mm) = 0 then 0::numeric else sum(ss.offon_billed_util * ss.total_mm) / sum(ss.total_mm) end as offon_billed_util,
               case when sum(ss.total_mm) = 0 then 0::numeric else sum(ss.combined_billed_util * ss.total_mm) / sum(ss.total_mm) end as combined_billed_util,
               case when sum(ss.total_mm) = 0 then 0::numeric else sum(ss.timed_utilisation * ss.total_mm) / sum(ss.total_mm) end  as timed_utilisation
        """
        return select_str

    def _from(self):
        from_str = """
                (SELECT row_number() OVER() AS id,
                    e.id as employee_id,
                    e.employee_no as employee_no,
                    e.department_id as department_id,
                    (select parent_id from hr_department where id = e.department_id ) as parent_deptt_id,
                    t.date_from as date,
                    t.project_id as project_id,
		            case when t.billing_perc != 0 then ( case when t.geography::text = 'offshore' then ( ((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end) else  0::numeric  end as offshore_billed_mm,
		            case when t.billing_perc != 0 then ( case when t.geography::text = 'offon' then ( ((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end) else  0::numeric  end as offon_billed_mm,
                    case when t.billing_perc != 0 then (((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end as total_billed_mm,
                    case when t.geography::text = 'offshore' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as total_offshore_mm,
                    case when t.geography::text = 'offon' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as total_offon_mm,
                    ((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) as total_mm,
                    case when t.billing_perc != 0 then ( case when t.geography::text = 'offshore' then ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100)) )*100 else 0::numeric end) else 0::numeric end as offshore_billed_util,
			        case when t.billing_perc != 0 then ( case when t.geography::text = 'offon' then  ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100)) )*100   else 0::numeric end) else 0::numeric end as offon_billed_util,
			        case when t.billing_perc != 0 then  ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100)) )*100  else 0::numeric end as combined_billed_util,
				    (case when (select sap_project_code from project_project where id = t.project_id) = 'bench' then 0::numeric else t.allocation_perc end) as timed_utilisation

                    FROM
                hr_employee e
                    join hr_timesheet_sheet_sheet t on e.id=t.employee_id GROUP BY e.id,
                    e.employee_no,
                    t.date_from,
                    t.date_to,
                    t.department_id,
                    t.geography,
                    t.billed_status,
                    t.project_id,
                    t.billing_perc,
                    t.allocation_perc) AS ss
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY ss.id,
                    ss.employee_no,
                    ss.employee_id,
                    ss.date,
                    ss.department_id,
                    department_name,
                    nti_unit,
                    ss.project_id
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
