from odoo import models, fields, api, _


class ModelName(models.Model):
    _inherit = 'model.name'

    name_1 = fields.Char()
    name_2 = fields.Char('Field String')
    name_3 = fields.Char(string='Field String')
    name_4 = fields.Char(help='Help')

    def method(self):
        return _('Code')
