# mnist + lenet + tensorflow
# -*- coding: utf-8 -*-
# @Time    : 2019/1/7 15:00
import subprocess
import tensorflow as tf
import numpy as np
import sys
from tensorflow.examples.tutorials.mnist import input_data
from sklearn.utils import shuffle
from tensorflow.contrib.layers import flatten

#################### 1.输出硬件和软件环境 ######################
def print_envs():
    print("-----------------------------硬件信息--------------------------------------------")
    try:
        cpu = subprocess.Popen('cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c ', 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        memory = subprocess.Popen('cat /proc/meminfo  ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        gpu = subprocess.Popen('nvidia-smi ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        linux = subprocess.Popen('head -n 1 /etc/issue',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        kernal = subprocess.Popen('uname -a  ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        memory = subprocess.Popen('cat /proc/meminfo  ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        cuda = subprocess.Popen('cat /usr/local/cuda/version.txt  ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cudnn = subprocess.Popen('cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2 ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        memory = subprocess.Popen('cat /proc/meminfo  ',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
        code      = e.returncode   # Return code

    print("CPU:", bytes.decode(cpu.stdout.readline()).strip())
    print("Memory:", bytes.decode(memory.stdout.readline()).strip())
    print("GPU:")
    for line in gpu.stdout.readlines():
        print(bytes.decode(line))
    print("Linux:", bytes.decode(linux.stdout.readline()).strip())
    print("Kernal:", bytes.decode(kernal.stdout.readline()).strip())
    print("\n\n----------------------------------环境信息-------------------------------")
    print("CUDA:", bytes.decode(cuda.stdout.readline()).strip())
    print("cuDNN:", bytes.decode(cudnn.stdout.readline()).strip())
    print("Tensorflow:", tf.__version__)
    print("Python:", sys.version)

print_envs()

###################  2. 加载数据   ##############################
# 不写这个会有warning
old_v = tf.logging.get_verbosity()
tf.logging.set_verbosity(tf.logging.ERROR)

mnist = input_data.read_data_sets("../mnist/", reshape=False)
X_train, y_train           = mnist.train.images, mnist.train.labels
X_validation, y_validation = mnist.validation.images, mnist.validation.labels
X_test, y_test             = mnist.test.images, mnist.test.labels

tf.logging.set_verbosity(old_v)

assert(len(X_train) == len(y_train))
assert(len(X_validation) == len(y_validation))
assert(len(X_test) == len(y_test))

print()
print("Image Shape: {}".format(X_train[0].shape))
print()
print("Training Set:   {} samples".format(len(X_train)))
print("Validation Set: {} samples".format(len(X_validation)))
print("Test Set:       {} samples".format(len(X_test)))



# Pad images with 0s
X_train      = np.pad(X_train, ((0,0),(2,2),(2,2),(0,0)), 'constant')
X_validation = np.pad(X_validation, ((0,0),(2,2),(2,2),(0,0)), 'constant')
X_test       = np.pad(X_test, ((0,0),(2,2),(2,2),(0,0)), 'constant')
    
print("Updated Image Shape: {}".format(X_train[0].shape))

# 数据预处理
X_train, y_train = shuffle(X_train, y_train)

################## 3. 神经网络部分 ############################
# 设置超参数
EPOCHS = 4
BATCH_SIZE = 128

def LeNet(x):    
    # Hyperparameters
    mu = 0
    sigma = 0.1
    layer_depth = {
        'layer_1' : 6,
        'layer_2' : 16,
        'layer_3' : 120,
        'layer_f1' : 84
    }

    
    # TODO: Layer 1: Convolutional. Input = 32x32x1. Output = 28x28x6.
    conv1_w = tf.Variable(tf.truncated_normal(shape = [5,5,1,6],mean = mu, stddev = sigma))
    conv1_b = tf.Variable(tf.zeros(6))
    conv1 = tf.nn.conv2d(x,conv1_w, strides = [1,1,1,1], padding = 'VALID') + conv1_b 
    # TODO: Activation.
    conv1 = tf.nn.relu(conv1)

    # TODO: Pooling. Input = 28x28x6. Output = 14x14x6.
    pool_1 = tf.nn.max_pool(conv1,ksize = [1,2,2,1], strides = [1,2,2,1], padding = 'VALID')
    
    # TODO: Layer 2: Convolutional. Output = 10x10x16.
    conv2_w = tf.Variable(tf.truncated_normal(shape = [5,5,6,16], mean = mu, stddev = sigma))
    conv2_b = tf.Variable(tf.zeros(16))
    conv2 = tf.nn.conv2d(pool_1, conv2_w, strides = [1,1,1,1], padding = 'VALID') + conv2_b
    # TODO: Activation.
    conv2 = tf.nn.relu(conv2)

    # TODO: Pooling. Input = 10x10x16. Output = 5x5x16.
    pool_2 = tf.nn.max_pool(conv2, ksize = [1,2,2,1], strides = [1,2,2,1], padding = 'VALID') 
    
    # TODO: Flatten. Input = 5x5x16. Output = 400.
    fc1 = flatten(pool_2)
    
    # TODO: Layer 3: Fully Connected. Input = 400. Output = 120.
    fc1_w = tf.Variable(tf.truncated_normal(shape = (400,120), mean = mu, stddev = sigma))
    fc1_b = tf.Variable(tf.zeros(120))
    fc1 = tf.matmul(fc1,fc1_w) + fc1_b
    
    # TODO: Activation.
    fc1 = tf.nn.relu(fc1)

    # TODO: Layer 4: Fully Connected. Input = 120. Output = 84.
    fc2_w = tf.Variable(tf.truncated_normal(shape = (120,84), mean = mu, stddev = sigma))
    fc2_b = tf.Variable(tf.zeros(84))
    fc2 = tf.matmul(fc1,fc2_w) + fc2_b
    # TODO: Activation.
    fc2 = tf.nn.relu(fc2)
    
    # TODO: Layer 5: Fully Connected. Input = 84. Output = 10.
    fc3_w = tf.Variable(tf.truncated_normal(shape = (84,10), mean = mu , stddev = sigma))
    fc3_b = tf.Variable(tf.zeros(10))
    logits = tf.matmul(fc2, fc3_w) + fc3_b
    return logits
x = tf.placeholder(tf.float32, (None, 32, 32, 1))
y = tf.placeholder(tf.int32, (None))
one_hot_y = tf.one_hot(y, 10)

##############  4. 训练定义 ###############################
rate = 0.001

logits = LeNet(x)
cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(logits = logits, labels=one_hot_y)
loss_operation = tf.reduce_mean(cross_entropy)
optimizer = tf.train.AdamOptimizer(learning_rate = rate)
training_operation = optimizer.minimize(loss_operation)
############ 5. 模型验证##################################
correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(one_hot_y, 1))
accuracy_operation = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
saver = tf.train.Saver()

def evaluate(X_data, y_data):
    num_examples = len(X_data)
    total_accuracy = 0
    sess = tf.get_default_session()
    for offset in range(0, num_examples, BATCH_SIZE):
        batch_x, batch_y = X_data[offset:offset+BATCH_SIZE], y_data[offset:offset+BATCH_SIZE]
        accuracy = sess.run(accuracy_operation, feed_dict={x: batch_x, y: batch_y})
        total_accuracy += (accuracy * len(batch_x))
    return total_accuracy / num_examples

############ 6.训练模型 #############################
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    num_examples = len(X_train)
    
    print("Training...")
    print()
    for i in range(EPOCHS):
        X_train, y_train = shuffle(X_train, y_train)
        for offset in range(0, num_examples, BATCH_SIZE):
            end = offset + BATCH_SIZE
            batch_x, batch_y = X_train[offset:end], y_train[offset:end]
            sess.run(training_operation, feed_dict={x: batch_x, y: batch_y})
            
        validation_accuracy = evaluate(X_validation, y_validation)
        print("EPOCH {} ...".format(i+1))
        print("Validation Accuracy = {:.3f}".format(validation_accuracy))
        print()
    
    checkpoint_name = "../output/lenet.ckpt"
    save_path = saver.save(sess, checkpoint_name)
    print("Model saved")

##############  7. 验证模型 ################### 
with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state('../output/')  # 注意此处是checkpoint存在的目录，千万不要写成‘./log’
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess,ckpt.model_checkpoint_path) # 自动恢复model_checkpoint_path保存模型一般是最新
        print("Model restored...")
    else:
        print('No Model')
#     saver.restore(sess, tf.train.latest_checkpoint('.'))

    test_accuracy = evaluate(X_test, y_test)
    print("Test Accuracy = {:.3f}".format(test_accuracy))
