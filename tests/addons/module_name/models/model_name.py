from odoo import models, fields, api, _


class ModelName(models.Model):
    _inherit = 'model.name'

    no_string_field = fields.Char()
    string_field = fields.Char('Field String')

    def method(self):
        return _('Code')
