from random import random
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import csv
import io
import base64
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime, date


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, copy=False, readonly="1", index=True, tracking=True, default=lambda self: _('PR'))
    department_id = fields.Many2one(comodel_name='hr.department', ondelete='set null', string="Department", readonly=True)
    request_id = fields.Many2one('res.users', string="Requested By", readonly=True, default=lambda self: self.env.user)
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
    def create(self, vals):
        vals['request_id'] = self.env.user.id

        if 'department_id' in vals:
            department =self.env['hr.department'].browse(vals['department_id'])
            if department.approver_id:
                vals['approve_id'] = department.approver_id.id
                return super(PurchaseRequest, self).create(vals)

    @api.model
    def create(self, der):
        der['department_id'] = self.env.user.department_id.id
        return super(PurchaseRequest, self).create(der)

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('purchase.request')
        return super(PurchaseRequest, self).create(values)

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

    # @api.constrains('request_line_ids', 'state')
    # def _check_request_line_editability(self):
    #     for request in self:
    #         if request.state != 'draft':
    #             if request.request_line_ids:
    #                 raise exceptions.ValidationError("Cannot add or remove request lines when the state is not 'draft'.")

    def export_to_excel(self):
        for line in self:
            output = io.StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow(['Product', 'Quantity', 'Uom'])

            for line in self.request_line_ids:
                csv_writer.writerow([line.product_id.name, line.qty, line.uom_id.name])

            attachment = self.env['ir.attachment'].create({
                'name': 'purchase_request_export.xlsx',
                'datas': base64.b64encode(output.getvalue().encode()),
                'res_model': self._name,
                'res_id': self.id,
            })

            output.close()

            return {
                'name': 'Xuất Excel',
                'type': 'ir.actions.act_url',
                'url': "/web/content/%s?download=true" % attachment.id,
                'target': 'self',
            }
