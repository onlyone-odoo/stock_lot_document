from odoo import fields, models

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    x_documento = fields.Many2one(
        comodel_name="documents.document",
        string="Documento",
        domain="[('name', '=', name)]",
    )

    def open_x_documento_spreadsheet(self):
        self.ensure_one()
        if not self.x_documento:
            return
        try:
            action = self.env.ref("spreadsheet.spreadsheet_action_open").read()[0]
        except ValueError:
            action = {
                "type": "ir.actions.act_window",
                "res_model": "documents.document",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_id": self.x_documento.id,
                "target": "current",
            }
        action["context"] = {
            "active_id": self.x_documento.id,
            "default_res_id": self.x_documento.id,
        }
        return action
