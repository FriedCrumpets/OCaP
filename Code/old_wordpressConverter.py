
rAmpersand = lambda v: v.replace('&amp;', '&')
name = lambda v: v[:99] if len(v) > 99 else v
categories = lambda v: v.split(', ') if v else ['Home']
images_to_list = lambda v: v.split(', ') if v else ''
tax = lambda v: '1' if v == 'taxable' else '2'
special_offer = lambda v: 'Yes' if v == 1 else 'No'#
hidden = lambda v: 'No' if v == 'visible' else 'Yes'

def price(v, *args):
    try: float(v)
    except: return '0'
    return '0' if float(v) < 0 else float(v)

def stock(v, *args):
    try: float(v)
    except: return '0'
    return '0' if float(v) < 0 else round(float(v))

# TODO: redo wordpress
# TODO: variable products have all variants in product row
# TODO: create variations and populate with info as it's found
# TODO: update requires price and other variant information

def create_simple_product_row(header, row, *args):
    product = {k : '' for k in header}

    c = categories(row.get('Categories'))
    categoryPath = 'Home>' + c.pop(0)
    categoryManagement = (':').join(['Home>' + v for v in c]) if c else ''
    imgs = images_to_list(row.get('Images'))

    changes = {
        'Action': 'Add Product',
        'CategoryPath': rAmpersand(categoryPath),
        'Name': name(row.get('Name')),
        'Code': row.get('SKU'),
        'ShortDescription': row.get('Short description'),
        'Description': row.get('Description'),
        'Stock': stock(row.get('Stock')),
        'Weight': row.get('Weight (kg)'),
        'CategoryManagement': rAmpersand(categoryManagement),
        'TaxRateID': tax(row.get('Tax status')),
        'SpecialOffer': special_offer(row.get('Published')),
        'Hidden': hidden(row.get('Visibility in catalogue')),
    }

    images = {f'Image{i+1}': v for i, v in enumerate(imgs) if i < 5}

    sale_price = price(row.get('Sale price'))
    regular_price = price(row.get('Regular price'))
    prices = {
        'Price': sale_price if sale_price != '' else regular_price,
        'RRP': regular_price if sale_price != '' else '',
    }

    product = {**product, **changes, **prices, **images}
    return product, False

def create_variable_product_row(header, row, *args):
    product = {k: '' for k in header}

    c = categories(row.get('Categories'))
    categoryPath = 'Home>' + c.pop(0)
    categoryManagement = (':').join(['Home>' + v for v in c]) if c else ''
    imgs = images_to_list(row.get('Images'))

    changes = {
        'Action': 'Add Product',
        'CategoryPath': rAmpersand(categoryPath),
        'Name': name(row.get('Name')),
        'Code': row.get('SKU'),
        'ShortDescription': row.get('Short description'),
        'Description': row.get('Description'),
        'Stock': stock(row.get('Stock')),
        'Weight': row.get('Weight (kg)'),
        'CategoryManagement': rAmpersand(categoryManagement),
        'TaxRateID': tax(row.get('Tax status')),
        'SpecialOffer': special_offer(row.get('Published')),
        'Hidden': hidden(row.get('is featured?')),
    }

    images = {f'Image{i+1}': v for i, v in enumerate(imgs) if i < 5}
    sale_price = price(row.get('Sale price'))
    regular_price = price(row.get('Regular price'))
    prices = {
        'Price': sale_price if sale_price != '' else regular_price,
        'RRP': regular_price if sale_price != '' else '',
    }

    number_of_variants = 2
    variant_information = {
        'CategoryPath': categoryPath,
        'VariantNames': [
            row.get(f'Attribute {i+1} name') for i in range(number_of_variants)
        ],
        'VariantItems': [
            row.get(f'Attribute {i+1} value(s)').split(',') for i in range(number_of_variants)
        ]
    }

    product = {**product, **changes, **prices, **images}
    return product, variant_information

def create_variation_product_row(header, row, variable_product_info, *args):
    variant = {k: '' for k in header}

    c = categories(row.get('Categories'))
    imgs = images_to_list(row.get('Images'))

    changes = {
        'Action': 'Add Product Variant',
        'Name': name(row.get('Name')),
        'Code': row.get('SKU'),
        'Stock': stock(row.get('Stock')),
        'Weight': row.get('Weight (kg)'),
        'TaxRateID': tax(row.get('Tax status')),
    }

    if not variable_product_info:
        changes['Action'] = 'Add Product'
        changes['CategoryPath'] = 'Home'
        return {**variant, **changes}, False

    variant_names = variable_product_info.get('VariantNames')[0]
    if len(variable_product_info.get('VariantNames')) > 1:
        variant_names = (':').join(variable_product_info.get('VariantNames'))

    variant_information = {
        'CategoryPath': variable_product_info.get('CategoryPath'),
        'VariantNames': variant_names,
    }

    applicable_variations = {
        f'VariantItem{x+1}': row.get(f'Attribute {x+1} value(s)') for x in range(len(variable_product_info.get('VariantNames')))
    }

    images = {f'Image{i+1}': v for i, v in enumerate(imgs) if i < 5}
    sale_price = price(row.get('Sale price'))
    regular_price = price(row.get('Regular price'))
    prices = {
        'Price': sale_price if sale_price != '' else regular_price,
        'RRP': regular_price if sale_price != '' else '',
    }

    variant = {**variant, **changes, **applicable_variations, **variant_information, **prices, **images}
    print(variant)
    return variant, False

def create_fieldnames():
    return [
        'Action', 'ID', 'CategoryPath', 'Name', 'Code',
        'ShortDescription', 'Description',
        'Price', 'RRP', 'Stock', 'Weight', 'CategoryManagement',
        'Image1', 'Image2', 'Image3','Image4', 'Image5',
        'MetaTitle', 'MetaDescription', 'MetaKeywords',
        'TaxRateID', 'SpecialOffer', 'Hidden',
        'VariantNames',
        'VariantItem1', 'VariantItem2', 'VariantItem3', 'VariantItem4',
        'VariantItem5', 'VariantDefault'
    ]

def check_row(row, *args):
    type = row.get('Type')
    return {
        'variable': create_variable_product_row,
        'variation': create_variation_product_row,
        'simple': create_simple_product_row,
    }.get(type, False)

def retrieve_variations(row, variable_product_list):
    product_name = row.get('Name')
    if product_name in variable_product_list:
        return variable_product_list[product_name]
    return None

def convert(file, *args):
    wordpress_header = file.fieldnames
    EKM_Header = create_fieldnames()

    variable_product_list = {}

    converted = []
    for row in file:
        type = check_row(row)
        if not type: continue

        print(row.get('ID'))

        product_variations = retrieve_variations(row, variable_product_list)
        new_row, variant_information = type(EKM_Header, row, product_variations)
        if variant_information:
            variable_product_list[new_row.get('Name')] = variant_information
        converted.append(new_row)

    return converted, EKM_Header
