from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    it_resource_registry_ids = fields.One2many(
        'it.resource.registry', 'assigned_to', string='Registros de Recursos de TI Atribuídos'
    )