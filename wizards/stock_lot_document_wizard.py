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
        domain="[('detailed_type', '=', 'product'), ('tracking', 'in', ['serial', 'lot'])]",
    )
    folder_id = fields.Many2one(
        comodel_name="documents.folder",
        string="Folder (optional)",
        help="Select a folder to process only Excels inside it. Leave empty to process all Excels in the system.",
    )

    def action_bulk_convert_and_link(self):
        self.ensure_one()
        domain = [
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
        if self.folder_id:
            domain += [("folder_id", "child_of", self.folder_id.id)]

        # sudo() for documents ops to bypass access rules (safe: only read/convert)
        documents = self.env["documents.document"].sudo().search(domain)
        if not documents:
            raise UserError(_("No Excel documents found."))

        created_lots = 0
        linked_docs = 0
        skipped = 0
        for doc in documents:
            lot_name = doc.name.rsplit(".", 1)[0]  # Strip extension safely
            lot = self.env["stock.lot"].search(
                [("name", "=", lot_name), ("product_id", "=", self.product_id.id)],
                limit=1,
            )
            if not lot and lot.x_documento:
                skipped += 1
                continue

            if not lot:
                lot = self.env["stock.lot"].create(
                    {
                        "name": lot_name,
                        "product_id": self.product_id.id,
                    }
                )
                created_lots += 1

            if doc.mimetype == "application/o-spreadsheet":
                skipped += 1
                continue

            try:
                new_id = doc.sudo().clone_xlsx_into_spreadsheet(archive_source=True)
                if new_id:
                    new_spreadsheet = self.env["documents.document"].browse(new_id)
                    lot.x_documento = new_spreadsheet
                    linked_docs += 1
            except Exception as e:
                skipped += 1
                self.env["bus.bus"]._sendone(
                    self.env.user.partner_id,
                    "simple_notification",
                    {
                        "title": _("Skip"),
                        "message": _(f"Failed for {doc.name}: {str(e)}"),
                        "type": "warning",
                    },
                )

        message = _(
            "%(created)s lots created, %(linked)s linked, %(skipped)s skipped."
        ) % {"created": created_lots, "linked": linked_docs, "skipped": skipped}
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Bulk Completed"),
                "message": message,
                "type": "success" if created_lots + linked_docs > 0 else "info",
                "sticky": False,
            },
        }
