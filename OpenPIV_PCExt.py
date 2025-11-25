from openpiv import tools, pyprocess, validation, filters, scaling, preprocess
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import math
from pylab import *


def process_images(frame_a_path, frame_b_path, window_size, search_area_size, window_overlap, dt, pixels_per_micron,
                   sig2noise_val, replace_outliers = False):

    '''
    frame_a_path            -> path to your first image of your image pair
    frame_b_path            -> path to your second image of your image pair
    window_size             -> PIV parameter: size of your interrogation window, also size of your flow cells
    search_area_size        -> PIV parameter: how far your windows search to correlate
    window_overlap          -> PIV parameter: the amount your interrogation windows overlap
    dt                      -> exposure time / time between image pairs
    pixels_per_micron       -> pixels per micron or some other conversion. Note: all labels will still use microns unless changes.
    sig2noise_val           -> amount of signal-to-noise to accept from vectors
    replace_outliers        -> if True will replace any outliers in the flow field by interpolation
    '''

    # Import image pair
    frame_a = tools.imread(frame_a_path)
    frame_b = tools.imread(frame_b_path)

    # Perform fourier transform cross correlation
    u, v, sig2noise = pyprocess.extended_search_area_piv(frame_a.astype(np.int32), frame_b.astype(np.int32),
                                                         window_size=window_size, overlap=window_overlap, dt=dt,
                                                         search_area_size=search_area_size,
                                                         sig2noise_method='peak2peak')

    # Get coordinates from the first image pair of vector cells
    x, y = pyprocess.get_coordinates(image_size=frame_a.shape, search_area_size=search_area_size,
                                     overlap=window_overlap)

    # Replaces outliers with sig2noise_val ratio with 0 flow vectors
    _ = validation.sig2noise_val(u, v, sig2noise, threshold=sig2noise_val)

    if replace_outliers:
        u, v = filters.replace_outliers(u, v, method='localmean', kernel_size=2)

    # Scale the coordinates with pixel conversion
    x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor=pixels_per_micron)

    return x, y, u, v


def process_folder_of_images(directory, window_size, search_area_size, window_overlap, dt, pixels_per_micron,
                             sig2noise_val, replace_outliers):

    # Process a folder of however many images there are

    image_files = os.listdir(directory)
    extension = image_files[0][-4:]
    number_of_images = len(image_files)
    big_u, big_v = [], []

    for image in range(0, number_of_images - 1):
        x, y, u, v = process_images(directory + str(image) + extension, directory + str(image + 1) + extension,
                                    window_size, search_area_size, window_overlap, dt, pixels_per_micron, sig2noise_val,
                                    replace_outliers)
        big_u.append(u)
        big_v.append(v)

    big_u = np.nanmean(big_u, axis=0)
    big_v = np.nanmean(big_v, axis=0)

    return x, y, big_u, big_v


def process_folder_of_images_batches(directory, window_size, search_area_size, window_overlap, dt, pixels_per_micron,
                                     sig2noise_val, replace_outliers, batches):

    '''
    :param directory:   Directory where you want to porcess a foler of images.
    :param batches:     The number of batches you want to process. i.e. (For 1000 image pairs, 10 batches will net 10 flow fields of 100 image pairs each)
    :return:            x-coordinates, y-coordinates, and averaged_u and v components
    '''

    image_files = os.listdir(directory)
    extension = image_files[0][-4:]
    number_of_images = len(image_files)

    if batches > number_of_images: raise ValueError("Cannot have more batches than images")

    images_per_batch = math.floor(number_of_images / batches)

    for batch in range(0, batches):

        big_x, big_y, big_u, big_v = [], [], [], []

        for image in range(batch * images_per_batch, (batch + 1) * images_per_batch - 1):
            x, y, u, v = process_images(directory + '\\' + str(image) + extension,
                                        directory + str(image + 1) + extension, window_size, search_area_size,
                                        window_overlap, dt, pixels_per_micron, sig2noise_val, replace_outliers)
            big_x.append(x)
            big_y.append(y)
            big_u.append(u)
            big_v.append(v)

        big_x = np.nanmean(big_x, axis=0)
        big_y = np.nanmean(big_y, axis=0)
        big_u = np.nanmean(big_u, axis=0)
        big_v = np.nanmean(big_v, axis=0)

        print(
            f"Processed videos {batch * images_per_batch + 1} to {(batch + 1) * images_per_batch} out of {number_of_images} in {batches} batches")

        draw_hmap(big_x, big_y, big_u, big_v,
                  directory.split('\\')[-1] + ' (' + str(batch * images_per_batch) + ' to ' + str(
                      (batch + 1) * images_per_batch) + ')' + " window_size= " + str(
                      window_size) + ", search_area= " + str(search_area_size) + ", window_overlap= " + str(
                      window_overlap))

    return big_x, big_y, big_u, big_v


def process_folders_of_images(main_directory, window_size, search_area_size, window_overlap, dt, pixels_per_micron,
                              sig2noise_val, replace_outliers, pair_limit=np.inf, mask=False, threshold_speed = None):
    
    '''
    
    :param main_directory:      The direction in which there are folders of folders of folders of image pairs.
    :param pair_limit:          How many image pairs you want to process
    :param mask:                Mask over certain regions in the flow field
    :param threshold_speed:     Threshold for speeds at and below this value
    :return:                    x-coordinates, y-coordinates, and averaged_u and v components and a strange with details of your process
    '''
    
    save_title = main_directory.split('\\')[-1] + " window_size= " + str(window_size) + ", search_area= " + str(
        search_area_size) + ", window_overlap= " + str(window_overlap) + ' val-' + str(sig2noise_val) + ' ro-' + str(
        replace_outliers)

    x, y, bulk_averaged_u, bulk_averaged_v = [], [], [], []

    folder_list = os.listdir(main_directory)

    for folder_of_images in folder_list:

        if folder_list.index(folder_of_images) + 1 > pair_limit: continue

        save_folder = str(window_size) + ' ' + str(search_area_size) + ' ' + str(window_overlap) + ' val-' + str(
            sig2noise_val) + ' ro-' + str(replace_outliers)

        if os.path.isfile('saved\\' + main_directory.split("\\")[
            -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv'):

            df = pd.read_csv('saved\\' + main_directory.split("\\")[
                -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv')
            averaged_x, averaged_y, averaged_u, averaged_v = [], [], [], []


            for i in range(0, len(df)):
                averaged_u.append(df["u" + str(i)].tolist())
                averaged_v.append(df["v" + str(i)].tolist())

            if folder_list.index(folder_of_images) == 0:
                for i in range(0, len(df)):
                    x.append(df["x" + str(i)].tolist())
                    y.append(df["y" + str(i)].tolist())

        else:
            number_of_frames = os.listdir(main_directory + '\\' + folder_of_images + '\\')

            try:
                number_of_frames.remove('.DS_Store')
            except:
                pass

            number_of_frames = len(number_of_frames)

            if number_of_frames <= 1:
                print("Skipping folder with only 1 image: " + str(folder_of_images))
                continue

            # Process the folder of images
            x, y, averaged_u, averaged_v = process_folder_of_images(main_directory + "\\" + folder_of_images + "\\",
                                                                    window_size, search_area_size, window_overlap, dt,
                                                                    pixels_per_micron, sig2noise_val, replace_outliers)

            # Combine u and v data into one dictionary
            u_v_data = {}

            for i in range(0, len(averaged_u)):
                u_v_data.update({"u" + str(i): averaged_u[i],
                                 "v" + str(i): averaged_v[i],
                                 "x" + str(i): x[i],
                                 "y" + str(i): y[i]})

            # Create a DataFrame using DataFrame function
            df = pd.DataFrame(u_v_data)

            # Specify the file path to save data
            csv_file_path = 'saved\\' + main_directory.split("\\")[
                -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv'

            # Create the folder if it does not exist
            try:
                if not os.path.exists(
                        'saved\\' + main_directory.split("\\")[-1] + '\\' + save_folder + '\\' + folder_of_images):
                    os.makedirs(
                        'saved\\' + main_directory.split("\\")[-1] + '\\' + save_folder + '\\' + folder_of_images)
            except OSError:
                print('Error: Creating directory of data')

            # Write the DataFrame to a CSV file using to_csv() function where file path is passed
            df.to_csv(csv_file_path, index=False)

            # Print a confirmation message
            print(f"CSV file {csv_file_path} created successfully")

        print(f"{folder_list.index(folder_of_images) + 1} of {len(folder_list)} completed.")

        # thresholds all flow vectors below some value threshold_speed
        if threshold_speed != None:
            vec_magnitude = calculate_magnitude(averaged_u, averaged_v)
            above_speed_threshold_indices = np.where(np.array(vec_magnitude) > threshold_speed)
            for row in above_speed_threshold_indices[0]:
                for column in above_speed_threshold_indices[1]:
                    averaged_u[row][column] = np.nan
                    averaged_v[row][column] = np.nan

        bulk_averaged_u.append(averaged_u)
        bulk_averaged_v.append(averaged_v)

    final_averaged_u = np.nanmean(bulk_averaged_u, axis=0)
    final_averaged_v = np.nanmean(bulk_averaged_v, axis=0)

    draw_hmap(x, y, final_averaged_u, final_averaged_v, save_title + ' mask-' + str(mask), mask=mask,
              search_area_size=search_area_size, window_overlap=window_overlap)

    return x, y, final_averaged_u, final_averaged_v, bulk_averaged_u, bulk_averaged_v, save_title


def process_folders_of_images_batches(main_directory, window_size, search_area_size, window_overlap, dt,
                                      pixels_per_micron, sig2noise_val, replace_outliers, batches, mask=False):
    
    '''
    :param main_directory:  The direction in which there are folders of folders of folders of image pairs.
    :param batches:         The number of batches you want to process. i.e. (For 1000 image pairs, 10 batches will net 10 flow fields of 100 image pairs each)
    :param mask:            Mask over certain regions in the flow field
    :return:                x-coordinates, y-coordinates, and averaged_u and v components
    '''

    folder_list = os.listdir(main_directory)

    folders_per_batch = math.floor(len(folder_list) / batches)

    x, y, batch_u_list, batch_v_list = [], [], [], []

    for batch in range(0, batches):

        bulk_averaged_u, bulk_averaged_v = [], []

        if batches > len(folder_list): raise ValueError("Cannot have more batches than videos")

        for folder_of_images in folder_list[batch * folders_per_batch:(batch + 1) * folders_per_batch]:

            save_folder = str(window_size) + ' ' + str(search_area_size) + ' ' + str(window_overlap) + ' val-' + str(
                sig2noise_val) + ' ro-' + str(replace_outliers)

            if os.path.isfile('saved\\' + main_directory.split("\\")[
                -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv'):

                df = pd.read_csv('saved\\' + main_directory.split("\\")[
                    -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv')
                averaged_u, averaged_v = [], []

                for i in range(0, len(df)):
                    averaged_u.append(df["u" + str(i)].tolist())
                    averaged_v.append(df["v" + str(i)].tolist())

                if folder_list.index(folder_of_images) == 0:
                    for i in range(0, len(df)):
                        x.append(df["x" + str(i)].tolist())
                        y.append(df["y" + str(i)].tolist())

            else:
                number_of_frames = os.listdir(main_directory + '\\' + folder_of_images + '\\')

                try:
                    number_of_frames.remove('.DS_Store')
                except:
                    pass

                number_of_frames = len(number_of_frames)

                if number_of_frames == 1:
                    print("Skipping folder with only 1 image: " + str(folder_of_images))
                    continue

                # Process the folder of images
                averaged_x, averaged_y, averaged_u, averaged_v = process_folder_of_images(
                    main_directory + "\\" + folder_of_images + "\\", window_size, search_area_size, window_overlap, dt,
                    pixels_per_micron, sig2noise_val, replace_outliers)

                # Combine u and v data into one dictionary
                u_v_data = {}
                x, y = [], []

                for i in range(0, len(averaged_u)):
                    u_v_data.update({"x" + str(i): x[i],
                                     "y" + str(i): y[i],
                                     "u" + str(i): averaged_u[i],
                                     "v" + str(i): averaged_v[i]})

                # Create a DataFrame using DataFrame function
                df = pd.DataFrame(u_v_data)

                # Specify the file path to save data
                csv_file_path = 'saved\\' + main_directory.split("\\")[
                    -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv'

                # Create the folder if it does not exist
                try:
                    if not os.path.exists(
                            'saved\\' + main_directory.split("\\")[-1] + '\\' + save_folder + '\\' + folder_of_images):
                        os.makedirs(
                            'saved\\' + main_directory.split("\\")[-1] + '\\' + save_folder + '\\' + folder_of_images)
                except OSError:
                    print('Error: Creating directory of data')

                # Write the DataFrame to a CSV file using to_csv() function where file path is passed
                df.to_csv(csv_file_path, index=False)

                print('saved\\' + main_directory.split("\\")[
                    -1] + '\\' + save_folder + '\\' + folder_of_images + '\\data.csv')
                # Print a confirmation message
                print(f"CSV file {csv_file_path} created successfully")

            print(f"{folder_list.index(folder_of_images) + 1} of {len(folder_list)} completed.")

            bulk_averaged_u.append(averaged_u)
            bulk_averaged_v.append(averaged_v)

        # Convert the bulk averaged magnitudes to float arrays to properly replace 0s with nans
        final_averaged_u = np.nanmean(bulk_averaged_u, axis=0)
        final_averaged_v = np.nanmean(bulk_averaged_v, axis=0)

        title = main_directory.split('\\')[-1] + ' (' + str(batch * folders_per_batch) + ' to ' + str(
            (batch + 1) * folders_per_batch) + ')' + " window_size= " + str(window_size) + ", search_area= " + str(
            search_area_size) + ", window_overlap= " + str(window_overlap)

        draw_hmap(x, y, final_averaged_u, final_averaged_v, title, search_area_size=search_area_size,
                  window_overlap=window_overlap, mask=mask)

        batch_u_list.append(final_averaged_u)
        batch_v_list.append(final_averaged_v)

    return x, y, final_averaged_u, final_averaged_v


def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#")  # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v / 256 for v in value]


def calculate_magnitude(u_matrix, v_matrix):
    w, h = shape(u_matrix)[0], shape(u_matrix)[1]
    magnitude = [[0 for x in range(w)] for y in range(h)]

    for a in range(0, h, 1):
        for b in range(0, w, 1):
            magnitude[a][b] = math.sqrt(u_matrix[a][b] ** 2 + v_matrix[a][b] ** 2)
    return magnitude


def draw_hmap(x, y, u, v, title, mask=False, search_area_size=None, window_overlap=None):
    # Re-replace nans with 0s
    u = np.nan_to_num(u, copy=True, nan=0.0)
    v = np.nan_to_num(v, copy=True, nan=0.0)

    # Multiply the average calculated magnitudes with microns per vector to get microns/second
    averaged = calculate_magnitude(u, v)

    hex_list = ['#4D68FF', '30A7C9', '#51E34F', '#FFFF4D', 'F5A311', '#FF2B00']

    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    float_list = list(np.linspace(0, 1, len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmap = mcolors.LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)

    plt.figure(figsize=(10, 10))

    # Adding and styling axis labels
    plt.xlabel('$\u03BC$m', fontsize=35, color="k")
    plt.xticks(fontsize=20, color="k")
    plt.xlim(0, max(x[0]) + min(x[0]))
    plt.ylabel('$\u03BC$m', fontsize=35, color="k")
    plt.yticks(fontsize=20, color="k")
    plt.ylim(0, max(x[0]) + min(x[0]))

    plt.title(title, fontsize=20, color="white")

    # plt.gca().invert_xaxis()

    y = np.flip(y)

    if mask:
        # Import the pre-made mask
        mask = tools.imread('mask.tif')

        x_mask, y_mask = pyprocess.get_coordinates(image_size=mask.shape, search_area_size=search_area_size,
                                                   overlap=window_overlap)
        grid_mask = preprocess.prepare_mask_on_grid(x_mask, y_mask, preprocess.mask_coordinates(mask))
        masked_u = np.ma.masked_array(u, mask=grid_mask)
        masked_v = np.ma.masked_array(v, mask=grid_mask)
        plt.quiver(x, y, masked_u, -masked_v)
    else:
        plt.quiver(x, y, u, -v)

    plt.imshow(averaged, cmap=cmap, interpolation='gaussian', origin='lower', vmin=0,
               vmax=max([sublist[-1] for sublist in averaged]), extent=(min(x[0]), max(x[0]), max(x[0]), min(x[0])))

    cbar = plt.colorbar(matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(min([sublist[-1] for sublist in averaged]),
                                         max([sublist[-1] for sublist in averaged])), cmap=cmap), ax=plt.gca())

    # Change fontsize of colorbar
    cbar.ax.tick_params(labelsize=35, colors="k")
    cbar.set_label(label="Speed [$\u03BC$m/s]", size=50, color="k")

    # the heatmap is saved
    plt.savefig('Heatmap Figures\\' + title + '.png')
    plt.show()


def average_left_right_vecs(x, y, u, v):
    u = np.array(u)
    v = np.array(v)

    num_x_vectors = len(x[0])

    if num_x_vectors % 2 == 0:  # If even
        half_num_x_vectors = int(num_x_vectors / 2)
    else:
        half_num_x_vectors = int(math.floor(num_x_vectors / 2))

    if len(u.shape) == 2:

        # us and vs on the left side:
        u_left = u[:, :half_num_x_vectors]
        v_left = v[:, :half_num_x_vectors]

        # us and vs on the right side:
        u_right = -u[:, half_num_x_vectors:]  # Make negative because we're reflecting the right onto the left side
        u_right = u_right[:, ::-1]  # Flip the values from left to right to then right to left
        v_right = v[:, half_num_x_vectors:]
        v_right = v_right[:, ::-1]  # # Flip the values from left to right to then right to left

        # average u and v components
        u_averaged = np.nanmean((u_left, u_right), axis=0)
        v_averaged = np.nanmean((v_left, v_right), axis=0)

        # replace both component sides with averaged values
        u[:, :half_num_x_vectors] = u_averaged
        u[:, half_num_x_vectors:] = -u_averaged[
            :, ::-1]  # To properly reflect we change the direction and flip from the left side
        v[:, :half_num_x_vectors] = v_averaged
        v[:, half_num_x_vectors:] = v_averaged[:, ::-1]  # Reflect from the left to the right side

    elif len(u.shape) == 3:

        # us and vs on the left side:
        u_left = u[:, :, :half_num_x_vectors]
        v_left = v[:, :, :half_num_x_vectors]

        # us and vs on the right side:
        u_right = -u[:, :, half_num_x_vectors:]  # Make negative because we're reflecting the right onto the left side
        u_right = u_right[:, :, ::-1]  # Flip the values from left to right to then right to left
        v_right = v[:, :, half_num_x_vectors:]
        v_right = v_right[:, :, ::-1]  # # Flip the values from left to right to then right to left

        # average u and v components
        u_averaged = np.nanmean((u_left, u_right), axis=0)
        v_averaged = np.nanmean((v_left, v_right), axis=0)

        # replace both component sides with averaged values
        u[:, :, :half_num_x_vectors] = u_averaged
        u[:, :, half_num_x_vectors:] = -u_averaged[
            :, :, ::-1]  # To properly reflect we change the direction and flip from the left side
        v[:, :, :half_num_x_vectors] = v_averaged
        v[:, :, half_num_x_vectors:] = v_averaged[:, :, ::-1]  # Reflect from the left to the right side

    else:

        raise ValueError("Shape of vector components invalid:\n"
                         "u.shape = " + str(u.shape) + ", v.shape = " + str(v.shape))

    return u, v


def draw_hmap_lines(x, y, u, v, title, line_density=1):
    # Re-replace nans with 0s
    u = np.nan_to_num(u, copy=True, nan=0.0)
    v = np.nan_to_num(v, copy=True, nan=0.0)

    # Multiply the average calculated magnitudes with microns per vector to get microns/second
    averaged = calculate_magnitude(u, v)

    hex_list = ['#4D68FF', '30A7C9', '#51E34F', '#FFFF4D', 'F5A311', '#FF2B00']

    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    float_list = list(np.linspace(0, 1, len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmap = mcolors.LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)

    plt.figure(figsize=(10, 10))

    # Adding and styling axis labels
    plt.xlabel('$\u03BC$m', fontsize=35, color="k")
    plt.xticks(fontsize=20, color="k")
    plt.xlim(0, max(x[0]) + min(x[0]))
    plt.ylabel('$\u03BC$m', fontsize=35, color="k")
    plt.yticks(fontsize=20, color="k")
    plt.ylim(0, max(x[0]) + min(x[0]))

    speed = np.sqrt(np.asarray(u ** 2 + np.asarray(v) ** 2))
    lw = 5 * speed / speed.max()

    u_arr = np.asarray(u)
    v_arr = np.asarray(v)

    plt.title(title, fontsize=20, color="white")

    plt.imshow(averaged, cmap=cmap, interpolation='gaussian', origin='lower', vmin=0,
               vmax=max([sublist[-1] for sublist in averaged]), extent=(min(x[0]), max(x[0]), min(x[0]), max(x[0])))

    cbar = plt.colorbar(matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(min([sublist[-1] for sublist in averaged]),
                                         max([sublist[-1] for sublist in averaged])), cmap=cmap), ax=plt.gca())

    # Change fontsize of colorbar
    cbar.ax.tick_params(labelsize=35, colors="k")
    cbar.set_label(label="Speed [$\u03BC$m/s]", size=50, color="k")

    plt.streamplot(np.asarray(x), np.asarray(y), u_arr, v_arr,
                   density=line_density, linewidth=lw, arrowsize=3, arrowstyle='->', color='k')
    plt.gca().invert_yaxis()

    # the heatmap is saved
    plt.savefig('Heatmap Figures\\' + title + '.png')
    plt.show()
