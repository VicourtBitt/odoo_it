from odoo import models, fields, api

class ItResourceRegistry(models.Model):
    _name = 'it.resource.registry'
    _description = 'Registro de Recursos de TI'

    name = fields.Char(string='Nome do Registro', required=True)
    resource_item_id = fields.Many2one('it.resource.item', string='Item de Recurso de TI', required=True)
    assigned_to = fields.Many2one('hr.employee', string='Atribuído a')
    allocation_date = fields.Datetime(string='Data de Alocação', default=fields.Datetime.now)
    return_date = fields.Datetime(string='Data de Devolução')
    status = fields.Selection([
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('maintenance', 'Em Manutenção')
    ], string='Status', default='active')

    def _compute_if_returned(self):
        for record in self:
            if record.return_date and record.return_date <= fields.Datetime.now():
                record.status = 'inactive'

    def mark_as_returned(self):
        for record in self:
            record.return_date = fields.Datetime.now()
            record.status = 'inactive'