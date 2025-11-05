from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)

class ItResourceRegistry(models.Model):
    _name = 'it.resource.registry'
    _description = 'Registro de Recursos de TI'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(string='Nome do Registro', required=True, compute='_compute_name', store=True, readonly=False)
    resource_item_id = fields.Many2one('it.resource.item', string='Item de Recurso de TI', required=True, tracking=True)
    assigned_to = fields.Many2one('hr.employee', string='Atribuído a', required=True, tracking=True)
    allocation_date = fields.Datetime(string='Data de Alocação', default=fields.Datetime.now, tracking=True)
    return_date = fields.Datetime(string='Data de Devolução', tracking=True)
    observation = fields.Text(string='Observação')
    employee_signature = fields.Binary(string='Assinatura do Funcionário', copy=False)
    has_been_accepted = fields.Boolean(string='Aceito pelo Funcionário', default=False, copy=False)
    has_been_neglected = fields.Boolean(string='Negligenciado pelo Funcionário', default=False, copy=False)
    has_been_revoked = fields.Boolean(string='Revogado', default=False, copy=False)
    has_been_returned = fields.Boolean(string='Devolvido', default=False, copy=False)
    status = fields.Selection([
        ('active', 'Ativo'),
        ('interrupted', 'Interrompido'),
        ('rejected', 'Rejeitado'),
        ('revoked', 'Revogado'),
        ('awaiting_signature', 'Aguardando Assinatura'),
        ('returned', 'Devolvido')
    ], string='Status', default='awaiting_signature', readonly=True, tracking=True) 

    def _compute_if_returned(self):
        for record in self:
            if record.return_date and record.return_date <= fields.Datetime.now():
                record.status = 'returned' 

    def mark_as_returned(self):
        for record in self:
            record.return_date = fields.Datetime.now()
            record.status = 'returned' 

    @api.depends('resource_item_id', 'assigned_to')
    def _compute_name(self):
        for record in self:
            if record.resource_item_id and record.assigned_to:
                record.name = f"{record.resource_item_id.name} - {record.assigned_to.name}"
            else:
                record.name = "Novo Registro"

    @api.constrains('return_date', 'allocation_date', "employee_signature")
    def _check_dates_and_signature(self):
        pass 

    def _get_partner_recipients(self):
        """
        Helper para obter os parceiros para envio de email.
        Retorna uma lista de IDs de res.partner.
        """
        self.ensure_one()
        recipients = []
        if self.assigned_to and self.assigned_to.user_id and self.assigned_to.user_id.partner_id:
            recipients.append(self.assigned_to.user_id.partner_id.id)
        if self.create_uid and self.create_uid.partner_id:
            recipients.append(self.create_uid.partner_id.id)
        
        return list(set(recipients))

    # --- Funções de Envio de Email (COM A CORREÇÃO) ---

    def _send_creation_email(self):
        """Envia email de criação."""
        for record in self:
            try:
                template = record.env.ref('resource_management_it.email_template_it_registry_created')
                partner_ids = record._get_partner_recipients()
                if template and partner_ids:
                    # CORREÇÃO: Passar recipients via email_values
                    email_values = {'recipient_ids': [(6, 0, partner_ids)]}
                    template.send_mail(record.id, force_send=True, email_values=email_values)
            except Exception as e:
                _logger.error(f"Erro ao enviar email de criação para o registro {record.id}: {e}")

    def _send_accepted_email(self):
        """Envia email de aceite com PDF."""
        for record in self:
            try:
                template = record.env.ref('resource_management_it.email_template_it_registry_accepted')
                partner_ids = record._get_partner_recipients()
                if template and partner_ids:
                    # CORREÇÃO: Passar recipients via email_values
                    email_values = {'recipient_ids': [(6, 0, partner_ids)]}
                    template.send_mail(record.id, force_send=True, email_values=email_values)
            except Exception as e:
                _logger.error(f"Erro ao enviar email de aceite para o registro {record.id}: {e}")

    def _send_rejected_email(self):
        """Envia email de recusa."""
        for record in self:
            try:
                template = record.env.ref('resource_management_it.email_template_it_registry_rejected')
                partner_ids = record._get_partner_recipients()
                if template and partner_ids:
                    # CORREÇÃO: Passar recipients via email_values
                    email_values = {'recipient_ids': [(6, 0, partner_ids)]}
                    template.send_mail(record.id, force_send=True, email_values=email_values)
            except Exception as e:
                _logger.error(f"Erro ao enviar email de recusa para o registro {record.id}: {e}")

    def _send_revoked_email(self):
        """Envia email de revogação com PDF."""
        for record in self:
            try:
                template = record.env.ref('resource_management_it.email_template_it_registry_revoked')
                partner_ids = record._get_partner_recipients()
                if template and partner_ids:
                    # CORREÇÃO: Passar recipients via email_values
                    email_values = {'recipient_ids': [(6, 0, partner_ids)]}
                    template.send_mail(record.id, force_send=True, email_values=email_values)
            except Exception as e:
                _logger.error(f"Erro ao enviar email de revogação para o registro {record.id}: {e}")

    # --- Métodos Create e Write ---

    @api.model
    def create(self, vals):
        if vals.get('employee_signature') and not vals.get('allocation_date'):
            raise exceptions.UserError("Para assinar, o recurso deve primeiro ser alocado.")
        
        if vals.get('employee_signature'):
            raise exceptions.UserError("O recurso deve ser alocado antes de ser assinado pelo funcionário.")
        
        record = super(ItResourceRegistry, self).create(vals)
        record._send_creation_email()
        return record

    def write(self, vals):
        old_statuses = {rec.id: rec.status for rec in self}
        
        for record in self:
            return_date = vals.get('return_date', record.return_date)
            allocation_date = vals.get('allocation_date', record.allocation_date)
            employee_signature = vals.get('employee_signature', record.employee_signature)

            if record.status == "returned":
                raise exceptions.UserError("Um recurso devolvido não pode ser modificado.")

            if return_date and not allocation_date:
                raise exceptions.UserError("Para devolver um recurso, ele primeiro deve ser alocado.")
            if not employee_signature and allocation_date:
                pass

            if "return_date" in vals or vals.get("has_been_returned"):
                if "return_date" >= fields.Datetime.now() or vals.get("has_been_returned"):
                    vals["status"] = "returned"
                    vals["has_been_returned"] = True

            elif "employee_signature" in vals:
                if allocation_date:
                    vals["status"] = "active"
                    vals["has_been_accepted"] = True
            
            elif vals.get("has_been_neglected"):
                if not allocation_date:
                    raise exceptions.UserError("Para negligenciar um recurso, ele primeiro deve ser alocado.")
                vals["status"] = "rejected"
                vals["has_been_neglected"] = True 
            
            elif vals.get("has_been_revoked"):
                if not allocation_date:
                    raise exceptions.UserError("Para revogar um recurso, ele primeiro deve ser alocado.")
                vals["status"] = "revoked"
                vals["has_been_revoked"] = True 

        res = super(ItResourceRegistry, self).write(vals)

        for record in self:
            old_status = old_statuses.get(record.id)
            new_status = record.status
            
            if old_status != new_status:
                _logger.info(f"Registro {record.id} mudou de status: {old_status} -> {new_status}")
                if new_status == 'active':
                    record._send_accepted_email()
                elif new_status == 'rejected':
                    record._send_rejected_email()
                elif new_status == 'revoked':
                    record._send_revoked_email()

        return res