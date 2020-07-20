
def create_fieldnames():
    return [
        'Action', 'ID', 'CategoryPath', 'Name', 'Code', 'Description',
        'Price', 'Brand', 'Stock', 'Hidden', 'Weight', 'CategoryManagement',
        'Image1', 'Image2', 'Image3','Image4', 'Image5',
        'MetaTitle', 'MetaDescription', 'MetaKeywords',
    ]

def numeric_type(func):
    


def numeric(v, type):
    p = 0
    try:
        p = float(v)
    except:
        pass
    if  < 0:
        return '0'
    return p

def create_product_row(header, row):
    product = {k: '' for k in header}

    name = lambda v: v if len(v) < 100 else v[:99]


    changes = {
        'Action': 'Add Product',
        'CategoryPath': row.get('Category Path'),
        'Name': name(row.get('Name')),
        'Code': row.get('SKU'),
        'Description': row.get('Long Description'),
        'Price': price(row.get('Price')),
        'Stock':
        'Attribute:MPN' row.get('MPN')
    }

def add_product_attribute(header, row):
    pass

def add_product_image(header, row):
    pass

def skip(*args):
    pass

def check_type(row):
    type = row.get('Type')
    action = row.get('Action')

    return {
        'Product;Product': create_product_row,
        'Product;Tag': add_product_attribute,
        'Product;Image': add_product_image,
        'Product;Variant': skip
    }.get(f'{type};{action}', None)

def convert(file, *args):
    shopBlocks_header = file.fieldnames
    EKM_Header = create_fieldnames()

    converted = []
    for row in file {
        type = check_type(row)
        if not type: continue

        type(EKM_Header, row)
    }

# if type and action = product then create product
# if type = product and action = tag then assign attributes to above product
# if type = product and action = image then assign image to product
#
# Category Path is an id of the category name which is listed at the bottom of the sheet.
