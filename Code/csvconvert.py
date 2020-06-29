#! python3
import csv
import Errors
import shopifyConverter, etsyConverter, magentoConverter, shopwiredConverter, wixConverter, cShopConverter
from popup import popup

def start(file, location):
    # newfilelocation is essential to direct the file to where you want it to go
    newfileLocation = location

    # Initialising read variables (for scope)
    header, origin, oldFile = '', '', ''

    # Initialises convert Variables
    newfile, fieldnames = '', ''

    # Image link variable for magento
    imageLink = ''
    # Attribute set variable for magento
    attribute_set = ''

    with open(file, newline = '', encoding='utf-8', errors='ignore') as f:
        # Creates an ordered dictionary of the file
        oldFile = csv.DictReader(f)
        # Get the headers of the file for key purposes
        header = oldFile.fieldnames

        # Use the oldFile.keys() to detect and return the origin of the file
        origin = detectOrigin(header)
        if origin == False: # If the origin is not recognised
            raise Errors.IncorrectFile('File is not recognised') # skips file temporary fix

        # If the origin is in iLink yeild to get value for image links
        iLink = ['magento','wix','cShop']
        if origin in iLink:
            f = file.split('/')
            fn = f.pop()
            t = popup(fn)
            imageLink = t.images()

        # if file has custom attributes
        aSet = ['magento', 'cShop']
        if origin in aSet:
            t = popup('')
            attribute_set = t.attributes()

        # Conversion
        newfile, fieldnames = convert(oldFile, origin, imageLink, attribute_set)

    # Get old filename
    oldfilename = getoldfilename(file)
    # Create name for the new file
    filename = createfilename(oldfilename, newfileLocation)

    # Writing to new file uses 'fieldnames, newfile, filename'
    with open(filename, 'w', newline='', encoding='utf-8', errors='ignore') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in newfile:
            writer.writerow(row)

def createfilename(oldfilename, newfilelocation):
    return f'{newfilelocation}/Converted_{oldfilename}'

def getoldfilename(file):
    return file.split('/')[-1] # returns the last element of the list

def convert(oldFile, origin, imageLink, attribute_set):
    # Converts the files based on their origin
    dispatch = {
        'shopify': shopifyConverter,
        'etsy': etsyConverter,
        'magento': magentoConverter,
        'shopwired': shopwiredConverter,
        'wix' : wixConverter,
        'cShop': cShopConverter,
        '': ''
    }
    newfile, fieldnames = '', ''

    lAl = dispatch.get(origin, '') # locked and loaded
    if lAl != '': newfile, fieldnames = lAl.convert(oldFile, imageLink, attribute_set)
    return newfile, fieldnames

# returns a string for the origin of the file
def detectOrigin(header):
    # THE ESSENTIALS :  Name description Price
    match = {
        'cShop': ['TITLE', 'CATEGORY', 'SECONDARY CATEGORY'],
        'etsy': ['TITLE', 'DESCRIPTION','PRICE'],
        'shopify': ['Title', 'Body (HTML)', 'Variant Price'],
        'magento': ['sku', 'product_type', 'name'],
        'shopwired': ['Item ID', 'Item Name'],
        'wix': ['fieldType', 'productImageUrl'],
    }

    origin = ''

    if 'type' in header:
        index = header.index('type')
        header.pop(index)
        header.insert(index, 'product_type')

    for k, v in match.items():
        if all(str in header for str in v):
            return k
    with open(".\log.txt", 'a+') as f:
        f.write("Below Header is not recognised")
        f.write(f"{header}\n")
    return False
