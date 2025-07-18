# License AGPL-3.0 or later[](https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Lot Document Link",
    "summary": """
        Añade un campo para enlazar documentos con el mismo nombre en lotes de stock y un botón para abrirlos.""",
    "author": "Be OnlyOne",
    "maintainers": ["onlyone-odoo"],
    "website": "https://onlyone.odoo.com/",
    "license": "AGPL-3",
    "category": "Inventory",
    "version": "17.0.2.1.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["stock", "documents", "spreadsheet"],
    "data": [
        "views/stock_lot_form.xml",
    ],
}
