from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    first_lot_id = fields.Many2one(
        "stock.lot",
        string="First Lot",
        compute="_compute_first_lot_id",
        store=False,
    )
    lot_x_documento = fields.Many2one(
        "documents.document",
        string="Lot Document",
        related="first_lot_id.x_documento",
        readonly=True,
    )

    @api.depends("lot_ids")
    def _compute_first_lot_id(self):
        for move in self:
            move.first_lot_id = move.lot_ids[0] if move.lot_ids else False

    def open_lot_documento_spreadsheet(self):
        """Delegate to open the linked document in Spreadsheet from the first lot."""
        self.ensure_one()
        if not self.first_lot_id:
            raise UserError(_("No lot selected in this line."))
        return self.first_lot_id.open_x_documento_spreadsheet()
