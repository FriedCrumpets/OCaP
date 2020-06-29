import re

def name(value, *args):
    if len(value) > 99:
        return value[:99]
    return value

def category(value, *args):
    if value == '':
        return 'Home'
    else:
        return 'Home > ' + value

def num(value, *args):
    try:
        if value == '' or round(float(value)) < 0:
            return '0'
        return round(float(value))
    except ValueError:
        return '0'

def image(value, imageLink, *args):
    return f'{imageLink}{value}.jpg'

def tax(value, *args):
    if value == 'YES': return 1
    return 2

def gen(value, *args):
    return value

def skip(value, *args):
    return ''

match = {
    'CODE' : 'Code',
    'TITLE' : 'Name',
    'PRICE' : 'Price',
    'CATEGORY' : 'CategoryPath',
    'SECONDARY CATEGORY' : 'CategoryManagement',
    'DESCRIPTION': 'Description',
    'IMAGE' : 'Image1', #images don't show file type, need image link + file type (assume jpg)
    'IMAGE 2': 'Image2',
    'IMAGE 3': 'Image3',
    'VAT': 'TaxRateID' # yes = 1; no = 2.
}

dispatch = {
    'Code' : gen,
    'Name' : name,
    'Price': num,
    'CategoryPath': category,
    'CategoryManagement': category,
    'Description': gen,
    'Image1': image,
    'Image2': image,
    'Image3': image,
    'TaxRateID': tax,
    'skip': skip
}

def createHeader():
    # cShop fieldnames
    return [
        'Action', 'ID', 'Name', 'CategoryPath', 'CategoryManagement',
        'Code', 'Description', 'Price',
        'Image1', 'Image2', 'Image3', 'TaxRateID',
        'OptionName', 'OptionSize', 'OptionType', 'OptionValidation',
        'OptionItemName', 'OptionItemPriceExtra', 'OptionItemOrder'
    ]

def saver(string):
    if not string: return
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def attributes(row, attribute_set):
    attributeList = [attr for attr in attribute_set.split(';') if attr in row.keys()]
    if len(attributeList) < 1: return {'':''}
    # c for cShop
    cAttributes = {attribute: row[attribute] for attribute in attributeList}
    # e for EKM
    i = 0
    eAttributes = {}
    for k, v in cAttributes.items():
        if v == '' or v not in row.keys():
            continue
        i+=1
        eAttributes[f'Attribute:{k.replace("_", " ")}'] = f'{v.replace(":"," ")}:{i}000:True:{k.replace("_", " ").title()}'
    return eAttributes

def createProduct(row, EKM_header, imageLink, attribute_set):
    product = {k: '' for k in EKM_header}

    {product.update(
        {match.get(k, 'skip'): dispatch[match.get(k, 'skip')](saver(v), imageLink)}
    ) for k, v in row.items() if v != ''}

    changes = {
        'Action': 'Add Product'
    }

    {product.pop(p, None) for p in ['skip']}

    return {**product, **changes, **attributes(row, attribute_set)}

def createOption(row, EKM_Header):
    option = {k: '' for k in EKM_Header}
    option_prices = [int(v) for v in row.values() if 'PRICE ' in v]

    modified_option_prices = [o - int(option['Price']) for o in option_prices]

    changes = {
        'Action': 'Add Product Option',
        'Name': name(row.get('TITLE', '')),
        'CategoryPath': category(row.get('CATEGORY', '')),
        'OptionName': 'Type',
        'OptionSize': '0',
        'OptionType': 'DROPDOWN',
        'OptionItemName': (':').join([i for i in range(len(modified_option_prices))]),
        'OptionItemPriceExtra': (':').join(modified_option_prices),
        'OptionItemOrder': (':').join([0 for o in modified_option_prices])
    }

    {option.pop(p, None) for p in \
        ['skip', 'Description', 'Stock', 'Price']}

    return {**option, **changes}

def convert(file, imageLink, attribute_set, *args):
    cShop_Header = file.fieldnames
    EKM_Header = createHeader()

    converted = []

    for row in file:
        if row.get('TITLE') == '':
            continue

        converted.append(createProduct(row, EKM_Header, imageLink, attribute_set))
        options = len([k for k in row.keys() if 'PRICE ' in k and k != ''])
        {converted.append(createOption(row, EKM_Header)) for o in range(options)}

    return converted, EKM_Header
