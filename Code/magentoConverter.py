#! python3
import csv, random, datetime, math

def name(value, *args):
    if len(value) > 99: return value[:99]
    return value

def category(value, *args):
    if value != '' or value != ' ':
        whatareyoudoingmagentoyoudick = value.split(',')[0]
        c = whatareyoudoingmagentoyoudick.split('/')
        c.insert(0,'Home')
        return ' > '.join(c)
    else:
        return 'Home'

def price(value, *args):
    p = float(value)
    if p < 0:
        return '0'
    return p

def stock(value, *args):
    s = float(value)
    if s < 0:
        return '0'
    return round(s)

def image(value, imageLink):
    return f'{imageLink}{value}'

def images(value, imageLink):
    imgs = [f'{imageLink}{img}' for img in value.split(',')]
    while len(imgs) > 4: imgs.pop()
    return imgs

def gen(value, *args):
    return value

def skip(value, *args):
    return ''

match = {
    'categories':'CategoryPath',
    'name':'Name',
    'sku': 'Code',
    'description':'Description',
    'short_description':'ShortDescription',
    'price':'Price',
    'base_image':'Image1',
    'additional_images': 'Images',
    'meta_title':'MetaTitle',
    'meta_description':'MetaDescription',
    'meta_keyword':'MetaKeywords',
    'qty':'Stock',
    'weight':'Weight',
    'skip': 'skip',
}

dispatch = {
    'CategoryPath': category,
    'Name': name,
    'Code': gen,
    'Description': gen,
    'ShortDescription': gen,
    'Price': price,
    'Image1': image,
    'Images': images,
    'MetaTitle': gen,
    'MetaDescription': gen,
    'MetaKeywords': gen,
    'Stock': stock,
    'Weight': price,
    'VariantNames': gen,
    'Attribute:SKU': gen,
    'skip': skip

}

def createFieldNames():
    # If shopify filenames = shopifyEKM, dict = shopify#
    fieldnames = [
        'Action', 'ID', 'CategoryPath', 'Name', 'Code',
        'Description', 'ShortDescription', 'Price',
        'Image1', 'Image2', 'Image3', 'Image4', 'Image5',
        'MetaTitle', 'MetaDescription', 'MetaKeywords',
        'Stock', 'Weight',
        'VariantNames', 'VariantTypes',
        'VariantItem1', 'VariantItem2', 'VariantItem3', 'VariantItem4', 'VariantItem5',
        'Attribute:SKU',
    ]
    """
        Created for reference magento - EKM

        product_type = product (simple) or product with variant (configural) variant (simple)
        qty = stock additional_attributes = Attributes
        base_image = image1 additional_images = image2,3,4,5
        related_skus is the skus of the configurable products variants
        configurable_variations is variant details for configurable product
        Custom options = product option
    """
    return fieldnames

def saver(string):
    saved = string.replace("'","\'") if "'" in string else string
    saved = string.replace('"', '\"') if '"' in string else string
    return saved

def getVariants(row):
    # creates empty lists for variant skus and variant type?
    skus, vList = [], []

    variants = row['configurable_variations']
    if variants != '':
        # loops through all variants in cell
        for variant in variants.split('|'):
            # splits variants down to core and allocates placement
            v = variant.split(',')
            sku = v[0].split('=')
            skus.append(sku[1])

            vara = v[1].split('=')
            var = vara[0].replace('_',' ')
            va = var.title()
            vList.append({va:vara[1]})
            continue
    else:
        skus, vList = '',''
    return skus, vList

def attributes(row):
    attributeSet = row.get('attribute_set')
    # m for magento
    mAttributes = {k : v for k, v in row.items() if attributeSet in k}
    # e for EKM
    i = 0
    eAttributes = {}
    for k, v in mAttributes.items():
        i+=1
        eAttributes[f'Attribute:{k}'] = f'{v}:{i}000:True:{k.replace("_", " ")}'
    return eAttributes

def createVariant(row, sku, variant, imageLink, fieldnames):
    productVariant = {key: '' for key in fieldnames}
    productVariant['Action'] = 'Add Product Variant'

    # Initialises variant k, v attributes as found in get variants
    variantKey, variantValue = '', ''
    for k, v in variant.items():
        variantKey, variantValue = k, v

    for k, v in row.items():
        if v != '' and k != 'additional_images':
            value = saver(v)
            productVariant[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value, imageLink)

    imgs = images(row.get('additional_images', ''), imageLink)
    for x in range(len(imgs)):
        productVariant[f'Image{x+1}'] = imgs[x]

    if productVariant['Stock'] == '': productVariant['Stock'] = '0'
    productVariant['Attribute:SKU'] = productVariant['Code']

    productVariant['VariantNames'] = variantKey
    productVariant['VariantItem1'] = variantValue
    productVariant['Code'] = sku
    productVariant['Attribute:SKU'] = sku

    {productVariant.pop(b) for b in [ # a list of things to blank out
        'Description', 'ShortDescription',
        'MetaTitle','MetaKeywords','MetaDescription',
        'skip'
    ]}

    {productVariant[x]: '0' for x in ['Price', 'Stock'] if productVariant[x] == ''}

    return {**productVariant, **attributes(row)}

def createProduct(row, imageLink, fieldnames):
    product = {key: '' for key in fieldnames}
    product['Action'] = 'Add Product'

    for k, v in row.items():
        if v != '' and k != 'additional_images':
            value = saver(v)
            product[match.get(k, 'skip')] = dispatch[match.get(k, 'skip')](value, imageLink)

    imgs = images(row.get('additional_images', ''), imageLink)
    imgs.insert(0, image(row['image'], imageLink))
    for x in range(len(imgs)):
        product[f'Image{x+1}'] = imgs[x]

    if product['Stock'] == '': product['Stock'] = '0'
    product['Attribute:SKU'] = product['Code']

    if product['CategoryPath'] == '': product['CategoryPath'] = 'Home'

    product.pop('skip')
    return {**product, **attributes(row)}

def updateVariant(row, oldVariant, imageLink):
    needed = ['price', 'qty']
    for k, v in row.items():
        if v != '' and k in needed:
            value = saver(v)
            oldVariant.update(
                {match.get(k):dispatch[match.get(k)](value, imageLink)}
            )
    return oldVariant

def mutateProduct(product, productRow):
    productCopy = {key: value for key, value in product.items()}
    changes = {k: v for k, v in {
        'Action': 'Add Product Variant',
        'Description': '',
        'CategoryPath' : productRow.get('categories', 'Home'),
        'Name' : productRow.get('name', ''),
        'VariantNames' : 'Size',
        'VariantItem1' : product.get('Name', '')
    }.items()}

    return {**productCopy, **changes}


def split(row, imageLink, fieldnames):
    product = createProduct(row, imageLink, fieldnames)
    skus, v = getVariants(row)
    variants = []
    for sku, variant in dict(zip(skus, v)).items():
        variants.append(createVariant(row, sku, variant, imageLink, fieldnames))
    return product, variants, skus

def checkType(skuList, row):
    # Check the product type and return value accordingly
    if row['product_type'] == 'configurable':
        return 'split'
    elif row['product_type'] == 'grouped':
        return 'group'
    elif row['sku'] in skuList:
        return 'variant'
    else:
        return 'product'

def additional_images(product_row, row, additional_image_number, imageLink):
    if additional_image_number < 5:
        product_row[f'Image{additional_image_number+1}'] = images(row['additional_images'],imageLink)
    return product_row

def checkHeader(header, *args):
    

def convert(file, imageLink):
    # Creates variable to hold fieldnames
    # creates a list to contain the converted dictionary lists
    # create empty list to check all future products against
    Magento_Header = file.fieldnames
    EKM_Header = createFieldNames()
    converted, skuList = [], []
    additional_image_number = 0

    # Loop the rows in the file
    for row in file:
        # skip blank rows
        if row['product_type'] == '':
            if row.get('additional_images', '') != '':
                additional_image_number += 1
                converted[-1] = additional_images(converted[-1], row, additional_image_number, imageLink)
                continue
            continue
        additional_image_number = 0

        if row['sku'] in skuList:
            # gets the index of the row with the same sku as current row
            index = converted.index(next(r for r in converted if r['Code'] == row['sku']))
            oldVariant = converted.pop(index)
            updatedVariant = updateVariant(row, oldVariant, imageLink)
            converted.insert(index, updatedVariant)
            continue

        type = checkType(skuList, row)
        if type == 'split':
            product, variants, skus = split(row, imageLink, EKM_Header)
            if not all(str in header for str in product.keys()):
                EKM_Header = list(dict.fromkeys(EKM_header += product.keys()))
            converted.append(product)
            if variants != '':
                {converted.append(v) for v in variants}
            if skus != '':
                {skuList.append(sku) for sku in skus}
                # Creates list of skus to reference in the future for assigning prices
            continue
        elif type == 'group':
            converted.append(createProduct(row, imageLink, EKM_Header))
            for sku in row['sku'].split('-'):
                index = converted.index(next(r for r in converted if r['Code'] == sku))
                product = converted.pop(index)
                converted.append(mutateProduct(product, row))
            continue
        elif type == 'variant':
            continue
        else:
            # Creates a basic product and resets the variants variables
            p = createProduct(row, imageLink, EKM_Header)
            if not all(str in header for str in p.keys()):
                EKM_Header = list(dict.fromkeys(EKM_header += p.keys()))
            converted.append(p)
            continue

    return converted, EKM_Header
