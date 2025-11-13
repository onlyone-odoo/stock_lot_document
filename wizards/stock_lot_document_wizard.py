from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLotDocumentWizard(models.TransientModel):
    _name = "stock.lot.document.wizard"
    _description = "Wizard for Bulk Convert Excels to Spreadsheets and Link to Lots"

    folder_id = fields.Many2one(
        comodel_name="documents.folder",
        string="Folder",
        required=True,
        help="Select the folder containing the Excel documents to convert and link.",
    )

    def action_bulk_convert_and_link(self):
        """Convert all Excel documents in the selected folder to Spreadsheets and link to matching stock lots."""
        self.ensure_one()
        documents = self.env["documents.document"].search(
            [
                (
                    "folder_id",
                    "child_of",
                    self.folder_id.id,
                ),  # Include subfolders if any
                (
                    "mimetype",
                    "in",
                    [
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.ms-excel",
                    ],
                ),
                ("type", "=", "binary"),
            ]
        )
        if not documents:
            raise UserError(_("No Excel documents found in the selected folder."))

        converted_count = 0
        for doc in documents:
            # Convert to Spreadsheet (send_to_trash=True to move original to trash)
            new_spreadsheet = doc._create_spreadsheet_from_excel(
                doc.id, send_to_trash=True
            )
            if new_spreadsheet:
                # Link to stock.lot by name (assuming unique)
                lot = self.env["stock.lot"].search([("name", "=", doc.name)], limit=1)
                if lot:
                    lot.x_documento = new_spreadsheet
                    converted_count += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Bulk Conversion Completed"),
                "message": _("%s documents converted and linked successfully.")
                % converted_count,
                "sticky": False,
                "type": "success",
            },
        }
