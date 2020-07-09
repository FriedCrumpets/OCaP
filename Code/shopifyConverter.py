#! python3
import csv, random, datetime, Errors

name = lambda v: v if len(v) < 100 else v[:99]
gen = lambda v: v
numericValue = lambda v: str(0) if 0 > float(v) or v == '' else v
variantNames = lambda v: v if v != '' else ''
default = lambda v: ''

def categoryPath(value):
    category_list = ['Home'] + value.split(', ')
    while '' in category_list: category_list.pop()
    return (' > ').join(category_list)

def default(value):
    return ''

match = {
    'Title':'Name',
    'Tags':'CategoryPath',
    'Variant SKU': 'Code',
    'Body (HTML)':'Description',
    'Vendor': 'Brand',
    'Variant Price': 'Price',
    'Image Src': 'Image1',
    'Variant Inventory Qty':'Stock',
    'Option1 Name':'VariantNames', 'Option1 Value':'VariantItem1',
    'Option2 Name':'VariantName2', 'Option2 Value':'VariantItem2',
    'Option3 Name':'VariantName3', 'Option3 Value':'VariantItem3',
    'Option4 Name':'VariantName4', 'Option4 Value':'VariantItem4',
    'skip': 'default'
}

dispatch = {
    'Name': name,
    'CategoryPath': categoryPath,
    'Code': gen,
    'Description': gen,
    'Brand': gen,
    'Price': numericValue,
    'Image1': gen,
    'Stock': numericValue,
    'VariantNames': gen,
    'VariantName2': variantNames,
    'VariantName3': variantNames,
    'VariantName4': variantNames,
    'VariantItem1': gen,
    'VariantItem2': gen,
    'VariantItem3': gen,
    'VariantItem4': gen,
    'skip': default
}


def createHeader():
    # If shopify filenames = shopifyEKM, dict = shopify#
    return [
        'Action', 'ID', 'Name', 'CategoryPath', 'Code',
        'Description', 'Brand', 'Price',
        'Image1', 'Image2', 'Image3', 'Image4', 'Image5',
        'Stock',
        'VariantNames',
        'VariantItem1', 'VariantItem2', 'VariantItem3', 'VariantItem4',
    ]

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def createProductVariant(row, fieldnames, product_row=None):

    productVariant = {key: '' for key in fieldnames}
    productVariant['Action'] = 'Add Product Variant'
    # Why are these here? ↓↓↓↓ ???
    productVariant['VariantName2'] = ''
    productVariant['VariantName3'] = ''
    productVariant['VariantName4'] = ''

    if product_row == None: product_row = row

    # loop Variant Row and Product row
    for (k, v), (_, v2) in zip(row.items(), product_row.items()):
        if v2 != '':
            value = saver(v2)
            productVariant[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)
        if v != '':
            value = saver(v)
            productVariant[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)
        vns = []
        try:
            vns.append(productVariant['VariantNames'])
            vns.append(productVariant['VariantName2'])
            vns.append(productVariant['VariantName3'])
            vns.append(productVariant['VariantName4'])
        except KeyError:
            vns.append('')

        new_vns = (':').join(
            [vn for vn in vns if vn != '']
        )
        productVariant['VariantNames'] =  new_vns

        {productVariant.pop(x, None) for x in [
            'VariantName2', 'VariantName3', 'VariantName4', 'Description',
            'Brand', 'skip'
        ]}

        # If the category path has been overridden with nothing ensure it returns to being
        if productVariant['CategoryPath'] == '' and product_row != None:
            productVariant['CategoryPath'] =  categoryPath(product_row['Tags'])
    return productVariant

def createProduct(row, fieldnames):
    # Creates Product row as dictionary sharing fieldnames with the header of the
    # Dictwriter thusly creating a dynamic product row creator

    product = {key: '' for key in fieldnames}
    product['Action'] = 'Add Product'

    # Create placeholder product Variant Incase variant doesn't exist
    productVariant = ''

    for k, v in row.items():
        if v != '':
            value = saver(v)
            product[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)

    if product['VariantItem1'] != '': # product has built in variant
        {product.pop(x, None) for x in [
            'VariantNames', 'VariantName2', 'VariantName3', 'VariantName4',
            'VariantItem1', 'VariantItem2', 'VariantItem3', 'VariantItem4',
            'skip'
        ]}

        productVariant = createProductVariant(row, fieldnames)

    return product, productVariant

def convert(file, *args):
    # Calls all other methods to write to the file this it done individually
    Shopify_header = file.fieldnames
    EKM_header = createHeader()

    # Initialises a blank variable for the previous row & product row
    # Product row initialised with empty handle for easier programming
    product_row = {'Handle':''}

    converted = []

    # Loop the rows in the file
    for row in file:
        # First thing to check handle
        # A blank row is considered a row without a handle & are skipped
        if row['Handle'] == '':
            continue
        # Need to check for product row, variant, or Image row
        # row handle is checked and compared to previous product handle
        if row['Handle'] != product_row['Handle']:
            if len(converted) > 1 and converted[-2]['Action'] == 'Add Product':
                converted[-1]['Action'] = 'Add Product'
                converted[-1]['Description'] = converted[-2]['Description']
                converted.pop(-2)
            product, variant = createProduct(row, EKM_header)
            if variant != '':
                if product['CategoryPath'] != variant['CategoryPath']:
                    product['CategoryPath'] = variant['CategoryPath']
                converted.append(product)
                converted.append(variant)
            else:
                converted.append(product)
            product_row = row
            continue
        # If product handle is same as prior must be image or variant
        else:
            if row['Option1 Value'] != '':
                converted.append(createProductVariant(row, EKM_header, product_row))
                continue
            elif 6 > int(row['Image Position']) > 1: # must be additional image
                x = row['Image Position']
                converted[-1][f'Image{x}'] = row['Image Src']
                continue
            else: # Must be a variant
                continue

    return converted, EKM_header
    # rows are created and assigned to a list. Dict writer loops through the list
    # and writes the rows accordingly
