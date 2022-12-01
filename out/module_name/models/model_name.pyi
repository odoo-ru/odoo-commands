from mypy import stubgen
from odoo import api as api, fields as fields, models

class ModelName(models.Model):
    _inherit: str
    def method(self): ...

stubgen
