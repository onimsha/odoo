{
    'name': 'Product Barcodes',
    'version': '1.0',
    'category': 'Hidden/Dependency',
    'summary': 'Gen Barcodes',
    'description': """
This module adds support for gen barcode for product.
""",
    'depends': ['product'],
    'data': [
        'views/product_view.xml',
        'views/report_productlabel.xml',
    ],
    'installable': True,
    'auto_install': False,
}
