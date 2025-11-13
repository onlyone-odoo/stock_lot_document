from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64


class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    @api.model
    def _create_spreadsheet_from_excel(self, excel_document_id, send_to_trash=True):
        """Override to link back to stock.lot after conversion."""
        # Call super to create the new spreadsheet
        new_spreadsheet = super()._create_spreadsheet_from_excel(
            excel_document_id, send_to_trash
        )
        # Find related lot by name (assuming unique)
        original_doc = self.browse(excel_document_id)
        lot = self.env["stock.lot"].search([("name", "=", original_doc.name)], limit=1)
        if lot:
            lot.x_documento = new_spreadsheet
        return new_spreadsheet
