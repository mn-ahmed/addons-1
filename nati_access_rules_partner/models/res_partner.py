from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import re
import phonenumbers



class ResPartner(models.Model):
    _inherit = "res.partner"


    def _default_access_group(self):
        thisuser = self.env.user
        domain = [("category_id.name", "=", "PartnerAccess"),]
        domain += [("users", "=", thisuser.name), ]
        groups = thisuser.groups_id.search(domain, limit=1, order="sequence_access asc")
        return groups

    access_groups = fields.Many2many(default=_default_access_group, comodel_name='res.groups',string="Access Group", store=True,)
    same_mobile_partner_id = fields.Many2one('res.partner', string='Partner with same Mobile NO', compute='_compute_same_mobile_partner_id', store=False)
    crn = fields.Char('CRN', help="Commercial Registration No")
    same_crn_partner_id = fields.Many2one('res.partner', string='Partner with same CRN', compute='_compute_same_crn_partner_id', store=False)

    @api.constrains('mobile','phone')
    def _constrains_mobile(self):
        if self.mobile:
            try:
                mob= phonenumbers.parse(self.mobile, None)
            except:
                raise ValidationError(_('Invalid Mobile Country.'))
        if self.phone:
            try:
                mob= phonenumbers.parse(self.phone, None)
            except:
                raise ValidationError(_('Invalid phone Country.'))

    @api.depends('mobile', 'company_id')
    def _compute_same_mobile_partner_id(self):
        for partner in self:
            partner_id = partner._origin.id
            #active_test = False because if a partner has been deactivated you still want to raise the error,
            #so that you can reactivate it instead of creating a new one, which would loose its history.
            Partner = self.with_context(active_test=False).sudo()
            domain = [
                ('mobile', '=', partner.mobile),
                ('company_id', 'in', [False, partner.company_id.id]),
            ]
            if partner_id:
                domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
            partner.same_mobile_partner_id = bool(partner.mobile) and not partner.parent_id and Partner.search(domain, limit=1)

    @api.depends('crn', 'company_id')
    def _compute_same_crn_partner_id(self):
        for partner in self:
            partner_id = partner._origin.id
            Partner = self.with_context(active_test=False).sudo()
            domain = [
                ('crn', '=', partner.crn),
                ('company_id', 'in', [False, partner.company_id.id]),
            ]
            if partner_id:
                domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
            partner.same_crn_partner_id = bool(partner.crn) and not partner.parent_id and Partner.search(domain, limit=1)

    trackingaccessgroups = fields.Char(string="Access Group", tracking=True)

    @api.onchange('access_groups')
    def msgpost(self):
        msg = ''
        for access in self.access_groups:
            msg += access.name + ','
        self.write({'trackingaccessgroups': msg})
