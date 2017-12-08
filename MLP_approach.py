import numpy as np
import tensorflow as tf

#%%

# Data
from Preprocessor import Preprocessor

# Create an object of Preprocessor class and use its method
pp = Preprocessor()
X_train = pp.preprocess_input_file('HS_D08.wav')
y_train = pp.preprocess_output_file('HS_D08_Spk1.csv')


#Match numpy array shapes of X_train and Y_train
if X_train.shape[0] != y_train.shape[0]:
    y_train = y_train[0:X_train.shape[0],:]

X_train = X_train[0:1000,:]
y_train = y_train[0:1000,:]

print ("X_train.shape = ", X_train.shape, "y_train.shape = ", y_train.shape)

def reset_graph(seed=42):
    tf.reset_default_graph()
    tf.set_random_seed(seed)
    np.random.seed(seed)

#%%

# Using plain tensor flow
n_inputs = X_train.shape[1]
n_hidden1 = 300
n_hidden2 = 100
n_outputs = 1

reset_graph()

X = tf.placeholder(tf.float32, shape=(None, n_inputs), name="X")
y = tf.placeholder(tf.float32, shape=(None), name="y")

def neuron_layer(X, n_neurons, name, activation=None):
    with tf.name_scope(name):
        n_inputs = int(X.get_shape()[1])
        stddev = 2 / np.sqrt(n_inputs)
        init = tf.truncated_normal((n_inputs, n_neurons), stddev=stddev)
        # random stuff to initialize the neuron
        W = tf.Variable(init, name="kernel")
        b = tf.Variable(tf.zeros([n_neurons]), name="bias")
        Z = tf.matmul(X, W) + b
        if activation is not None:
            return activation(Z)
        else:
            return Z

# Create the neuron layers
with tf.name_scope("dnn"):
    hidden1 = neuron_layer(X, n_hidden1, name="hidden1",
                           activation=tf.nn.relu)
    hidden2 = neuron_layer(hidden1, n_hidden2, name="hidden2",
                           activation=tf.nn.relu)
    y_pred = neuron_layer(hidden2, n_outputs, name="outputs", activation=tf.nn.sigmoid)

with tf.name_scope("mse"):
    error = y_pred - y
    mse = tf.reduce_mean(tf.square(error), name="mse")

learning_rate = 0.01

with tf.name_scope("train"):
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    training_op = optimizer.minimize(mse)

init = tf.global_variables_initializer()
saver = tf.train.Saver()

n_epochs = 6000
batch_size = 100
n_batches = int(np.ceil(X_train.shape[0] / batch_size))

with tf.Session() as sess:
    init.run()
    for epoch in range(n_epochs):
        for b in range(0, X_train.shape[0], batch_size):
            X_batch , y_batch = X_train[b:b+batch_size], y_train[b:b+batch_size]
            sess.run(training_op, feed_dict={X: X_batch, y:y_batch})
        if epoch % 100 == 0:
            c = sess.run(mse, feed_dict={X: X_batch, y:y_batch})
            print(epoch, "Train error mse:", c)
    save_path = saver.save(sess, "./my_model_final.ckpt")

print("Training done...")

