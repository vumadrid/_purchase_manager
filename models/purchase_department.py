
from odoo import fields, models
class Department(models.Model):
    _name = 'hr.department'
    _rec_name = 'department'

    department = fields.Char(string='Department', required=True, unique=True)
    department_members = fields.One2many(comodel_name='purchase.request', inverse_name='department_id',
                                         string='Department Members')
    _sql_constraints = [
        ('department_unique',
         'unique(department)',
         'Choose another value - it has to be unique!')
    ]
    department_count = fields.Integer(string='Department count', compute='_compute_department_count')
    all_purchase = fields.Integer(string='All purchase count', compute='_compute_all_purchase')

    def _compute_department_count(self):
        for rec in self:
            department_count = self.env['purchase.request'].search_count([('department_id', '=', rec.id)])
            rec.department_count = department_count

    def _compute_all_purchase(self):
        all_purchase = self.env['purchase.request'].search_count([])
        self.all_purchase = all_purchase

