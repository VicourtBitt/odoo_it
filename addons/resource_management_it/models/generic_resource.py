from odoo import models, fields, api, exceptions

class GenericResource(models.Model):
    _name = "generic.resource"
    _description = "Generic Resource"

    name = fields.Char(string="Resource Name", required=True)
    description = fields.Text(string="Description", tracking=True)
    category = fields.Char(string="Category", tracking=True)
    revision_frequency = fields.Selection([('daily', 'Daily'),
                                           ('weekly', 'Weekly'),
                                           ('monthly', 'Monthly'),
                                           ('yearly', 'Yearly')],
                                          string="Revision Frequency", tracking=True)