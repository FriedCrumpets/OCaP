#! python3
import csv, random, datetime

category = lambda v: f'Home>{v}' if v else 'Home'
name = lambda v: v if len(v) < 100 else v[:99]
gen = lambda v: v
skip = lambda v: ''

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
    'Category 1': 'CategoryPath',
    'Item Name': 'Name',
    'SKU': 'Code',
    'Variant SKU' : 'Code',
    'Price': 'Price',
    # 'Variant Price': 'Price',
    'RRP': 'RRP',
    'Image URL/File Name 1': 'Image1',
    'Image URL/File Name 2': 'Image2',
    'Image URL/File Name 3': 'Image3',
    'Image URL/File Name 4': 'Image4',
    'Image URL/File Name 5': 'Image5',
    'Meta Title': 'MetaTitle',
    'Meta Description': 'MetaDescription',
    'Meta Keywords': 'MetaKeywords',
    'Opening Stock': 'Stock',
    'Variant Stock':'Stock',
    # ['Category 2', 'Category 3', 'Category 4', 'Category 5']: 'CategoryManagement',
    # ['Variant Option 1', 'Variant Option 2', 'Variant Option 3']: 'VariantNames',
    # 'VariantTypes',
    # 'VariantCategoryPage',
    'Variant Option 1 Value': 'VariantItem1',
    'Variant Option 2 Value': 'VariantItem2',
    'Variant Option 3 Value': 'VariantItem3',
    'Option Extra Name 1': 'OptionName',
    # 'OptionSize',
    # 'OptionType',
    # ['Option Extra Name 1', 'Option Extra Name 2', 'Option Extra Name 3']: 'OptionItemName',
    # ['Option Extra Price 1', 'Option Extra Price 2', 'Option Extra Price 3']: 'OptionItemPriceExtra',
    # 'OptionItemOrder',
    'Global Trade Item Number (GTIN)': 'Attribute:GTIN',
    'Variant GTIN': 'Attribute:GTIN',
    'Manufacturer Part Number (MPN)': 'Attribute:MPN',
    'skip': 'skip',
}

dispatch = {
    'CategoryPath': category,
    'Name': name,
    'Code': gen,
    'Description': gen,
    'ShortDescription': gen,
    'Brand': gen,
    'Price': price,
    'RRP': price,
    'Image1': gen,
    'Image2': gen,
    'Image3': gen,
    'Image4': gen,
    'Image5': gen,
    'MetaTitle': gen,
    'MetaDescription': gen,
    'MetaKeywords': gen,
    'Stock': stock,
    'VariantItem1': gen,
    'VariantItem2': gen,
    'VariantItem3': gen,
    'OptionName': gen,
    # 'OptionSize',
    # 'OptionType',
    # 'OptionItemName',
    # 'OptionItemPriceExtra',
    # 'OptionItemOrder',
    'Attribute:GTIN': gen,
    'Attribute:MPN': gen,
    'skip': skip
}

def createFieldNames():
    # If shopify filenames = shopifyEKM, dict = shopify#
    fieldnames = [
        'Action', 'ID', 'CategoryPath', 'Name', 'Code',
        'Description', 'ShortDescription', 'Brand',
        'Price', 'RRP',
        'Image1', 'Image2', 'Image3', 'Image4', 'Image5',
        'MetaTitle', 'MetaDescription', 'MetaKeywords',
        'Stock', 'CategoryManagement',
        'VariantNames', 'VariantTypes', 'VariantCategoryPage',
        'VariantItem1', 'VariantItem1Data',
        'VariantItem2', 'VariantItem2Data',
        'VariantItem3', 'VariantItem3Data',
        'OptionName', 'OptionSize', 'OptionType', 'OptionItemName',
        'OptionItemPriceExtra', 'OptionItemOrder',
        'Attribute:GTIN', 'Attribute:MPN'
    ]

    # Created for reference shopwired - EKM
    shopwired = [
        'Item ID', # used to find out product or variant?
        'Item Name', 'Item Description', 'Item Description 2',
        'Item Description 3', 'Item Description 4', 'Item Description 5',
        'Image URL/File Name 1', 'Image URL/File Name 2', 'Image URL/File Name 3',
        'Image URL/File Name 4', 'Image URL/File Name 5', 'Price', 'RRP', 'SKU',
        'Opening Stock', 'Meta Title', 'Meta Keywords', 'Meta Description',
        'Global Trade Item Number (GTIN)', 'Manufacturer Part Number (MPN)',
        'Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5',
        'Variant Option 1', 'Variant Option 1 Value',
        'Variant Option 2', 'Variant Option 2 Value',
        'Variant Option 3', 'Variant Option 3 Value',
        'Variant Image', 'Variant SKU', 'Variant GTIN', 'Variant Price',
        'Variant Weight', 'Variant Stock',
        'Optional Extra Name 1', 'Optional Extra Price 1',
        'Optional Extra Name 2', 'Optional Extra Price 2',
        'Optional Extra Name 3', 'Optional Extra Price 3',
    ]
    return fieldnames

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def createOption(row, fieldnames):
    option = {key: '' for key in fieldnames}
    option['Action'] = 'Add Product Option'
    # The key for which is followed for the fieldnames of the new file

    oNNumber = 0 # Option Names number used to calculate number of options in range

    for k, v in row.items():
        if 'Optional Extra Name' in k: oNNumber += 1

    # List of headers required for this type
    option['CategoryPath'] = f"Home > {row['Category 1']}"
    option['Name'] = row['Item Name']
    option['OptionName'] = row['Optional Extra Name 1']
    option['OptionType'] = 'DROPDOWN'
    option['OptionSize'] = '240'
    option['OptionItemName'] = (':').join([row[f'Optional Extra Name {x+1}'] for x in range(oNNumber) if row[f'Optional Extra Name {x+1}'] != ''])
    option['OptionItemPriceExtra'] = (':').join([row[f'Optional Extra Price {x+1}'] for x in range(oNNumber) if row[f'Optional Extra Name {x+1}'] != ''])
    option['OptionItemOrder'] = (':').join(['0' for x in range(oNNumber) if row[f'Optional Extra Name {x+1}'] != ''])

    return option

def createVariant(row, product_row, fieldnames, v): # 2 is 1, 1 is 2, 0 is 3
    variant = createProduct(product_row, fieldnames)
    variant['Action'] = 'Add Product Variant'
    # Creates empty description and category variables
    # For columns to be joined togetherat a later date

    not_needed = [
        'RRP', 'SKU', 'Price', 'Item Name',
        'Item Description', 'Item Description 2',
        'Item Description 3', 'Item Description 4', 'Item Description 5',
        'Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5',
        'Opening Stock', 'Meta Title', 'Meta Keywords', 'Meta Description',
        'Image URL/File Name 1', 'Image URL/File Name 2', 'Image URL/File Name 3',
        'Image URL/File Name 4', 'Image URL/File Name 5',
        'Optional Extra Name 1', 'Optional Extra Price 1',
        'Optional Extra Name 2', 'Optional Extra Price 2',
        'Optional Extra  Name 3', 'Optional Extra Price 3',
    ]

    for k, v in row.items():
        if v != '' or k not in not_needed:
            value = saver(v)
            variant.update({match.get(k, 'skip'): dispatch[match.get(k, 'skip')](value)})
            if 'Variant' in k and v != '':
                if 'Image' in k: variant.update({'Image1': product_row[f'Image URL/File Name {v}']})
                if 'Price' in k: variant.update({'Price': v})
                if 'SKU' in k: variant.update({'Code': v})
    {variant.update({x: ''}) for x in [ # Blanks these cells out.
        'Description', 'CategoryManagement',
        'Global Trade Item Number (GTIN)', 'Manufacturer Part Number (MPN)',
    ]}

    variant.update({'VariantNames': (':').join([
        product_row[f'Variant Option {x+1}'] for x in range(3) if product_row[f'Variant Option {x+1}'] != ''
    ])})

    {variant.update({f'VariantItem{index+1}': value}) for value, index in zip(v, range(len(v), -1, -1))}

    variant.pop('skip')
    return variant

def createProduct(row, fieldnames):
    product = {key: '' for key in fieldnames}
    product['Action'] = 'Add Product'

    not_needed = [
        'Variant Price', 'Variant Image', 'Variant Stock',
        'Variant Option 1', 'Variant Option 1 Value', # variant option 1,2,3 sanitized into variant names
        'Variant Option 2', 'Variant Option 2 Value',
        'Variant Option 3', 'Variant Option 3 Value',
        'Variant GTIN', 'Variant SKU',
        'Optional Extra Name 1', 'Optional Extra Price 1',
        'Optional Extra Name 2', 'Optional Extra Price 2',
        'Optional Extra  Name 3', 'Optional Extra Price 3',
    ]

    # Creates empty description and category variables
    # For columns to be joined togetherat a later date
    description, category = 0, 0

    for k, v in row.items():
        if v != '' or k not in not_needed:
            value = saver(v)
            product[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value)
        if 'Item Description ' in k: description += 1
        if 'Category ' in k: category += 1

    # for all descriptions assigns initial description as list appends the rest
    # and then joins them all together with a break
    desc = [row['Item Description']]
    {desc.append(row[f'Item Description {x+2}']) for x in range(description-1) if row[f'Item Description {x+2}'] != ''}
    product['Description'] = '<br /'.join(desc)

    product['CategoryManagement'] = (';').join(
        [f"Home > {row[f'Category {x+2}']}" for x in range(category-1) if row[f'Category {x+2}'] != '']
    )
    # Refer to dictionary in createfieldnames method to correctly assign data
    product.pop('skip')
    return product

def checkRow(row):
    type = []
    if row['Item ID'] != 'variant':
        # Row is a product row. Need to check if row has variants or options
        type.append('product')
    if row['Variant Option 1'] != '' or row['Item ID'] == 'variant':
        type.append('variant')
    if row['Optional Extra Name 1'] != '':
        type.append('option')
    return ''.join(type)

def convert(file, *args):
    # Creates variable to hold fieldnames
    # creates a list to contain the converted dictionary lists
    # create empty list to check all future products against
    EKM_Header = createFieldNames()
    shopwired_Header = file.fieldnames
    converted = []
    product_row = ''
    variants = {f'VariantItem{x+1}': [''] for x in range(3)}

    for row in file:
        # skip blank rows
        if row['Item ID'] == '': continue

        row_type = checkRow(row)
        if 'product' in row_type:
            converted.append(createProduct(row, EKM_Header))
            product_row = row
        if 'product' in row_type and 'variant' in row_type:
            product_row = row
            temp = {f'VariantItem{x+1}': [''] for x in range(3)}
            for (k,v),(x) in zip(temp.items(), range(len(temp))):
                if product_row[f'Variant Option {x+1} Value'] != '':
                    variants[k] = [x for x in product_row[f'Variant Option {x+1} Value'].split(', ')]
        if 'variant' in row_type and 'product' not in row_type:
            vList = [(x,y,z) for x in variants['VariantItem3']
                              for y in variants['VariantItem2']
                              for z in variants['VariantItem1']]
            {converted.append(createVariant(row, product_row, EKM_Header, v)) for v in vList if v[2] != ''}

            # converted.append(createVariant(row, product_row, EKM_Header, v[0], v[1], v[2]))
            variants = {f'VariantItem{x+1}': [''] for x in range(3)}

        if 'product' in row_type and 'option' in row_type:
            converted.append(createOption(row, EKM_Header))

    return converted, EKM_Header
