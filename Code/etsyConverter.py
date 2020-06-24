#! python3
import csv

def name(value):
    if len(value) > 99:
        return value[:99]
    return value

def category(value):
    if value == '':
        return 'Home'
    elif len(value.split(',')) > 2:
        tags = value.split(',', 2)
        tags.insert(0, 'Home')
        tags.pop()
        catPath = ' > '.join([x.replace("_", " ") if "_" in x else x for x in tags])
        return catPath
    else:
        return 'Home > ' + value

def num(value):
    if value == '' or round(float(value)) < 0:
        return '0'
    return round(float(value))

def gen(value):
    return value

def skip(value):
    return ''

match = {
    'TITLE':'Name',
    'DESCRIPTION':'Description',
    'PRICE': 'Price',
    'TAGS':'CategoryPath',
    'IMAGE1':'Image1',
    'IMAGE2':'Image2',
    'IMAGE3':'Image3',
    'IMAGE4':'Image4',
    'IMAGE5': 'Image5',
    'QUANTITY': 'Stock',
    'VARIATION 1 NAME': 'OptionName1', 'VARIATION 1 VALUES' : 'OptionItemName1', #separate line for each option
    'VARIATION 2 NAME': 'OptionName2', 'VARIATION 2 VALUES' : 'OptionItemName2', #separate line for each option
    'VARIATION 3 NAME': 'OptionName3', 'VARIATION 3 VALUES' : 'OptionItemName3',
    'skip': 'skip'
}

dispatch = {
    'Name': name,
    'Description': gen,
    'Price': num,
    'CategoryPath': category,
    'Image1': gen,
    'Image2': gen,
    'Image3': gen,
    'Image4': gen,
    'Image5': gen,
    'Stock': num,
    'OptionName1': gen,
    'OptionName2': gen,
    'OptionName3': gen,
    'OptionItemName1': gen,
    'OptionItemName2': gen,
    'OptionItemName3': gen,
    'skip': skip
}

def createHeader():
    # Etsy fieldnames
    fieldnames = [
        'Action', 'ID', 'Name', 'CategoryPath',
        'Description', 'Price', 'Stock',
        'Image1', 'Image2', 'Image3', 'Image4', 'Image5',
        'OptionName', 'OptionSize', 'OptionType', 'OptionValidation',
        'OptionItemName', 'OptionItemPriceExtra', 'OptionItemOrder'
    ]
    return fieldnames
    # If Etsy filesnames = etsyEKM, dict = Etsy

def saver(string):
    if not string: return
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def createOption(row, fieldnames, x, sk):
    productOption = {key: '' for key in fieldnames}
    productOption['Action'] = 'Add Product Option'

    for k, v in row.items():
        if v:
            value = saver(v)
            productOption[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)

    optionCells = [
        'Description', 'Stock', 'Price',
        'Image1', 'Image2', 'Image3', 'Image4', 'Image5',
    ]
    [productOption.pop(oC, None) for oC in optionCells]

    productOption['OptionName'] = row[f'VARIATION {x} NAME']
    productOption['OptionSize'] = '0'
    productOption['OptionType'] = 'DROPDOWN'
    productOption['OptionItemName'] = row[f'VARIATION {x} VALUES'].replace(',',':') if row[f'VARIATION {x} VALUES'] else ''
    temp = (':').join(['0' for i in row[f'VARIATION {x} VALUES'].split(',')]) if row[f'VARIATION {x} VALUES'] else ''
    productOption['OptionItemPriceExtra'] = temp
    productOption['OptionItemOrder'] = temp

    [productOption.pop(f'OptionName{i}', None) for i in range(3)]
    [productOption.pop(f'OptionItemName{i}', None) for i in range(3)]
    productOption.pop('skip', None)
    return productOption

def createProduct(row, fieldnames):
    # Creates Product row as dictionary sharing fieldnames with the header of the
    # Dictwriter thusly creating a dynamic product row creator

    product = {key: '' for key in fieldnames}
    product['Action'] = 'Add Product'

    for k, v in row.items():
        if v:
            value = saver(v)
            product[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)

        checkNum = ['Price', 'Stock']
        {product[cn]: 0 if cn == '' else None for cn in checkNum}
    [product.pop(f'OptionName{i}', None) for i in range(3)]
    [product.pop(f'OptionItemName{i}', None) for i in range(3)]
    product.pop('skip', None)
    return product

def convert(file, *args):
    # Calls all other methods to write to the file this it done individually
    Etsy_Header = file.fieldnames
    EKM_Header = createHeader()
    # for row in file check if product or variant and create row accordingly
    converted = []
    for row in file:
        if row['TITLE'] == '':
            continue
        # Append row to filerow list
        converted.append(createProduct(row, EKM_Header))
        # try:
        # Check if the row has variants
        x, sk = 0, 0 # x and sk for variant calculation
        for x in range(3):
            if row.get(f'VARIATION {x} NAME', '') != '':
                converted.append(createOption(row, EKM_Header, x, sk))
                sk += 1
            continue

    # Returns the converted file and the fieldnames for the header
    return converted, EKM_Header
