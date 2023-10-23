from odoo import models, fields
class CustomUser(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2one('hr.department', 'Department')
