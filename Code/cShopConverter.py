def name(value):
    if len(value) > 99:
        return value[:99]
    return value

def category(value):
    if value == '':
        return 'Home'
    else:
        return 'Home > ' + value

def num(value):
    if value == '' or round(float(value)) < 0:
        return '0'
    return round(float(value))

def image(value, imageLink):
    return f'{imageLink}{value}.jpg'

def tax(value, *args):
    if value == 'YES'
        return 1
    return 2

def gen(value):
    return value

def skip(value):
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
    'skip': ''
}

def createHeader():
    # cShop fieldnames
    return [
        'Action', 'ID', 'Name', 'CategoryPath', 'CategoryManagement'
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

def convert(file, *args):
    cShop_Header = file.fieldnames
    EKM_header = createHeaders()

    converted = []
    for row in file:
        
