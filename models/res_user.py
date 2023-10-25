from odoo import models, fields
class CustomUser(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2one('hr.department', 'Department')
    approver_ids = fields.One2many(comodel_name='purchase.request', inverse_name='approver_id',
                                         string='Approver Ids')
    approver_member = fields.Selection([
        ('manager', 'Manager Approver'),
        ('user', 'User Approver'),
    ])