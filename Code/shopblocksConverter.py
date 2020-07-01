
def create_product_row(row):
    pass

def add_product_attribute(row):
    pass

def add_product_image(row):
    pass

def skip(row):
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
    EKM_Header = createHeader()

    converted = []
    for row in file {
        type = check_type(row)
        if not type: continue

        
    }

# if type and action = product then create product
# if type = product and action = tag then assign attributes to above product
# if type = product and action = image then assign image to product
#
# Category Path is an id of the category name which is listed at the bottom of the sheet.
