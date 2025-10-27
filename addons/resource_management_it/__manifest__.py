# Copyright 2015-2017 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Gestão de Equipamentos",
    "version": "14.0.1.0.0",
    "category": "WMS",
    "author": "Victor Bittencourt",
    "license": "AGPL-3",
    "summary": "Faça a gestão de ativos que foram alocados e os seus respectivos alocantes.",
    "depends": ["base", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/it_registry_tree.xml",
        "views/it_resource_item_tree.xml",
        "views/it_employee_view.xml",
        "views/it_management_menu.xml",
    ],
    "demo": [
    ],
    "installable": True,
}