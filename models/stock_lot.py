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
        return {
            "type": "ir.actions.act_window",
            "name": "Documentos",
            "res_model": "documents.document",
            "view_mode": "kanban,list,form",
            "views": [(False, "kanban"), (False, "list"), (False, "form")],
            "domain": [("name", "=", self.name)],
            "context": {"search_default_name": self.name},
            "target": "current",
        }
