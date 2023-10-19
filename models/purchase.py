from random import random
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
class Department(models.Model):
    _name = 'hr.department'
    _rec_name = 'department'

    # department_code = fields.Char(string='Department', required=True, unique=True)
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


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one('purchase.request', string="Purchase Request", ondelete='cascade')
    product_id = fields.Many2one('product.template', string="Product", required=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", required=True)
    qty = fields.Float(string="Quantity", default=1.0)
    qty_approve = fields.Float(string="Approved Quantity", readonly=False)
    price_unit = fields.Float(string="Unit Price")
    total = fields.Float(string="Total", compute='_compute_total', store=True)

    @api.depends('qty_approve', 'price_unit')
    def _compute_total(self):
        for line in self:
            line.total = line.qty_approve * line.price_unit

    @api.onchange('qty_approve')
    def _onchange_qty_approve(self):
        if self.state == 'wait':
            return
        else:
            self.qty_approve = self._origin.qty_approve

    @api.constrains('qty_approve')
    def _check_qty_approve(self):
        for line in self:
            if line.state == 'wait' and line.qty_approve < 0:
                raise exceptions.ValidationError("Approved quantity cannot be negative when the request is in 'wait' state.")


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, copy=False, readonly=True, index=True, tracking=True, default=lambda self: _('PR'))
    department_id = fields.Many2one(comodel_name='hr.department', ondelete='set null', string="Department")
    request_id = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    approver_id = fields.Many2one('res.users', string="Approver")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    date_approve = fields.Date(string="Date Approved")
    request_line_ids = fields.One2many('purchase.request.line', 'request_id', string="Request Lines")
    description = fields.Text(string="Description")
    state = fields.Selection([
        ('request', 'Request Approval'),
        ('draft', 'Draft'),
        ('wait', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string="State", default='draft', readonly=True, copy=False, Tracking=True, track_visibility='onchange')
    total_qty = fields.Float(string="Total Quantity", compute='_compute_total')
    total_amount = fields.Float(string="Total", compute='_compute_total')

    @api.model
    def create(self, values):

        if values.get('name', _('PR')) == _('PR'):
            values['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or _('PR')

        res = super(PurchaseRequest, self).create(values)

        return res
    @api.depends('request_line_ids.qty_approve', 'request_line_ids.total')
    def _compute_total(self):
        for request in self:
            request.total_qty = sum(request.request_line_ids.mapped('qty_approve'))
            request.total_amount = sum(request.request_line_ids.mapped('total'))


    def unlink(self):
        for request in self:
            if request.state != 'draft':
                raise UserError(_("You can only delete purchase requests in draft state."))
        return super(PurchaseRequest, self).unlink()

    def request_approval(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
        else:
            order.write({'state': 'approved'})
        return True


    def action_set_draft(self):
        self.write({'state': 'draft'})
        return {}


    def action_set_done(self):
        for order in self:
            if order.state == 'approved':
                order.write({'state': 'cancel'})
        return True

    # def write(self, vals):
    #     if any(state == 'cancel' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super().write(vals)

