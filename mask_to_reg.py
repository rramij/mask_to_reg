# Make contours from mask file
import numpy as np
from skimage.measure import find_contours
from astropy.wcs import WCS
import regions
from regions import PolygonSkyRegion
from astropy.io import fits

#import astropy.units as u
#from astropy.io import fits
#from astropy.wcs import WCS
#from astropy.coordinates import Angle
#from astropy.coordinates import SkyCoord


mask_image=input('Enter mask file name: ')
outregion=input('Output region file name, e.g., inc.reg: ')
######################
def get_image_data(fitsfile):
    """
    Reads a FITS file and returns a tuple of the image array and the header.
    
    Parameters:
    fitsfile (str): The path to the FITS file.
    
    Returns:
    tuple: A tuple containing the image array and the header.
    """
    with fits.open(fitsfile) as input_hdu:
        # Check the dimensionality of the data and extract the appropriate slice
        if len(input_hdu[0].data.shape) == 2:
            image = np.array(input_hdu[0].data[:, :])
        elif len(input_hdu[0].data.shape) == 3:
            image = np.array(input_hdu[0].data[0, :, :])
        else:
            image = np.array(input_hdu[0].data[0, 0, :, :])
        
        header = input_hdu[0].header
    
    return image, header

######

mask_image, mask_header = get_image_data(mask_image)

wcs = WCS(mask_header)
while len(wcs.array_shape) > 2:
    wcs = wcs.dropaxis(len(wcs.array_shape) - 1)

contours = find_contours(mask_image, 0.5)
polygon_regions = []
for contour in contours:
    # Convert the contour points to pixel coordinates
    contour_pixels = contour
    # Convert the pixel coordinates to Sky coordinates
    contour_sky = wcs.pixel_to_world(contour_pixels[:, 1], contour_pixels[:, 0])
    # Create a Polygon region from the Sky coordinates
    polygon_region = PolygonSkyRegion(vertices=contour_sky, meta={'label': 'Region'})
    # Add the polygon region to the list
    polygon_regions.append(polygon_region)

# Write region file
regions.Regions(polygon_regions).write(outregion, format='ds9')
