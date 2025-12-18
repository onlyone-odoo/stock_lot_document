from odoo import models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def open_lot_documento_spreadsheet(self):
        """Delegate to open the linked document in Spreadsheet from the lot."""
        self.ensure_one()
        if not self.lot_id:
            raise UserError(_("No lot selected in this line."))
        return self.lot_id.open_x_documento_spreadsheet()
