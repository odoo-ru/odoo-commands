from odoo import models, fields, api, _


class ModelName(models.Model):
    _inherit = 'model.name'

    def method(self):
        return _('Code')
