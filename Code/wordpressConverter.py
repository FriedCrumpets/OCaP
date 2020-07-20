
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

    product = {**product, **changes, **prices, **images}
    variant_list = create_variation_product_rows(header, row, product)
    return product, variant_list

def create_variation_product_rows(header, row, product, *args):
    variant = {k: '' for k in header}

    number_of_variants = 2
    variant_information = {
        'VariantNames': [
            row.get(f'Attribute {i+1} name') for i in range(number_of_variants)
        ],
        'VariantItems': [
            row.get(f'Attribute {i+1} value(s)').split(',') for i in range(number_of_variants)
        ]
    }


    variant_names = variant_information.get('VariantNames')[0]
    if len(variant_information.get('VariantNames')) > 1:
        variant_names = (':').join(variant_information.get('VariantNames'))

    changes = {
        'Action': 'Add Product Variant',
        'SpecialOffer': '',
        'Hidden': '',
        'Description': '',
        'ShortDescription': '',
        'CategoryManagement': '',
        'VariantNames': variant_names
    }

    variant = {**variant, **product, **changes}

    variant_item1 = variant_information.get('VariantItems')[0]
    variant_item2 = variant_information.get('VariantItems')[1]

    variant_list = []
    for v1 in variant_item1:
        for v2 in variant_item2:
            variant_list.append({**variant, **{'VariantItem1': v1.strip(), 'VariantItem2': v2.strip()}})

    return variant_list

def update_variant_product_row(header, row, *args):
    variant = {k: '' for k in header}
    imgs = images_to_list(row.get('Images'))

    changes = {
        'Name': name(row.get('Name')),
        'Code': row.get('SKU'),
        'Stock': stock(row.get('Stock')),
        'Weight': row.get('Weight (kg)'),
        'TaxRateID': tax(row.get('Tax status')),
    }

    images = {f'Image{i+1}': v for i, v in enumerate(imgs) if i < 5}

    sale_price = price(row.get('Sale price'))
    regular_price = price(row.get('Regular price'))

    prices = {
        'Price': sale_price if sale_price != '' else regular_price,
        'RRP': regular_price if sale_price != '' else '',
    }

    variant = {**variant, **changes, **prices, **images}
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
        'variation': update_variant_product_row,
        'simple': create_simple_product_row,
    }.get(type, False)

def get_update_index(converted, row, *args):
    row_variant1 = row.get('Attribute 1 value(s)')
    row_variant2 = row.get('Attribute 2 value(s)')
    print(row_variant1)
    print(row_variant2)
    print([r.get('VariantItem1') for r in converted])
    print([r.get('VariantItem2') for r in converted])
    print(row_variant1 in [r.get('VariantItem1') for r in converted])
    print(row_variant2 in [r.get('VariantItem2') for r in converted])
    match = [r for r in converted if row_variant1 in r.values() and row_variant2 in r.values()].pop()
    return converted.index(match)

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def convert(file, *args):
    wordpress_header = file.fieldnames
    EKM_Header = create_fieldnames()

    variant_lookup = []
    converted = []

    for row in file:
        row = {k: saver(v) for k,v in row.items()}
        type = check_row(row)
        if not type: continue

        new_row, variant_list = type(EKM_Header, row)
        if variant_list: {converted.append(variant) for variant in variant_list}

        if type == update_variant_product_row:
            index = get_update_index(converted, row)
            old_row = converted.pop(index)
            updated_variant = {**old_row, **new_row}
            converted.insert(index, updated_variant)

    return converted, EKM_Header
