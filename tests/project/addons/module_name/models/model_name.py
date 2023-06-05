from odoo import models, fields, _


class ModelName3(models.Model):
    _name = 'model.name.3'
    _description = 'Model Description'

    name_1 = fields.Char()
    name_2 = fields.Char('Field String')
    name_3 = fields.Char(string='Field String')
    name_4 = fields.Char(help='Help')
    html = fields.Html()

    def method(self):
        return _('Code')
