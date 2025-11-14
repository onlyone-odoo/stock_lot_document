from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLotDocumentWizard(models.TransientModel):
    _name = "stock.lot.document.wizard"
    _description = (
        "Wizard for Bulk Create Lots, Convert Excels to Spreadsheets and Link"
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain="[('type', '=', 'product')]",  # Assume serial-tracked products
        help="The product to assign to all new lots created from the files.",
    )
    folder_id = fields.Many2one(
        comodel_name="documents.folder",
        string="Folder",
        required=True,
        help="Select the folder containing the Excel documents to process and link.",
    )

    def action_bulk_convert_and_link(self):
        """For each Excel in the folder: Create lot if not exists, convert to Spreadsheet, and link to lot."""
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Please select a product."))
        documents = self.env["documents.document"].search(
            [
                ("folder_id", "child_of", self.folder_id.id),
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

        created_lots = 0
        linked_docs = 0
        skipped = 0
        for doc in documents:
            lot_name = doc.name.replace(".xlsx", "").replace(
                ".xls", ""
            )  # Strip extension for lot name
            if not lot_name:
                skipped += 1
                continue

            # Search existing lot by name and product (unique combo)
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", lot_name),
                    ("product_id", "=", self.product_id.id),
                ],
                limit=1,
            )

            if not lot:
                # Create new lot
                lot = self.env["stock.lot"].create(
                    {
                        "name": lot_name,
                        "product_id": self.product_id.id,
                        "ref": lot_name,  # Optional: Use as internal ref
                    }
                )
                created_lots += 1

            # Skip if already a Spreadsheet (domain filters, but double-check)
            if doc.mimetype == "application/o-spreadsheet":
                skipped += 1
                continue

            # Convert to Spreadsheet (archive original)
            try:
                new_spreadsheet_id = doc.clone_xlsx_into_spreadsheet(
                    archive_source=True
                )
                if new_spreadsheet_id:
                    new_spreadsheet = self.env["documents.document"].browse(
                        new_spreadsheet_id
                    )
                    if not lot.x_documento:  # Link only if not already linked
                        lot.x_documento = new_spreadsheet
                        linked_docs += 1
                else:
                    skipped += 1
            except Exception as e:
                skipped += 1
                # Optional: Log per-doc error, but continue batch
                self.env["bus.bus"]._sendone(
                    self.env.user.partner_id,
                    "simple_notification",
                    {
                        "title": _("Conversion Skipped"),
                        "message": _(f"Failed for {doc.name}: {str(e)}"),
                        "type": "warning",
                    },
                )

        message = _(
            "%(created)s lots created, %(linked)s documents linked, %(skipped)s skipped.",
            created=created_lots,
            linked=linked_docs,
            skipped=skipped,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Bulk Processing Completed"),
                "message": message,
                "sticky": False,
                "type": "success" if created_lots + linked_docs > 0 else "warning",
            },
        }
