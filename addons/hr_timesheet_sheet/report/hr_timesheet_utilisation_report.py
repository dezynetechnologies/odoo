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
        'name': fields.char("Name", required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'employee_no': fields.char('Employee No'),
        'offshore_billed_mm' : fields.float('Offshore Billed Man Months'),
        'offon_billed_mm' : fields.float('Offon Billed Man Months'),
        'total_billed_mm' : fields.float('Total Billed Man Months'),
        'total_offshore_mm' : fields.float('Total Offshore Man Months'),
        'total_offon_mm' : fields.float('Total Offon Man Months'),
        'total_mm' : fields.float('Total Man Months'),
        'offshore_billed_util1' : fields.float('Offshore Billed Utilisation'),
        'offon_billed_util1' : fields.float('Offon Billed Utilisation'),
        'combined_billed_util1' : fields.float('Combined Billed Utilisation'),
        'timed_utilisation1' : fields.float('Timed Utilisation'),
        'offshore_billed_util' : fields.float('Offshore Billed Utilisation'),
        'offon_billed_util' : fields.float('Offon Billed Utilisation'),
        'combined_billed_util' : fields.float('Combined Billed Utilisation'),
        'timed_utilisation' : fields.float('Timed Utilisation'),
        'department_id': fields.many2one('hr.department','Department',readonly=True),
        'project_id':  fields.many2one('project.project','Project'),
        'date' : fields.date('Date'),
        }
    _order = 'name asc'

    def _select(self):
        select_str = """
                SELECT min(e.id) as id,
                    e.name_related as name,
                    e.id as employee_id,
                    e.employee_no as employee_no,
                    t.department_id as department_id,
                    t.date_from as date,

		            case when t.billing_perc != 0 then ( case when t.geography::text = 'offshore' then ( ((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end) else  0::numeric  end as offshore_billed_mm,

		            case when t.billing_perc != 0 then ( case when t.geography::text = 'offon' then ( ((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end) else  0::numeric  end as offon_billed_mm,

                    case when t.billing_perc != 0 then (((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100*100) ) else 0::numeric end as total_billed_mm,


                    case when t.geography::text = 'offshore' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as total_offshore_mm,

                    case when t.geography::text = 'offon' then ( (t.date_to - t.date_from + 1)*t.allocation_perc/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) ) else 0::numeric end as total_offon_mm,

                    ((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) as total_mm,

                    case when t.billing_perc != 0 then ( case when t.geography::text = 'offshore' then ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))) ) else 0::numeric end) else 0::numeric end as offshore_billed_util1,

			        case when t.billing_perc != 0 then ( case when t.geography::text = 'offon' then ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))) ) else 0::numeric end) else 0::numeric end as offon_billed_util1,

			        case when t.billing_perc != 0 then ( (((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))) else 0::numeric end as combined_billed_util1,

			        ((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100) as timed_utilisation1,
			        to_char(AVG (case when t.billing_perc != 0 then ( case when t.geography::text = 'offshore' then ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))) ) else 0::numeric end) else 0::numeric end),'99999999999999999D99') AS offshore_billed_util,
			        to_char(AVG (case when t.billing_perc != 0 then ( case when t.geography::text = 'offon' then ((((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))) ) else 0::numeric end) else 0::numeric end),'99999999999999999D99') AS offon_billed_util,
			        to_char(AVG (case when t.billing_perc != 0 then ( (((t.date_to - t.date_from + 1)*t.allocation_perc*t.billing_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))/(((t.date_to - t.date_from + 1)*t.allocation_perc)/date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to)))) else 0::numeric end),'99999999999999999D99') AS combined_billed_util,
			        to_char(AVG (((t.date_to - t.date_from + 1)*t.allocation_perc)/(date_part('days',date_trunc('month',t.date_to) + '1 month'::interval - date_trunc('month',t.date_to))*100)),'99999999999999999D99') AS timed_billed_util,
                    t.project_id as project_id
        """
        return select_str

    def _from(self):
        from_str = """
                hr_employee e
                    left join hr_timesheet_sheet_sheet t on e.id=t.employee_id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY e.id,
                    e.name_related,
                    e.employee_no,
                    t.date_from,
                    t.date_to,
                    t.department_id,
                    t.geography,
                    t.billed_status,
                    t.project_id,
                    t.billing_perc,
                    t.allocation_perc
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
