
rAmpersand = lambda v: v.replace('&amp;', '&')
name = lambda v: v[:99] if len(v) > 99 else v
categories = lambda v: v.split(', ') if v else ['Home']
images_to_list = lambda v: v.split(', ') if v else ''
tax = lambda v: '1' if v == 'taxable' else '2'
special_offer = lambda v: 'Yes' if v == 1 else 'No'#
hidden = lambda v: 'No' if v == 'visible' else 'Yes'

def price(v, *args):
    try: float(v)
    except: return 0
    return 0 if float(v) < 0 else float(v)

def stock(v, *args):
    try: float(v)
    except: return 0
    return 0 if float(v) < 0 else round(float(v))

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
        'Price': sale_price if sale_price != '0' else regular_price,
        'RRP': regular_price if sale_price != '0' else '',
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
        'VariableID': row.get('ID'),
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

    sale_price = price(row.get('Meta: _max_variation_sale_price'))
    regular_price = price(row.get('Meta: _max_variation_regular_price'))

    prices = {
        'Price': sale_price if sale_price != 0 else regular_price,
        'RRP': regular_price if sale_price != 0 else '',
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

    variant_names = (':').join(variant_information.get('VariantNames'))
    if variant_names.endswith(':'): variant_names = variant_names[:-1]

    changes = {
        'VariableID': row.get('ID'),
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
    imgs = images_to_list(row.get('Images'))

    changes = {
        'Stock': stock(row.get('Stock')),
        'Weight': row.get('Weight (kg)'),
        'TaxRateID': tax(row.get('Tax status')),
        'VariantItem1': row.get('Attribute 1 value(s)'),
        'VariantItem2': row.get('Attribute 2 value(s)')
    }

    SKU = row.get('SKU')
    if SKU != '': changes['Code'] = SKU

    images = {f'Image{i+1}': v for i, v in enumerate(imgs) if i < 5}

    sale_price = price(row.get('Sale price'))
    regular_price = price(row.get('Regular price'))

    prices = {
        'Price': sale_price if sale_price != 0 else regular_price,
        'RRP': regular_price if sale_price != 0 else '',
    }

    variant = {**changes, **prices, **images}
    return variant, False

def create_fieldnames():
    return [
        'VariableID', 'Action', 'ID', 'CategoryPath', 'Name', 'Code',
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

def get_variant_update_index(converted, row, *args):
    product_id = row.get('Parent')[3:]
    match_ids = [r for r in converted if product_id in r.get('VariableID')]

    row_variant1 = row.get('Attribute 1 value(s)')
    row_variant2 = row.get('Attribute 2 value(s)')
    match_variants = [r for r in converted if row_variant1 in r.values() and row_variant2 in r.values()]

    if not match_variants:
        print(f'no match::\n{row}\n')
        return False
    match = match_variants.pop()
    try:
        index = converted.index(match)
        if converted[index].get('Name') in row.get('Name'):
            return index
        else:
            return False
    except ValueError:
        return False

def get_product_update_index(converted, row, *args):
    product_id = row.get('Parent')[3:]
    match_ids = [r for r in converted if product_id in r.get('VariableID')]
    product_match = [r for r in match_ids if r.get('Action') == 'Add Product']

    if not product_match:
        print(f'no match::\n{row}\n')
        return False
    match = product_match.pop()
    try:
        return converted.index(match)
    except ValueError:
        return False

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def update_variable_product_cell(old_row, new_row, title):
    current = 0 if old_row.get(title) in [None, ''] else float(old_row.get(title))
    competing = 0 if new_row.get(title) in [None, ''] else float(new_row.get(title))
    return competing if competing > current else current

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

        if type == update_variant_product_row:
            index = get_variant_update_index(converted, row)
            if index:
                old_row = converted.pop(index)
                updated_variant = {**old_row, **new_row}
                converted.insert(index, updated_variant)
            index = get_product_update_index(converted, row)
            if index:
                old_row = converted.pop(index)
                updates = {
                    'Price': update_variable_product_cell(old_row, new_row, 'Price'),
                    'RRP': update_variable_product_cell(old_row, new_row, 'RRP'),
                    'Stock': update_variable_product_cell(old_row, new_row, 'Stock'),
                }
                updated_product = {**old_row, **updates}
                converted.insert(index, updated_product)
            continue

        converted.append(new_row)
        if variant_list: {converted.append(variant) for variant in variant_list}

    return converted, EKM_Header
