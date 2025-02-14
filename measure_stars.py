import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from astropy.io import fits
from astropy.stats import sigma_clipped_stats,gaussian_sigma_to_fwhm
from photutils.detection import DAOStarFinder
from photutils.psf import fit_2dgaussian, fit_fwhm
from photutils.aperture import CircularAperture,aperture_photometry
import os,logging
from astropy.modeling import models, fitting
import csv
from astropy.table import QTable
from scipy.stats import norm


#Config  
#fits_path = '/home/ferrante/astrophoto/M81/Emilio/NGC 7771/2024-12-04_21-06-31_-10.00_180.00s_150.fits' # Path to the FITS file or directory containing FITS files
#fits_path = '/home/ferrante/astrophoto/M81/Emilio/thor/2024-12-18_02-56-49_-10.00_180.00s_200.fits' # Path to the FITS file or directory containing FITS files

#fits_path = '/home/ferrante/astrophoto/M42/M_42_LIGHT_R_180s_BIN1_0C_004_20240312_204325_430_GA_0_OF_0_E.FIT' # Path to the FITS file or directory containing FITS files
fits_path = '/home/ferrante/astrophoto/M81/1810/ngc253_5s_7150f.fits' # Path to the FITS file or directory containing FITS files

cropFactor = 1 # Crop the image by cropFactor of its width and height (faster processing)
randomSources = 60 # Choose randomSources (faster processing)
threshold = 20 #threshold for star detection, 20 seems to work well
pixelScale = 0.73 # pixel scale in arcsec/pixel
bit = 16 # bit depth of the sensor, used to cut saturated stars
bin = 1 # binning factor
radius = 7*bin # radius of the aperture for the star measurement
mode = "both" # "micah" or "astropy" or "both"
plot_image = True # plot the image with the detected stars

def measure_stars(fits_file):
    fwhm_micah = []
    ecc = []
    fwhmfit = []
    average_fwhm_micah, average_fwhm,average_ecc = 0,0,0

    # Load the FITS file
    hdu_list = fits.open(fits_file)
    image_data = hdu_list[0].data
    hdu_list.close()

    # Crop the image by cropFactor of its width and height (faster processing)
    height, width = image_data.shape
    crop_height = height // cropFactor
    crop_width = width // cropFactor
    start_y = (height - crop_height) // 2
    start_x = (width - crop_width) // 2
    image_data = image_data[start_y:start_y + crop_height, start_x:start_x + crop_width]

    # Calculate basic statistics
    mean, median, std = sigma_clipped_stats(image_data, sigma = 3.0)
    print(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
    # Detect stars
    daofind = DAOStarFinder(fwhm = 3.0, threshold = threshold*std)
    sources = daofind(image_data - median)
    print(f"Number of stars detected by DAO: {len(sources)}")

    # Cutting saturated stars
    sources = sources[sources['peak'] < (2**bit)*0.98 ]
    print(f"Number of non clipped stars (< 98% peak): {len(sources)}")
    print(sources)
    
    # Cutting weak stars (noise)
    #sources = sources[sources['peak'] > median*10.0]
    sources['peak_median_ratio'] = sources['peak'] / median
    sources.sort('peak_median_ratio', reverse=True)
    print(f"Number of non clipped  stars above background*10: {len(sources)}")
    # Exclude sources with flux/peak too high, it is likely to be in  a galaxy or in a nebula too bright
    #sources = sources[sources['peak'] / sources['flux'] > 0.1]
    print(f"Number of stars with flux/peak too high: {len(sources)}")

    if len(sources) == 0:
        logging.warning("No stars detected")
        return  
    
    # Choose randomSources (faster processing)
    np.random.seed(42)  # For reproducibility
    if len(sources) > randomSources:
        sources = sources[np.random.choice(len(sources), randomSources, replace=False)]
        #sources.sort('peak', reverse=True)
        #sources = sources[:randomSources]
    #print(sources)
    # Calculate and print the average peak value
    average_peak = np.mean(sources['peak'])
    print(f"Average Peak: {average_peak:.2f}")

    print(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
    print(f"Number of sources detected: {len(sources)}")
    results_table = QTable(names=('xcentroid', 'ycentroid', 'peak', 'fwhm', 'peak_median_ratio'), dtype=('f4', 'f4', 'f4', 'f4', 'f4'))

    if mode == "micah" or mode == "both":
        for source in sources:
            x = source['xcentroid']
            y = source['ycentroid']
            try:
                if (x > radius and x < (width - radius) and y > radius and y < (height - radius)):
                # Assuming you have the star's image data in `data` and the aperture in `aperture`
                    cutout = image_data[int(y-radius):int(y+radius), int(x-radius):int(x+radius)]
                    cutout2 = image_data[int(y-10*radius):int(y+10*radius), int(x-10*radius):int(x+10*radius)]
                    cutout_mean, cutout_median, cutout_std = sigma_clipped_stats(cutout, sigma = 3.0)
                    print(x,y)
                    cutout2_mean, cutout2_median, cutout2_std = sigma_clipped_stats(cutout2, sigma = 3.0)
                    print(f"Cutout Mean: {cutout_mean:.2f}, Cutout Median: {cutout_median:.2f}, Cutout Std: {cutout_std:.2f}")
                    print(f"Cutout2 Mean: {cutout2_mean:.2f}, Cutout Median: {cutout2_median:.2f}, Cutout Std: {cutout2_std:.2f}")
                    print("------------------------")
                    if cutout2_median < 2 * median:

                        # Fit a 2D Gaussian
                        p_init = models.Gaussian2D(amplitude=np.max(cutout), x_mean=radius, y_mean=radius)
                        fit_p = fitting.LevMarLSQFitter()
                        y, x = np.mgrid[:cutout.shape[0], :cutout.shape[1]]
                        p = fit_p(p_init, x, y, cutout)

                        # Calculate the FWHM
                        sigma_x = p.x_stddev.value
                        sigma_y = p.y_stddev.value
                        fwhm_x = sigma_x * gaussian_sigma_to_fwhm
                        fwhm_y = sigma_y * gaussian_sigma_to_fwhm
                        fwhm_micah.append(np.sqrt(fwhm_x * fwhm_y))
                        if fwhm_y < fwhm_x:
                            ecc.append(np.sqrt(abs(1 - fwhm_y/fwhm_x)))
                        else:
                            ecc.append(0)
                        
                        print(f"FWHM Micah: {np.sqrt(fwhm_x * fwhm_y):.2f}")
                        fwhml = fit_fwhm(cutout-median, fit_shape=(7, 7))
                        fwhmfit.append( fwhml)
                        if plot_image:

                            # Plot a 3D graph of the cutout
                            fig = plt.figure()
                            ax = fig.add_subplot(111, projection='3d')
                            x = np.arange(cutout.shape[1])
                            y = np.arange(cutout.shape[0])
                            x, y = np.meshgrid(x, y)
                            ax.plot_surface(x, y, cutout, cmap='viridis')
                            ax.set_xlabel('X Pixel')
                            ax.set_ylabel('Y Pixel')
                            ax.set_zlabel('Intensity')
                            plt.show()
                        
                        results_table.add_row((source['xcentroid'], source['ycentroid'], source['peak'], fwhml, source['peak_median_ratio']))

                    else:
                        print(f"Star rejected because of high background : {cutout2_median}, vs : {median} ")
                        #print(f"FWHM_x: {fwhm_x}, FWHM_y: {fwhm_y}")
                else:
                    print(f"Star at position x: {x}, y: {y} is too close to the edge")
            except Exception as e:
                print(f"Error fitting 2D Gaussian at position x: {x}, y: {y}")
                print(f"Cutout values: {cutout}")
                print(f"Exception: {e}")
    print(results_table)

    roundness1_avg = np.mean(abs(sources['roundness1']))
    roundness2_avg = np.mean(abs(sources['roundness2']))
    print(f"Average Roundness1: {roundness1_avg:.2f}")
    print(f"Average Roundness2: {roundness2_avg:.2f}")

    if mode == "astropy" or mode ==  "both":
        xypos = list(zip(sources['xcentroid'], sources['ycentroid']))

        psfphot = fit_2dgaussian(image_data, xypos=xypos, fix_fwhm=False, fit_shape=(7, 7))
        phot_tbl = psfphot.results
        fwhm = fit_fwhm(image_data, xypos=xypos, fit_shape=(7, 7))
        #print(fwhm)
    # Calculate and print the average FWHM value
    if mode == "micah" or mode == "both": 
        average_fwhm_micah = np.mean(fwhm_micah)
        print(f"Average FWHM Micah: {average_fwhm_micah:.2f}")
        average_ecc = np.mean(ecc)
        print(f"Average ecc: {average_ecc:.2f}")
     
        average_fwhmfit = np.mean(fwhmfit)
        print(f"Average FWHM fit: {average_fwhmfit:.2f}")   
    if mode == "astropy" or mode == "both": 
        average_fwhm = np.mean(fwhm)
        print(f"Average FWHM Astropy: {average_fwhm:.2f}")

    if plot_image:

        cpositions = np.transpose((results_table['xcentroid'], results_table['ycentroid']))
        apertures = CircularAperture(cpositions, r = radius)
        plt.figure()
        plt.imshow(image_data, cmap = 'Greys', origin = 'lower', norm = LogNorm(), interpolation = 'nearest')
        plt.colorbar()

        # draw apertures. apertures.plot command takes arguments (color, line-width, and opacity (alpha))
        apertures.plot(color = 'red', lw = 2.5, alpha = 0.5)
        for i, cposition in enumerate(cpositions):
            plt.text(cposition[0], cposition[1], f'{results_table["fwhm"][i]:.2f}', color='red', fontsize=9, ha='right', va='top')
            plt.text(cposition[0], cposition[1], f'{results_table["peak"][i]:.2f}', color='blue', fontsize=9, ha='left', va='bottom')
        plt.show()

    return np.array([round(average_fwhm_micah, 2), round(average_fwhm, 2), round(average_ecc, 2)])

if __name__ == "__main__":
    if os.path.isdir(fits_path):
        ret = []
        for file in os.listdir(fits_path):
            if file.lower().endswith(('.fit', '.fits')):
                print("------------------------")
                print(f"Start measuring: {file}")
                ret = measure_stars(os.path.join(fits_path, file))

    else:
        print(f"Start measuring: {fits_path}")
        measure_stars(fits_path)
