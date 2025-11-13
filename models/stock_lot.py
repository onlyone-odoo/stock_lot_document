from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLot(models.Model):
    _inherit = "stock.lot"

    x_documento = fields.Many2one(
        comodel_name="documents.document",
        string="Document",
        domain="[('name', '=', name), ('mimetype', 'in', ['application/o-spreadsheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'])]",
        help="Linked document (Spreadsheet or Excel) with the same name as the lot.",
    )
    x_excel_file = fields.Binary(
        string="Upload Excel",
        attachment=False,
        help="Temporary field to upload an Excel file, which will be converted to a document.",
    )
    x_excel_filename = fields.Char(string="Excel Filename")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):
            record._handle_uploaded_excel(vals)
        return records

    def write(self, vals):
        res = super().write(vals)
        self._handle_uploaded_excel(vals)
        return res

    def _handle_uploaded_excel(self, vals):
        """Handle uploaded Excel file: create a document and link it."""
        if "x_excel_file" not in vals or not vals["x_excel_file"]:
            return
        self.ensure_one()
        if self.x_documento:
            raise UserError(
                _(
                    "A document is already linked. Please remove it before uploading a new one."
                )
            )
        # Create attachment from binary
        attachment_vals = {
            "name": self.x_excel_filename or f"{self.name}.xlsx",
            "res_model": "documents.document",
            "res_id": 0,
            "datas": vals["x_excel_file"],
            "type": "binary",
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        attachment = self.env["ir.attachment"].create(attachment_vals)
        # Create document
        document_vals = {
            "name": self.name,
            "attachment_id": attachment.id,
            "folder_id": False,  # Adjust if you want a specific folder
        }
        document = self.env["documents.document"].create(document_vals)
        self.x_documento = document

    def open_x_documento_spreadsheet(self):
        """Open the linked document in preview mode to trigger Spreadsheet if possible."""
        self.ensure_one()
        if not self.x_documento:
            raise UserError(_("No document linked to this lot."))
        doc = self.x_documento
        if doc.mimetype == "application/o-spreadsheet":
            # Direct open in Spreadsheet
            return {
                "type": "ir.actions.client",
                "tag": "spreadsheet",
                "params": {
                    "spreadsheet_id": doc.id,
                },
                "target": "current",
            }
        else:
            # Open in kanban view for single doc to trigger preview dialog (conversion prompt for Excel)
            return {
                "type": "ir.actions.act_window",
                "name": _("Document"),
                "res_model": "documents.document",
                "view_mode": "kanban",
                "views": [(False, "kanban")],
                "domain": [("id", "=", doc.id)],
                "context": {},
                "target": "current",
            }
