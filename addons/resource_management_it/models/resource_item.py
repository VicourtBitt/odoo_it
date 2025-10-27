from odoo import models, fields

class ItResourceItem(models.Model):
    _name = 'it.resource.item'
    _description = 'Item de Recurso de TI'

    name = fields.Char(string='Nome do Recurso', required=True)
    description = fields.Text(string='Descrição')
    category = fields.Char(string='Categoria')
    revision_frequency = fields.Integer(string='Frequência de Revisão (dias)')
    registry_ids = fields.One2many('it.resource.registry', 'resource_item_id', string='Histórico de Alocações')
    previous_assignees = fields.Many2many('hr.employee', compute='_compute_previous_assignees', string='Usuários Anteriores')
    
    def _compute_previous_assignees(self):
        for record in self:
            assignees = record.registry_ids.filtered(lambda r: r.assigned_to and r.status != 'active').mapped('assigned_to')
            record.previous_assignees = assignees