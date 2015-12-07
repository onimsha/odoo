# -*-coding:utf-8-*-
import logging

from openerp.osv import osv, fields

log = logging.getLogger(__name__)


class product_product(osv.osv):
    _inherit = 'product.product'
    _description = 'Product Variants'

    def create(self, cr, uid, vals, context=None):
        res_id = super(product_product, self).create(cr, uid, vals, context)
        if not vals.get('barcode', False):
            self.gen_barcode(cr, uid, res_id, 1, context=context)
        return res_id

    def gen_barcode(self, cr, uid, prod_id, index, context=None):
        if context is None:
            context = {}
        res = False
        context.update({'active_test': False})
        prod_attr_obj = self.pool.get('product.attribute.value')
        color = 0
        attr_color_ids = prod_attr_obj.search(cr, uid, [('name', '=', 'Color')], order='sequence desc', limit=1)
        if attr_color_ids:
            attr_color = prod_attr_obj.browse(cr, uid, attr_color_ids[0], context=context)
            color = attr_color.sequence + 1
        size = 0
        attr_size_ids = prod_attr_obj.search(cr, uid, [('name', '=', 'Size')], order='sequence desc', limit=1)
        if attr_size_ids:
            attr_size = prod_attr_obj.browse(cr, uid, attr_size_ids[0], context=context)
            size = attr_size.sequence + 1

        if prod_id:
            res_prod = self.browse(cr, uid, prod_id, context=context)
            list_attr = {'Color': [], 'Size': []}
            for attr in res_prod.attribute_value_ids:
                if attr.attribute_id.name == 'Color':
                    list_attr['Color'].append(attr.sequence)
                if attr.attribute_id.name == 'Size':
                    list_attr['Size'].append(attr.sequence)
            if len(list_attr['Color']) == 1:
                color = list_attr['Color'][0]
            if len(list_attr['Size']) == 1:
                size = list_attr['Size'][0]

            if res_prod.categ_id or res_prod.pos_categ_id:
                next_sequence = 1
                if res_prod.pos_categ_id:
                    suffix = res_prod.pos_categ_id.complete_code
                    args = [('pos_categ_id', '=', res_prod.pos_categ_id.id), ('id', '!=', prod_id)]
                else:
                    suffix = res_prod.categ_id.complete_code
                    args = [('categ_id', '=', res_prod.categ_id.id), ('id', '!=', prod_id)]
                prods = self.search(cr, uid, args, order='sequence desc', limit=1, context=context)
                if prods:
                    res_prod = self.browse(cr, uid, prods[0], context=context)
                    next_sequence = res_prod.sequence + 1
                if suffix:
                    barcode = "%s%.2d%.2d%.5d" % (suffix, color, size, next_sequence)
                    bar_chk = self.pool.get('barcode.nomenclature')
                    checksum = bar_chk.ean_checksum("%s0" % barcode)
                    barcode = "%s%s" % (barcode, checksum)
                    res = self.write(cr, uid, [prod_id], {'sequence': next_sequence, 'barcode': barcode})
        return res

product_product()


class product_category(osv.osv):

    def get_complete_code(self, cr, uid, cat, context=None):
        res = ""
        while cat:
            res = (cat.sequence and str(cat.sequence) or "0") + res
            cat = cat.parent_id
        return res

    def _get_complete_code(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = self.get_complete_code(cr, uid, item, context=context)
        return res

    _inherit = "product.category"
    _description = "Product Category"
    _columns = {
        'complete_code': fields.function(_get_complete_code, type="char", string='Name'),
    }

product_category()