from odoo import api, fields, models, exceptions

class GenericRegistry(models.Model):
    _name = "generic.registry"
    _description = "Generic Registry"

    name = fields.Char(string="Registry Name")
    assigned_to = fields.Many2one('hr.employee', string="Assigned To", tracking=True, required=True)
    observation = fields.Text(string="Observation", tracking=True)
    allocation_date = fields.Date(string="Allocation Date", tracking=True)
    retrieval_date = fields.Date(string="Retrieval Date", tracking=True)
    has_been_accepted = fields.Boolean(string="Has Been Accepted", default=False, tracking=True)
    has_been_revoked = fields.Boolean(string="Has Been Revoked", default=False, tracking=True)
    has_been_returned = fields.Boolean(string="Has Been Returned", default=False, tracking=True)
    assigned_signature = fields.Binary(string="Assigned Signature", copy=False)
    status = fields.Selection([('active', 'Active'),
                               ('revoked', 'Revoked'),
                               ('returned', 'Returned'),
                               ('awaiting_signature', 'Awaiting Signature')], 
                               string="Status", default='awaiting_signature',
                               tracking=True)
    

    def write(self, vals):
        old_status = {rec.id: rec.status for rec in self}
        for record in self:
            retrieval_date = vals.get('retrieval_date', record.retrieval_date)
            allocation_date = vals.get('allocation_date', record.allocation_date)
            assigned_signature = vals.get('assigned_signature', record.assigned_signature)

            if record.status == 'returned' :
                raise exceptions.UserError("Cannot modify a Registry that has been returned.")
            
            if retrieval_date:
                if not allocation_date:
                    raise exceptions.UserError("Allocation date must be set before setting retrieval date.")
                
                if retrieval_date < allocation_date:
                    raise exceptions.UserError("Retrieval date cannot be before allocation date.")
                
                vals['status'] = 'returned'
                vals['has_been_returned'] = True

            if assigned_signature:
                if not allocation_date or retrieval_date:
                    raise exceptions.UserError("Allocation/Retrieval date must be set before adding a signature.")
                vals['status'] = 'awaiting_signature'

        res = super(GenericRegistry, self).write(vals)

        for record in self:
            if old_status[record.id] != record.status:
                record.message_post(body=f"Status changed from {old_status[record.id]} to {record.status}")            

        return res