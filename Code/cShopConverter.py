import re

name = lambda v: v if len(v) <= 99 else v[:99]
category = lambda l: 'Home >' + ('>').join(l) if len(l) > 1 else 'Home'
image = lambda v, image_link: f'{image_link}{v}.jpg' if v != '' else ''
tax = lambda v: 1 if v == 'YES' else 2
price_check = lambda p: p if p != '' else '0'
def num(value):
    try:
        if value == '' or round(float(value)) < 0:
            return '0'
        return round(float(value))
    except ValueError:
        return '0'

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
    string = f'{string}'
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
        if v == '':
            continue
        i+=1
        eAttributes[f'Attribute:{k.replace("_", " ")}'] = f'{v.replace(":"," ")}:{i}000:True:{k.replace("_", " ").title()}'
    return eAttributes

def createProduct(row, EKM_header, image_link, attribute_set):
    product = {k: '' for k in EKM_header}

    category_chain = ['TYPE', 'CATEGORY', 'BREED/SPECIES']
    category_management_chain = ['ARTIST', 'TYPE']

    # List of changes that exist outside of the main loop
    changes = {
        'Action': 'Add Product',
        'Code' : row.get('CODE', ''),
        'Name' : name(row.get('TITLE', '')),
        'Price': price_check(num(row.get('PRICE', ''))),
        'CategoryPath': category(
            [row.get(c, '') for c in category_chain]),
        'CategoryManagement': category(
            [row.get(c, '') for c in category_management_chain]),
        'Description': row.get('DESCRIPTION', ''),
        'Image1': image(row.get('IMAGE', ''), image_link),
        'Image2': image(row.get('IMAGE 2', ''), image_link),
        'Image3': image(row.get('IMAGE 3', ''), image_link),
        'TaxRateID': tax(row.get('VAT', '')),
    }
    changes = {k: saver(v) for k, v in changes.items()}


    return {**product, **changes, **attributes(row, attribute_set)}

def createOptions(row, EKM_Header):
    option = {k: '' for k in EKM_Header}
    option_prices = [v for k, v in row.items() if 'PRICE' in k and v != '']
    modified_option_prices = \
        [str(float(o) - float(row["PRICE"])) for o in option_prices]

    category_chain = ['TYPE', 'CATEGORY', 'BREED/SPECIES']

    changes = {
        'Action': 'Add Product Option',
        'Name': name(row.get('TITLE', '')),
        'CategoryPath': category(
            [row.get(c, None) for c in category_chain]),
        'OptionName': 'Type',
        'OptionSize': '0',
        'OptionType': 'DROPDOWN',
        'OptionItemName': (':').join([str(i) for i in range(len(modified_option_prices))]),
        'OptionItemPriceExtra': (':').join(modified_option_prices),
        'OptionItemOrder': (':').join(['0' for o in modified_option_prices])
    }
    changes = {k: saver(v) for k, v in changes.items()}

    {option.pop(p, None) for p in ['Description', 'Stock', 'Price']}

    return {**option, **changes}

def checkHeader(header, newHeader):
    # This needs to be checked for variants every single row :D
    if not all(str in header for str in list(newHeader)):
        return list(dict.fromkeys(header+list(newHeader)))
    return header

def convert(file, imageLink, attribute_set, *args):
    cShop_Header = file.fieldnames
    EKM_Header = createHeader()

    converted = []

    for row in file:
        if row.get('TITLE') == '':
            continue

        product = createProduct(row, EKM_Header, imageLink, attribute_set)
        converted.append(product)
        EKM_Header = checkHeader(EKM_Header, product.keys())
        if len([k for k, v in row.items() if 'PRICE' in k and v != '']) > 1:
            option = createOptions(row, EKM_Header)
            converted.append(option)
            EKM_Header = checkHeader(EKM_Header, option.keys())

    return converted, EKM_Header
