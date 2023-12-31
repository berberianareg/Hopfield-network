"""Discrete Hopfield network as content-addressable memory (CAM).

Notes
-----
  This script is version v0. It provides the base for all subsequent
  iterations of the project.
  
Requirements
------------
  See "requirements.txt"
  
Comments
--------
  Units are updated in random order, but each unit is updated at the same average rate.
  The network has no self-connections (zero weights on the matrix diagonal).
  Only one unit updates its activation at a time (asynchronous update rule).
  The patterns to be memorized are three alphabet letters 'a', 'b' and 'c'.
  The number of stored patterns is much smaller than the number of units.
  The initial network activation is equal to the external input.
  The network is presented with bipolar patterns (-1 and +1).
  There is no external input after the initial time step.
  The network has symmetric weights (W = W.T).
  
"""

#%% import libraries and modules
import matplotlib.pyplot as plt
import numpy as np  
import random
import os

#%% figure parameters
plt.rcParams['figure.figsize'] = (6,6)
plt.rcParams['lines.linewidth'] = 5
plt.rcParams['font.size']= 15

#%% build Hopfield class

class Hopfield:
    """Hopfield class."""
    
    def __init__(self, num_repetitions=200, num_iterations=1):
        # number of repetitions for recall performance simulation
        self.num_repetitions = num_repetitions
        # number of iterations for update rule
        self.num_iterations = num_iterations
    
    def make_inputs(self):
        """Generate input patterns."""
        # 49-dimensonal pattern 'a' to be memorized
        memorized_pattern_a = np.array([[-1], [-1], [-1], [-1], [-1], [-1], [-1],
                                        [-1], [-1], [-1], [-1], [-1], [-1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [ 1], [-1], [-1],
                                        [-1], [-1], [-1], [-1], [ 1], [ 1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [ 1], [ 1], [-1],
                                        [ 1], [-1], [-1], [-1], [ 1], [ 1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [-1], [ 1], [ 1]])
        # 49-dimensonal pattern 'b' to be memorized
        memorized_pattern_b = np.array([[ 1], [ 1], [ 1], [-1], [-1], [-1], [-1],
                                        [-1], [ 1], [ 1], [-1], [-1], [-1], [-1],
                                        [-1], [ 1], [ 1], [-1], [-1], [-1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [ 1], [ 1], [-1],
                                        [-1], [ 1], [ 1], [-1], [-1], [-1], [ 1],
                                        [-1], [ 1], [ 1], [-1], [-1], [-1], [ 1],
                                        [ 1], [ 1], [-1], [ 1], [ 1], [ 1], [-1]])
        # 49-dimensonal pattern 'c' to be memorized
        memorized_pattern_c = np.array([[-1], [-1], [-1], [-1], [-1], [-1], [-1],
                                        [-1], [-1], [-1], [-1], [-1], [-1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [ 1], [-1], [-1],
                                        [ 1], [ 1], [-1], [-1], [ 1], [ 1], [-1],
                                        [ 1], [ 1], [-1], [-1], [-1], [-1], [-1], 
                                        [ 1], [ 1], [-1], [-1], [ 1], [ 1], [-1],
                                        [-1], [ 1], [ 1], [ 1], [ 1], [-1], [-1]])
        
        # extract number of units and number of patterns to be memorized
        num_units, num_memorized_patterns = np.hstack((memorized_pattern_a, memorized_pattern_b, memorized_pattern_c)).shape
        
        return memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, num_units, num_memorized_patterns
    
    def activation_function(self, local_field, state_vector, index):
        """Apply signum function as activation function."""        
        # if induced local field equals 0, remain in previous state
        if np.sign(local_field) == 0:
            y = state_vector[index]
        # otherwise, get sign of the local field
        else:
            y = np.sign(local_field)
        
        return y
    
    def storage_phase(self, memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, num_units, num_memorized_patterns):
        """Generate connection weights using the outer-product rule of storage."""
        # compute outer products
        outer_product_a = memorized_pattern_a * memorized_pattern_a.T
        outer_product_b = memorized_pattern_b * memorized_pattern_b.T
        outer_product_c = memorized_pattern_c * memorized_pattern_c.T
        
        # compute outer product sum
        outer_product_sum = outer_product_a + outer_product_b + outer_product_c
        
        # generate diagonal matrix
        diagonal_matrix = num_memorized_patterns * np.eye(num_units)
        
        # compute weights
        weights = (outer_product_sum - diagonal_matrix) / num_units
        
        # check that there is no self-feedback in network
        assert (np.diag(weights)==0).all()
        
        # check that the weight matrix of network is symmetric
        assert (weights.T == weights).all()
        
        return weights
        
    def recall_phase(self, noisy_pattern, weights, num_units):
        """Apply recall (retrieval) phase using the asynchronous updating procedure."""
        # set initial state vector equal to noisy input (external input)
        state_vector = noisy_pattern.copy()
        
        for iteration_count in range(self.num_iterations):
            
            # generate list of random samples
            random_sample = random.sample(range(num_units), num_units)
            
            # initialize sample index
            sample_index = 0
            while sample_index < num_units:
                
                # random selection of sample
                random_choice = random_sample[sample_index]
                
                # compute induced local field
                local_field = np.dot(weights[random_choice, :],  state_vector)
                
                # apply activation function to induced local field
                y = self.activation_function(local_field, state_vector, random_choice)
                
                # update element of state vector
                state_vector[random_choice] = y
                
                # increment sample index
                sample_index += 1
        
        return state_vector
    
    def flip_pixels(self, memorized_pattern, num_pixel_flip, num_units):
        """Flip the pixels of a memorized pattern."""
        # extract pixel flip indices
        flip_indices = np.random.choice(num_units, num_pixel_flip, replace=False)
        # generate an N-by-1 vector of all ones, where N is number of units
        flip_pattern = np.ones(num_units).reshape(-1, 1)
        # flip pixels at specified indices
        flip_pattern[flip_indices] = flip_pattern[flip_indices] * -1
        # flip pixels of memorized pattern to generate noisy pattern
        noisy_pattern = memorized_pattern * flip_pattern
        
        return noisy_pattern
        
    def recall_error(self, memorized_pattern, recall_pattern):
        """Test recall error using squared error."""
        # compute error
        error = memorized_pattern - recall_pattern
        # compute squared error
        squared_error = np.dot(error.T, error)
        
        return squared_error
    
    def noisy_recall(self, num_pixel_flip=10):
        """Perform noisy recall."""

        # generate noisy inputs using memorized patterns
        noisy_pattern_a = self.flip_pixels(memorized_pattern_a, num_pixel_flip, num_units)
        noisy_pattern_b = self.flip_pixels(memorized_pattern_b, num_pixel_flip, num_units)
        noisy_pattern_c = self.flip_pixels(memorized_pattern_c, num_pixel_flip, num_units)

        # recall noisy version of memorized patterns (retrieval phase)
        recall_pattern_a = self.recall_phase(noisy_pattern_a, weights, num_units)
        recall_pattern_b = self.recall_phase(noisy_pattern_b, weights, num_units)
        recall_pattern_c = self.recall_phase(noisy_pattern_c, weights, num_units)

        # compute recall error (based on squared error)
        recall_error_a = self.recall_error(memorized_pattern_a, recall_pattern_a)
        recall_error_b = self.recall_error(memorized_pattern_b, recall_pattern_b)
        recall_error_c = self.recall_error(memorized_pattern_c, recall_pattern_c)

        print('recall error on pattern a: {}'.format(recall_error_a))
        print('recall error on pattern b: {}'.format(recall_error_b))
        print('recall error on pattern c: {}'.format(recall_error_c))
        
        return noisy_pattern_a, noisy_pattern_b, noisy_pattern_c, recall_pattern_a, recall_pattern_b, recall_pattern_c
    
    def recall_performance(self, num_units):
        """Compute recall performance for different levels of pixel flip."""
        # empty list for storing recall performance
        recall_performance = []
        # generate number of pixel flip sequence
        num_pixel_flip_sequence = np.arange(0, num_units//2 + 1, 3)

        for num_pixel_flip in num_pixel_flip_sequence:
            # empty list for storing mean squared error performance
            mean_squared_error_performance = []
            for repetition_index in range(self.num_repetitions):
                
                # generate noisy inputs using memorized patterns
                noisy_pattern_a = self.flip_pixels(memorized_pattern_a, num_pixel_flip, num_units)
                noisy_pattern_b = self.flip_pixels(memorized_pattern_b, num_pixel_flip, num_units)
                noisy_pattern_c = self.flip_pixels(memorized_pattern_c, num_pixel_flip, num_units)
                
                # recall noisy version of memorized patterns (retrieval phase)
                recall_pattern_a = self.recall_phase(noisy_pattern_a, weights, num_units)
                recall_pattern_b = self.recall_phase(noisy_pattern_b, weights, num_units)
                recall_pattern_c = self.recall_phase(noisy_pattern_c, weights, num_units)
                
                # compute recall error (based on squared error)
                recall_error_a = self.recall_error(memorized_pattern_a, recall_pattern_a)
                recall_error_b = self.recall_error(memorized_pattern_b, recall_pattern_b)
                recall_error_c = self.recall_error(memorized_pattern_c, recall_pattern_c)
                
                # specify squared error less than 1
                squared_error_performance = np.double(np.hstack((recall_error_a, recall_error_b, recall_error_c)) < 1)
                
                # compute mean squared error
                mean_squared_error_performance.append(np.mean(squared_error_performance))
                
            # compute recall performance in percentage
            recall_performance.append(np.mean(mean_squared_error_performance) * 100)
    
        # convert number of pixel flip to percentage of pixel flip
        pixel_flip_percentage = num_pixel_flip_sequence / num_units * 100

        return pixel_flip_percentage, recall_performance
    
    def plot_noisy_recall(self, memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, noisy_pattern_a, noisy_pattern_b, noisy_pattern_c, recall_pattern_a, recall_pattern_b, recall_pattern_c):
        vmin, vmax = -1, 1
        fig, ax = plt.subplots(num_memorized_patterns, 3)
        # memorized pattern 'a'
        ax[0, 0].imshow(memorized_pattern_a.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[0, 0].set_xticks([])
        ax[0, 0].set_yticks([])
        ax[0, 0].set_title('memorized')
        # presented pattern 'a'
        ax[0, 1].imshow(noisy_pattern_a.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[0, 1].set_xticks([])
        ax[0, 1].set_yticks([])
        ax[0, 1].set_title('presented')
        # retrieved pattern 'a'
        ax[0, 2].imshow(recall_pattern_a.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[0, 2].set_xticks([])
        ax[0, 2].set_yticks([])
        ax[0, 2].set_title('retrieved')
        
        # memorized pattern 'b'
        ax[1, 0].imshow(memorized_pattern_b.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[1, 0].set_xticks([])
        ax[1, 0].set_yticks([])
        ax[1, 0].set_title('memorized')
        # presented pattern 'b'
        ax[1, 1].imshow(noisy_pattern_b.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[1, 1].set_xticks([])
        ax[1, 1].set_yticks([])
        ax[1, 1].set_title('presented')
        # retrieved pattern 'b'
        ax[1, 2].imshow(recall_pattern_b.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[1, 2].set_xticks([])
        ax[1, 2].set_yticks([])
        ax[1, 2].set_title('retrieved')
        
        # memorized pattern 'c'
        ax[2, 0].imshow(memorized_pattern_c.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[2, 0].set_xticks([])
        ax[2, 0].set_yticks([])
        ax[2, 0].set_title('memorized')
        # presented pattern 'c'
        ax[2, 1].imshow(noisy_pattern_c.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[2, 1].set_xticks([])
        ax[2, 1].set_yticks([])
        ax[2, 1].set_title('presented')
        # retrieved pattern 'c'
        ax[2, 2].imshow(recall_pattern_c.reshape(7, 7), cmap='Greys', vmin=vmin, vmax=vmax)
        ax[2, 2].set_xticks([])
        ax[2, 2].set_yticks([])
        ax[2, 2].set_title('retrieved')
        fig.tight_layout()
        fig.savefig(os.path.join(os.getcwd(), 'figure_1'))
        
    def plot_recall_performance(self, pixel_flip_percentage, recall_performance):
        fig, ax = plt.subplots()
        ax.plot(pixel_flip_percentage, recall_performance, color='k')
        ax.set_ylabel('recall performance in %')
        ax.set_xlabel('% of pixels flipped')
        ax.set_title('simulation')
        ax.set_ylim(0, 101)
        ax.set_xlim(0, 50)
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(os.path.join(os.getcwd(), 'figure_2'))
        
#%%
cwd = os.getcwd()                                                               # get current working directory
fileName = 'images'                                                             # specify filename

# filepath and directory specifications
if os.path.exists(os.path.join(cwd, fileName)) == False:                        # if path does not exist
    os.makedirs(fileName)                                                       # create directory with specified filename
    os.chdir(os.path.join(cwd, fileName))                                       # change cwd to the given path
    cwd = os.getcwd()                                                           # get current working directory
else:
    os.chdir(os.path.join(cwd, fileName))                                       # change cwd to the given path
    cwd = os.getcwd()                                                           # get current working directory

#%% instantiate Hopfield class
model = Hopfield()

#%% generate input patterns
memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, num_units, num_memorized_patterns = model.make_inputs()

#%% store weights
weights = model.storage_phase(memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, num_units, num_memorized_patterns)

#%% compute memorized pattern, presented pattern and retrieved pattern
noisy_pattern_a, noisy_pattern_b, noisy_pattern_c, recall_pattern_a, recall_pattern_b, recall_pattern_c = model.noisy_recall(num_pixel_flip=10)

#%% plot memorized pattern, presented pattern and retrieved pattern
model.plot_noisy_recall(memorized_pattern_a, memorized_pattern_b, memorized_pattern_c, noisy_pattern_a, noisy_pattern_b, noisy_pattern_c, recall_pattern_a, recall_pattern_b, recall_pattern_c)

#%% compute recall performance vs percentage of pixel flip noise
pixel_flip_percentage, recall_performance = model.recall_performance(num_units)

#%% plot recall performance vs percentage of pixel flip noise
model.plot_recall_performance(pixel_flip_percentage, recall_performance)
