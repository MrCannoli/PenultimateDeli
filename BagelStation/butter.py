# Use XGBoost to generate an AI
# Reference: https://xgboost.readthedocs.io/en/stable/python/python_intro.html#python-data-interface

import xgboost as xgb
import os
import random

# Number of past days data used in the input files
input_num_days = 2

# Base name for the test. Used to generate file names.
test_basename = f"Test_{input_num_days}_days"

model_filepath_base = f'GeneratedModels/{test_basename}/'
train_file = f'../CuttingBoard/ParsedData/filtered_data_6-10_stripped/{input_num_days}_days/combined_train.csv'
test_file = f'../CuttingBoard/ParsedData/filtered_data_6-10_stripped/{input_num_days}_days/combined_test.csv'

if not os.path.exists(model_filepath_base):
    os.mkdir(model_filepath_base)

rand_seed = random.randint(0,1000000)
print(f"Seed is {rand_seed}")

# Import training data file
# Docs recommended to use sklearn's load_svmlight_file instead
dtrain = xgb.DMatrix(train_file)
dtrain.save_binary(f'{model_filepath_base}train.buffer')

# Import test data file
dtest = xgb.DMatrix(test_file)

eval_list = [(dtest, 'eval'), (dtrain, 'train')]

model_params = {'max_depth':24, 'eta':.3, 'objective':"reg:squarederror", 'nthread': 6, 'tree_method': 'gpu_hist', 'eval_metric':'mape',
                'lambda': 1, 'alpha': 0, 'grow_policy': 'depthwise', 'num_parallel_tree': 1, 'max_bin': 2048, 'seed': rand_seed}
# Potential objective values: reg:squarederror, reg:squaredlogerror
# Could update the 'eval_metric' as needed - though mean absolute percentage error has best results from testing
# Could remove 'nthread' to allow this to use all cores/threads
# Additional interesting parameters: lambda, alpha, gamma
# Max bin is the default 256 - Increasing this has shown general improvement
# Can increase trees used with `num_parallel_tree` (default 1). Seems to improve learning rate, but greatly increases computation time - net zero benefit.
# Can read up on params here: https://xgboost.readthedocs.io/en/stable/parameter.html

num_rounds = 2000

# Train the model with the given data and inputs
bst = xgb.train(model_params, dtrain, num_rounds, eval_list)
# Optionally, can load a pretrained model with bst = xgb.Booster(model_params), bst.load_model(<model_filename>)

'''
# Set of random extra eval data
randdata = xgb.DMatrix('inputdata.csv')

preds = bst.predict(randdata)
print("Predictions: ")
print(preds)
'''

bst.save_model(f'{model_filepath_base}{test_basename}.model')

# dump model with feature map
raw_model_dumpfile = f'{model_filepath_base}{test_basename}_raw.txt'
raw_model_featmap = f'{model_filepath_base}{test_basename}_featmap.txt'

# Need to create the raw files if they don't already exist
# Otherwise XGBoost complains
if not os.path.exists(raw_model_dumpfile):
    # Creates a new file
    with open(raw_model_dumpfile, 'w') as fp:
        pass

if not os.path.exists(raw_model_featmap):
    # Creates a new file
    with open(raw_model_featmap, 'w') as fp:
        pass

bst.dump_model(raw_model_dumpfile, raw_model_featmap)