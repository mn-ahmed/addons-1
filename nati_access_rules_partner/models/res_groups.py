from odoo import api, fields, models,_



class ResGroups(models.Model):
    _inherit = "res.groups"

    sequence_access = fields.Char(string="Access Sequence",required=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('sequence_access', 'New') == 'New':
            vals['sequence_access'] = self.env['ir.sequence'].next_by_code('partner.access') or 'New'
        result = super(ResGroups, self).create(vals)
        return result