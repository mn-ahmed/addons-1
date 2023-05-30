# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP


class CreditLimitMsgWizard(models.TransientModel):
    _name = 'partner.access.wiz'
    _description = 'Partner Access Rules'
    access_groups = fields.Many2many(comodel_name='res.groups', string="Access Groups", store=True,)

    def action_confirm(self):
        partner_ids = self.env['res.partner'].browse(self._context.get('active_ids', False))
        if not partner_ids:
            return

        vals = {}

        if self.access_groups:
            vals.update({'access_groups': self.access_groups})
        partner_ids.write(vals)
