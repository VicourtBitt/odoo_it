from odoo import fields, models, api

class ItResourceRequest(models.Model):
    _name = "it.resource.request"
    _description = "Solicitação de Recurso de TI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Descrição da Solicitação", required=True)
    requester_id = fields.Many2one("hr.employee", string="Solicitante", required=True)
    designed_employee_id = fields.Many2one("hr.employee", string="Funcionário Designado")
    description = fields.Text(string="Detalhes da Solicitação")
    request_date = fields.Datetime(string="Data da Solicitação", default=fields.Datetime.now)
    need_approval_of = fields.Many2one("hr.employee", string="Necessita Aprovação de", domain="[('id', '!=', requester_id), ('id', '!=', designed_employee_id)]")
    has_approval = fields.Boolean(string="Aprovado", default=False)
    approval_date = fields.Datetime(string="Data de Aprovação")
    state = fields.Selection([
        ("to_approve", "Aguardando Aprovação"),
        ("approved", "Aprovado"),
        ("done", "Concluído"),
        ("cancelled", "Cancelado")
    ], string="Estado", default="to_approve")

    def action_approve(self):
        for record in self:
            record.state = "approved"
            record.has_approval = True
            record.approval_date = fields.Datetime.now()

    def action_cancel(self):
        for record in self:
            record.state = "cancelled"

    def action_complete(self):
        for record in self:
            record.state = "done"