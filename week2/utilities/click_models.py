# Implements various click models
import pandas as pd
import numpy as np

# cmc tmp
im1_shown = False
im2_shown = False


def binary_func(x):
    if x > 0:
        return 1
    return 0


def step(x):

    # ------------------------------------------------------------------------
    # cmc todo():
    # . print("IMPLEMENT ME: step(x) a step function with a simple heuristic that buckets grades")
    #
    # reference:
    # . adapted from ltr_toy + class instructions
    #
    global im1_shown
    if not im1_shown:
        print("\n     >>>>>>>>>> IMPLEMENT ME: step(x) a step function with a simple heuristic that buckets grades \n")
        im1_shown = True

    return rng.choice([0,0.5, 1.0])


rng = np.random.default_rng(123456)
# Given a click model type, transform the "grade" into an appropriate value between 0 and 1, inclusive
# This operates on the data frame and adds a "grade" column
#
def apply_click_model(data_frame, click_model_type="binary", downsample=True):
    if click_model_type == "binary":
        print("Binary click model") # if we have at least one click, count it as relevant
        data_frame["grade"] = data_frame["clicks"].apply(lambda x: binary_func(x))
        if downsample:
            data_frame = down_sample_buckets(data_frame)
    elif click_model_type == "ctr":
        data_frame["grade"] = (data_frame["clicks"]/data_frame["num_impressions"]).fillna(0)
        if downsample:
            data_frame = down_sample_continuous(data_frame)
    elif click_model_type == "heuristic":
        data_frame["grade"] = (data_frame["clicks"]/data_frame["num_impressions"]).fillna(0).apply(lambda x: step(x))

        # ------------------------------------------------------------------------
        # cmc todo():
        # . print("IMPLEMENT ME: apply_click_model(): downsampling")
        #
        # reference:
        # . adapted from ltr_toy + class instructions
        #
        global im2_shown
        if not im2_shown:
            print("\n     >>>>>>>>>> IMPLEMENT ME: apply_click_model(): downsampling \n")
            im2_shown = True

    return data_frame

# https://stackoverflow.com/questions/55119651/downsampling-for-more-than-2-classes
def down_sample_buckets(data_frame):
    g = data_frame.groupby('grade', group_keys=False)
    return pd.DataFrame(g.apply(lambda x: x.sample(g.size().min()))).reset_index(drop=True)


# Generate the probabilities for our grades and then use that to sample from
# from: https://stackoverflow.com/questions/63738389/pandas-sampling-from-a-dataframe-according-to-a-target-distribution
# If you want to learn more about this, see http://www.seas.ucla.edu/~vandenbe/236C/lectures/smoothing.pdf
def down_sample_continuous(data_frame):
    x = np.sort(data_frame['grade'])
    f_x = np.gradient(x)*np.exp(-x**2/2)
    sample_probs = f_x/np.sum(f_x)
    try: # if we have too many zeros, we can get value errors, so first try w/o replacement, then with
        sample = data_frame.sort_values('grade').sample(frac=0.8, weights=sample_probs, replace=False)
    except Exception as e:
        print("Unable to downsample, keeping original:\n%s" % e)
        sample = data_frame #data_frame.sort_values('grade').sample(frac=0.8, weights=sample_probs, replace=True)
    return sample

