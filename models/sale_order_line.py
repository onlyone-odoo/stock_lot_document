from odoo import models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def open_lot_documento_spreadsheet(self):
        """Open the linked document in Spreadsheet from the component lot."""
        self.ensure_one()
        if not self.component_lot_id:
            raise UserError(_("No component lot selected in this line."))
        return self.component_lot_id.open_x_documento_spreadsheet()
