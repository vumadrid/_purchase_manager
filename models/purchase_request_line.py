from random import random
from odoo import fields, models, api, exceptions, _
import csv
import io
import base64
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

class PurchaseRequestLine(models.Model):
      _name = 'purchase.request.line'
      _description = 'Purchase Request Line'

      request_id = fields.Many2one('purchase.request', string="Purchase Request", readonly=True, ondelete='cascade')
      product_id = fields.Many2one('product.template', string="Product", readonly=True, required=True)
      uom_id = fields.Many2one('uom.uom', string="Unit of Measure", required=True)
      qty = fields.Float(string="Quantity", default=1.0)
      state = fields.Selection([
            ('request', 'Request Approval'),
            ('draft', 'Draft'),
            ('wait', 'Waiting Approval'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
      ], string="State", default='draft', readonly=True, copy=False, Tracking=True, track_visibility='onchange')
      qty_approve = fields.Float(string="Approved Quantity", readonly=False)
      price_unit = fields.Float(string="Unit Price")
      total = fields.Float(string="Total", compute='_compute_total', store=True)

      @api.depends('qty_approve', 'price_unit')
      def _compute_total(self):
          for line in self:
              line.total = line.qty_approve * line.price_unit


      # @api.onchange('qty_approve')
      # def _onchange_qty_approve(self):
      #     if self.state == 'wait':
      #         return
      #     else:
      #         self.qty_approve = self._origin.qty_approve
      #
      # @api.constrains('qty_approve')
      # def _check_qty_approve(self):
      #     for line in self:
      #         if line.state == 'wait' and line.qty_approve < 0:
      #             raise exceptions.ValidationError("Approved quantity cannot be negative when the request is in 'wait' state.")




