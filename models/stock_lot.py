from odoo import fields, models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    x_documento = fields.Many2one(
        comodel_name='documents.document',
        string='Documento',
        domain="[('name', '=', name)]"
    )

    def open_x_documento(self):
        self.ensure_one()
        if not self.x_documento:
            return
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.x_documento.id,
            'target': 'current',  # Abre en la ventana actual, como en Kanban
        }