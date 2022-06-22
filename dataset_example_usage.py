import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
#import tensorflow as tf
import copy
import matplotlib.pyplot as plt
import os
import imageio
from sklearn.utils import shuffle

from uah_dataset.pandas_importer import UAHDataset
from uah_dataset.image_process import add_pointers_to_window, dict_with_all_frames_pointed, video_to_frames, create_windowed_frames
import shutil
import pickle
from datetime import datetime
import argparse
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler

# TODO: find missing headers: have a look into their data reader again
# EFFORT: 2h (at most)

# TODO: sample frame of video corresponding to sensor data depending on time step
# EFFORT: 2h (depending on libraries i can use)

# TODO: apply some preprocessing on image data (image normalization, contrast sharpening, …)
# EFFORT depends on the amount of preprocessing

# TODO: save this form of dataset created by us and save it (using pandas and/or our own datastructure)

# to extract video data (run this one time only to set up your dataset correctly)
# UAHDataset(generate_video_frames=True)

# create the dataset
#dataset = UAHDataset()
# print("Dataset:", dataset.latest)
# print("Drivers:", dataset.drivers)

# #testorprint(1)


# '''# read one specific driver
# print("Info of driver D1")
# road_type_dict = dataset.dataframe_by_driver("D1", skip_missing_headers=True, suppress_warings=True)
# roads = [_ for _ in road_type_dict.keys()]
# print("Roads:\t", roads)
# print("# Roads:", sum([len(road_type_dict[_]) for _ in roads]))

# # read all drivers
# # note: this should work, but we loose information about when a time series resets.
# # This could prevent learning later on.
# print("Info of all drivers")'''
#road_type_dict = dataset.dataframe(skip_missing_headers=True, suppress_warings=True)

# '''roads = [_ for _ in road_type_dict.keys()]
# print("# Roads:", sum([len(road_type_dict[_]) for _ in roads]))

# for r, rd in road_type_dict.items():
#     print(f"\t{r} - {len(rd)}")
#     for l, ld in rd.items():
#         print(f"\t\t{l} - {len(ld)}")

# # process one specific dataframe'''
# array = []
# for road_type in road_type_dict.items():
#     print(1)

#     skip = True
#     for route in road_type[1].items():
#         mean = np.array(route[1].mean())
#         array.append(mean)

# #print(road_type_dict["SECONDARY"]["NORMAL"][['Altitude', 'Longitude', 'Latitude']].head(5))
# #'Altitude', 'Longitude', 'Latitude'

# fused_data = np.array(array)
# fused_data[np.isnan(fused_data)]=0

# kmeans = KMeans(n_clusters=2, random_state=0).fit(fused_data)



# define model
'''
visible = Input(shape=(8,))
# encoder level 1
e = Dense(n_inputs*2)(visible)
e = BatchNormalization()(e)
e = LeakyReLU()(e)
# encoder level 2
e = Dense(n_inputs)(e)
e = BatchNormalization()(e)
e = LeakyReLU()(e)
# bottleneck
n_bottleneck = n_inputs
bottleneck = Dense(n_bottleneck)(e)

# define decoder, level 1
d = Dense(n_inputs)(bottleneck)
d = BatchNormalization()(d)
d = LeakyReLU()(d)
# decoder level 2
d = Dense(n_inputs*2)(d)
d = BatchNormalization()(d)
d = LeakyReLU()(d)
# output layer
output = Dense(n_inputs, activation='linear')(d)
# define autoencoder model
model = Model(inputs=visible, outputs=output)

# compile autoencoder model
model.compile(optimizer='adam', loss='mse')

history = model.fit(X_train, X_train, epochs=200, batch_size=16, verbose=2, validation_data=(X_test,X_test))
'''


'''Then we will extract the inner layer after training'''


'''We will finaly cluster based on the representation'''
# print(kmeans.labels_)


def windowing(dictionary : dict ,rows_per_minute : int = 360, initial_threshold : int = 60, increment : int = 10) -> dict:
    """
    Creates windows, for every
    :param dictionary: nested dic road types -> mood -> dataframe
    :param rows_per_minute: number of rows that on average constitute one minute
    :param initial_threshold: timestamp when we start to approve the windows
    :param increment: timestamp difference between end of adjacent windows
    :return: dictionary: road type -> mood -> window_index -> dataframe
    """

    windowed_dic = copy.deepcopy(dictionary)
    window_number = 0
    window_time = 0
    time_difference = []

    for road, road_dic in dictionary.items():
        i = 0
        print(f"______________________Road: {road} _________________________________")
        for mood, mood_df in road_dic.items():
            windowed = {}
            t = initial_threshold                                    #first window ends at a point where more than t seconds have passed
            print(f"Mood: {mood}")
            '''for window in mood_df.rolling(window = rows_per_minute, min_periods = rows_per_minute):
                if window.shape != (2,41):
                    print('something went wrong')
                if window.iloc[-1, 0] < window.iloc[0, 0]:  # meaning we have finished one driver trip, as the nnext df values are lower than the previous
                    #TODO keep an eye om this
                    t = initial_threshold
                elif int(window.iloc[-1, 0]) > t:
                    #TODO time does not begin from zero
                    windowed[i] = window
                    i += 1
                    t += increment                     #creates 10 second windows
                    window_number += 1
                    time = (window.iloc[-1, 0]-window.iloc[0,0])+1
                    window_time += time
                    time_difference.append(time)'''

            for j in mood_df.index:
                try:
                    window = mood_df[j:j+window_size]
                except Exception:
                    pass
                if window.shape != (window_size,41):
                    print('pass')
                    pass
                if window.iloc[-1, 0] < window.iloc[0, 0]:  # meaning we have finished one driver trip, as the nnext df values are lower than the previous
                    #TODO keep an eye om this
                    t = initial_threshold
                elif int(window.iloc[-1, 0]) > t:
                    #TODO time does not begin from zero
                    windowed[i] = window
                    i += 1
                    t += increment                     #creates 10 second windows
                    window_number += 1
                    time = (window.iloc[-1, 0]-window.iloc[0,0])+1
                    window_time += time
                    time_difference.append(time)
            windowed_dic[road][mood] = windowed
    print(f"Average window timelapse: {window_time/window_number}")
    print(f"Number of windows: {window_number}")
    plt.hist(time_difference, bins = 120)
    plt.title(f"Window timelapse for {rows_per_minute} data points.")
    plt.xlabel("Seconds")
    #plt.show()
    return windowed_dic



def read(path_to_uah_folder: str = f"{os.path.dirname(__file__)}/uah_dataset/UAH-DRIVESET-v1/"):
    """
    Mainly copied from the original reader
    :param path_to_uah_folder:
    :return: Online semantics, in nested dictionary ->road type -> mood -> dataframe for all driver on this mood and road type
    """
    root_dir = "./uah_dataset/"
    latest = "UAH-DRIVESET-v1/"
    drivers = ['D1','D2','D3','D4','D5','D6']
    roads = ["MOTORWAY", "SECONDARY"]

    headers = ["time", "Latitude" , " Longitude", "Total" , "Accel", "Braking", "Turning", "Weaving",
                "Drifting", "Oversspeed", "Carfollow", "Normal", "Drowsy", "Aggressive", "Unknown",
                "Total_last_minute", "Accel_last_minute", "Braking_last_minute" , "Turning_last_minute",
                "Weaving_last_minute","Drifting_last_minute", "Oversspeed_last_minute", "Carfollow_last_minute",
                "Normal_last_minute", "Drowsy_last_minute", "Aggressive_last_minute", "Unknown_last_minute"
                ]
    online_semantics = {}
    for driver in drivers:
        folder = f"{path_to_uah_folder}{driver}"
        for direc in os.listdir(folder):
            splitted_string = direc.split('-')
            road = splitted_string[-1]
            mood = splitted_string[-2]
            scoresFileName = folder + '/' + direc + '/' + 'SEMANTIC_ONLINE.txt'
            scoresData = np.genfromtxt(scoresFileName, dtype=np.float64, delimiter=' ')
            df = pd.DataFrame(scoresData, columns = headers)
            df['Driver'] = driver
            if road in online_semantics:
                if mood in online_semantics[road]:
                    online_semantics[road][mood] = pd.concat([online_semantics[road][mood], df])
                else:
                    online_semantics[road][mood] = df
            else:
                online_semantics.update({road : {mood : df}})


    return online_semantics

def reshaping_to_numpy(dataf : pd.DataFrame, window_size):
    feature_size = list(list(list(dataf.values())[0].values())[0].values())[0].shape[1] #TODO change that again
    train = np.empty([0,window_size, feature_size])
    labels = np.empty([0,3], dtype=int)
    for road, road_dic in dataf.items():
        for mood, mood_df in road_dic.items():
            if "NORMAL" in mood:
                label = np.array([1,0,0], dtype=int)
            elif "AGGRESSIVE" in mood:
                label = np.array([0,1,0], dtype=int)
            elif "DROWSY" in mood:
                label = np.array([0,0,1], dtype=int)
            else:
                raise RuntimeError(mood , " does not correspond to any existing labels")

            for i in mood_df:
                # FIXME: window size can be smaller than specified
                #if mood_df[i].shape[0] != window_size:
                #    continue
                train = np.concatenate((train, mood_df[i].values[np.newaxis,...]), axis=0)
                labels = np.concatenate((labels, label[np.newaxis,...]), axis=0)
            print('Iteration passed')
    print(train.shape)
    print(labels.shape)

    return train, labels



def sensor_data_prepare(window_size):
    now = datetime.now()  # current date and time
    # Read data from files and store to panda frames
    dataset = UAHDataset()
    road_type_dict = dataset.dataframe(skip_missing_headers=True, suppress_warings=True)
    # Windowing the dataset
    windowed_dic = copy.deepcopy(road_type_dict)
    rows_per_minute = window_size  # args.window_size  # for dataframe, doesnt work consistently
    online_semantic = windowing(windowed_dic, rows_per_minute=rows_per_minute)
    pass
    # Reshaping to numpy
    train, labels = reshaping_to_numpy(online_semantic, window_size)

    n_samples = len(train)
    indexing = np.random.permutation(n_samples)

    (train,labels) = (train[indexing],labels[indexing])

    npy_new_dir = './uah_dataset/processed_dataset/sensor'
    if not os.path.exists(npy_new_dir):
        os.mkdir(npy_new_dir)
    npy_new_dir = npy_new_dir + '/npy'
    if not os.path.exists(npy_new_dir):
        os.mkdir(npy_new_dir)
    npy_new_dir = npy_new_dir + '/window_' + str(window_size)
    if os.path.exists(npy_new_dir):
        shutil.rmtree(npy_new_dir)
    os.mkdir(npy_new_dir)
    np.save(npy_new_dir + '/train_' + now.strftime("%m_%d_%Y-%H_%M_%S"), train)
    np.save(npy_new_dir + '/labels_' + now.strftime("%m_%d_%Y-%H_%M_%S"), labels)



    parent_dir = './uah_dataset/processed_dataset/sensor/npy/window_' + str(window_size)
    train_path = labels_path = None
    for file in os.listdir(parent_dir):
        if "train" in file:
            train_path = file
        else:
            labels_path = file
            
    # read data
    train = np.load(parent_dir + "/" + train_path, allow_pickle=True)
    labels = np.load(parent_dir + "/" + labels_path, allow_pickle=True)
    train_processed = train

    # train = np.load("train.npy",allow_pickle=True)
    # labels = np.load("labels.npy",allow_pickle=True)



    # 0:(OUT) Timestamp
    # 1: Car position form lane center (m)
    # 2: Phi
    # 3:(OUT) Road width
    # 4: State of lane estimator
    # 5: Current road max speed
    # 6:(OUT) Max speed reliability
    # 7:(OUT) Road type
    # 8: #lanes in road
    # 9: estimated current lane
    # 10: Latitude used to query OSM
    # 11:(OUT) Longitude used to query OSM
    # 12:(OUT) Delay answer OSM Query (s)
    # 13:(OUT) Speed (kmh)
    # 14: Distance to ahead vehicle
    # 15: Impact to ahead vehicle (s)
    # 16: Detectet # of vehicles
    # 17: GPS speed (kmh)
    # 18: Activation Boolean (speed>50kmh)
    # 19: X acceleration (Gs)
    # 20: Y acceleration(Gs)
    # 21:(OUT) Z acceleration(Gs)
    # 22: X acceleration (Gs)(Kernel Filter)
    # 23: Y acceleration(Gs)(Kernel Filter)
    # 24: Z acceleration(Gs)(Kernel Filter)
    # 25: Roll
    # 26:(OUT) Pitch
    # 27:(OUT) Yaw
    # 28:(OUT)Speed
    # 29:(OUT) Latitude
    # 30:(OUT) Longitude
    # 31:(OUT) Altitude
    # 32: Vertical Accuracy
    # 33: Horizontal accuracy
    # 34: Course
    # 35: Difcourse: course variation
    # 36:(OUT) Position state
    # 37:(OUT) Lanex dist state
    # 38:(OUT) Lanex history
    # 39:(OUT) Unknown
    # 40:(OUT) Driver


    idx_OUT_columns = [0, 3, 6, 7, 11, 12, 13, 21,26,27,28, 29, 30, 31, 36, 37, 38, 39, 40]
    idx_IN_columns = [i for i in range(np.shape(train_processed)[2]) if i not in idx_OUT_columns]
    extractedData = train_processed[:, :, idx_IN_columns]

    extractedData = extractedData.astype(np.float32)
    #Remove NaN values
    extractedData = np.nan_to_num(extractedData, copy=True, nan=0.0, posinf=None, neginf=None)

    #Normalize train by feautures (column)
    scalers = {}
    for i in range(extractedData.shape[2]):
        scalers[i] = StandardScaler() if scaler == "standard" else MinMaxScaler()
        extractedData[:, :, i] = scalers[i].fit_transform(extractedData[:, :, i]) 

    #for test
    '''for i in range(extractedData.shape[2]):
        extractedData[:, :, i] = scalers[i].transform(extractedData[:, :, i])'''

    """#Normalize train by feautures (column)
    # FIXME: normalize over the whole dataset
    for j in range(len(extractedData)):
        df1=pd.DataFrame(extractedData[j])
        for i in range(0, len(idx_IN_columns)):
            df1[i] = (df1[i] / (df1[i].abs().max()+0.01)).astype(float)

        extractedData[j]=df1.to_numpy()"""

    # save data to .dat format
    dat_new_dir = './uah_dataset/processed_dataset/sensor'
    if not os.path.exists(dat_new_dir):
        os.mkdir(dat_new_dir)
    dat_new_dir = dat_new_dir + '/dat'
    if not os.path.exists(dat_new_dir):
        os.mkdir(dat_new_dir)
    dat_new_dir = dat_new_dir + '/window_' + str(window_size)

    if os.path.exists(dat_new_dir):
        shutil.rmtree(dat_new_dir)
    os.mkdir(dat_new_dir)

    # save train data
    fp = np.memmap(dat_new_dir + '/train_' + now.strftime("%m_%d_%Y-%H_%M_%S") + ".dat", dtype='float32', mode='w+',
                   shape=extractedData.shape)
    fp[:] = extractedData[:]
    fp.flush()
    del fp

    print(extractedData.shape)



    # save label data
    labels_processed = labels
    dp = np.memmap(dat_new_dir + '/labels_' + now.strftime("%m_%d_%Y-%H_%M_%S") + ".dat", dtype='int', mode='w+',
                   shape=labels_processed.shape)
    dp[:] = labels_processed[:]
    dp.flush()

    del dp

    # save shape
    dict = {'sensor': extractedData.shape, 'labels': labels_processed.shape}
    file = open(dat_new_dir + '/shape.txt', 'wb')
    pickle.dump(dict, file)
    file.close()

    return indexing, n_samples, online_semantic

scaler = "minmax"
if __name__ == "__main__":
    # Create the parser
    dataset = UAHDataset()
    road_type_dict = dataset.dataframe(skip_missing_headers=True, suppress_warings=True)

    parser = argparse.ArgumentParser(description='Preprocessing stage')
    parser.add_argument('--window_size', type=int, help='window_size', required=True)
    parser.add_argument('--scaler', type=str, help='either minmax or standard', required=True)
    args = parser.parse_args()
    window_size = args.window_size
    scaler = args.scaler
    
    (indexing, n_samples, online_semantic) = sensor_data_prepare(window_size)
    fps = (window_size/60)
    video_to_frames(fps)
    create_windowed_frames(window_size, indexing, n_samples, online_semantic)




