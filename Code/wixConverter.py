
name = lambda v: v if len(v) < 100 else v[:99]
category = lambda v: f'Home > {v}'
hidden = lambda v: 'yes' if 'TRUE' in v else 'no'
gen = lambda v: v
skip = lambda v: ''
image = lambda v: None

def price(value):
    p = 0
    try:
        p = float(value)
    except:
        pass
    if p < 0:
        return '0'
    return p

def stock(value):
    s = 0
    try:
        s = float(value)
    except:
        pass
    if s < 0:
        return '0'
    return round(s)

match = {
    'name': 'Name',
    'description': 'Description',
    # 'productImageUrl': 'Images',
    'collection': 'CategoryPath',
    'sku': 'Code',
    'price': 'Price',
    'weight': 'Weight',
    'visible': 'Hidden',
    'skip':'skip',
    # ['discountMode', 'discountValue'] : mode is PERCENT OR VALUE. Value is number
    # 'productOptionDescription1': 'OptionItemName',
    # ['productOptionName1', 'customTextField1']: 'OptionName',
    # 'customTextCharLimit1': 'OptionSize',
    # 'customTextManditory1': 'OptionValidation',
    # 'productOptionType1': 'OptionType',
    # 'surcharge': 'OptionItemPriceExtra',
}

dispatch = {
    'CategoryPath': category,
    'Name': name,
    'Code': gen,
    'Description': gen,
    'Price': price,
    'Brand': gen,
    'Stock': stock,
    'Hidden': hidden,
    'Weight': price,
    'MetaTitle': gen, 'MetaDescription': gen, 'MetaKeywords': gen,
    'CategoryManagement': gen,
    'skip':skip
}

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def getFieldNames():
    return [
        'Action', 'ID', 'CategoryPath', 'Name', 'Code', 'Description',
        'Price', 'Brand', 'Stock', 'Hidden', 'Weight',
        'Image1', 'Image2', 'Image3','Image4', 'Image5',
        'MetaTitle', 'MetaDescription', 'MetaKeywords',
        'CategoryManagement',
        'OptionName', 'OptionSize', 'OptionType', 'OptionValidation',
        'OptionItemName', 'OptionItemPriceExtra', 'OptionItemOrder',
    ]

def createProduct(row, fieldnames, imageLink):
    product = {k: '' for k in fieldnames}
    product['Action'] = 'Add Product'

    for k, v in row.items():
        if v == '':
            continue
        product.update(
            {match.get(k, 'skip'): dispatch[match.get(k, 'skip')](saver(v))}
        )

    images = row['productImageUrl'].split(';', 5)
    if len(images) > 5: images.pop()
    for image, index in zip(images, range(len(images))):
        product[f'Image{index+1}'] = f'{imageLink}/{image}'

    product.pop('skip')
    return product

def createOption(row, fieldnames, index, type):
    option = {k: '' for k in fieldnames}

    changes = {
        'Action' : 'Add Product Option',
        'CategoryPath' : f"Home > {row['collection']}",
        'Name' : name(row['name'])
    }

    oItemOrder = lambda i: (':').join([
        '0' for x in i.split(';')
    ])
    oValidation = lambda v: 'NotEmpty' if v == 'TRUE' else ''
    if type == 'drop':
        changes.update({
            'OptionName': row[f'productOptionName{index}'],
            'OptionSize': '240',
            'OptionType': row[f'productOptionType{index}'].replace('_', ''),
            'OptionValidation': '',
            'OptionItemPriceExtra': oItemOrder(row[f'productOptionDescription{index}']),
            'OptionItemName': row[f"productOptionDescription{index}"].replace(';',':'),
            'OptionItemOrder': oItemOrder(row[f'productOptionDescription{index}']),
        })
    elif type == 'text':
        changes.update({
            'OptionName': row[f'customTextField{index}'],
            'OptionSize': row[f'customTextCharLimit{index}'],
            'OptionType': 'TEXT',
            'OptionValidation': oValidation(row[f'customTextMandatory{index}']),
            'OptionItemPriceExtra': '',
            'OptionItemName': '',
            'OptionItemOrder': '',
        })
    return {**option, **changes}

def updateOption(row, oldOption, x):
    index = oldOption['OptionItemName'].split(':').index(row[f'productOptionDescription{x}'])
    priceList = oldOption['OptionItemPriceExtra'].split(':')
    priceList[index] = row['surcharge'] if row['surcharge'] != '' else '0'
    oldOption['OptionItemPriceExtra'] = (':').join(priceList)
    return oldOption

def convert(file, imageLink, *args):
    wix_Header = file.fieldnames
    EKM_Header = getFieldNames()

    converted = []
    product_row = ''

    for row in file:
        type = row['fieldType']

        if type == 'Product':
            converted.append(createProduct(row, EKM_Header, imageLink))
            {converted.append(createOption(row, EKM_Header, x+1, 'drop')) for x in range(len([
                row[f'productOptionName{y+1}'] for y in range(3) if row[f'productOptionName{y+1}'] != ''
            ]))}
            {converted.append(createOption(row, EKM_Header, x+1, 'text')) for x in range(len([
                row[f'customTextField{y+1}'] for y in range(2) if row[f'customTextField{y+1}'] != ''
            ]))}
            product_row = row

        if type == 'Variant':
            for x in range(3):
                if row[f'productOptionDescription{x+1}'] in product_row[f'productOptionDescription{x+1}'].split(';') and row[f'productOptionDescription{x+1}'] != '':
                    # index = product_row[f'productOptionDescription{x+1}'].split(';').index(row[f'productOptionDescription{x+1}']) #index of the option in list
                    index = converted.index(next(r for r in converted if row[f'productOptionDescription{x+1}'] in r['OptionItemName'].split(':')))
                    oldOption = converted.pop(index)
                    updatedOption = updateOption(row, oldOption, x+1)
                    converted.insert(index, updatedOption)
                    continue
                    # {updateOption(r, index, row) for r in converted if r['OptionItemName'] == product_row[f'productOptionDescription{x+1}'].replace(';', ':')}

    return converted, EKM_Header


# so far to my understanding
"""
    each product has product options denoted as variants, but they're actually options
    each option can be created on the product line, but the additional cost must be updated
    via the variant line. If the product row has customTextField{x} they must be
    turned into product options accordingly.
"""
