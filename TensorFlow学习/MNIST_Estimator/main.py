#-*- coding:utf-8 _*-  
""" 
@author:KING 
@file: main.py 
@time: 2018/08/07 
"""

from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

#Parameters
learning_rate = 0.001
num_steps = 2000
batch_size = 128

num_input = 784
num_classes = 10
dropout = 0.5
mnist = input_data.read_data_sets("MNIST_data/", one_hot=False)

def conv_net(x_dict,n_classes,dropout,reuse,is_training):
    with tf.variable_scope('ConvNet',reuse=reuse):
        x = x_dict['images']
        #数量，高，宽，通道数
        x = tf.reshape(x,shape=[-1,28,28,1])
        conv1 = tf.layers.conv2d(x,32,5,activation=tf.nn.relu)
        conv1 = tf.layers.max_pooling2d(conv1,2,2)

        conv2 = tf.layers.conv2d(conv1, 64, 5, activation=tf.nn.relu)
        conv2 = tf.layers.max_pooling2d(conv2, 2, 2)

        fc1 = tf.contrib.layers.flatten(conv2)
        fc1 = tf.layers.dense(fc1,1024)
        fc1 = tf.layers.dropout(fc1,rate=dropout,training=is_training)
        out = tf.layers.dense(fc1,n_classes)
    return out

def model_fn(features,labels,mode):
    logits_train = conv_net(features,num_classes,dropout,reuse=False,is_training=True)
    logits_test = conv_net(features,num_classes,dropout,reuse=True,is_training=False)
    pred_classes = tf.argmax(logits_test,axis=1)
    pred_probas = tf.nn.softmax(logits_test)

    if mode==tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode,predictions=pred_classes)
    #将labels稀疏化
    loss_op = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits_train,
                                                                            labels=tf.cast(labels, dtype=tf.int32)))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op,global_step=tf.train.get_global_step())
    acc_op = tf.metrics.accuracy(labels=labels,predictions=pred_classes)
    estim_spec = tf.estimator.EstimatorSpec(mode=mode,predictions=pred_classes,
                                            loss=loss_op,train_op=train_op,
                                            eval_metric_ops={'accuracy':acc_op})
    return estim_spec



def train():
    model = tf.estimator.Estimator(model_fn)
    input_fn = tf.estimator.inputs.numpy_input_fn(x={'images':mnist.train.images},
                                                  y=mnist.train.labels,
                                                  batch_size=batch_size,num_epochs=None,shuffle=True)
    model.train(input_fn,steps=num_steps)
    return model


def evaluate(model):
    input_fn = tf.estimator.inputs.numpy_input_fn(
            x={'images': mnist.test.images}, y=mnist.test.labels,
            batch_size=batch_size, shuffle=False)
    model.evaluate(input_fn)

def test(model):
    # 预测单个图像
    n_images = 4
    # 从数据集得到测试图像
    test_images = mnist.test.images[:n_images]
    # 准备输入数据
    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'images': test_images}, shuffle=False)
    # 用训练好的模型预测图片类别
    preds = list(model.predict(input_fn))

    # 可视化显示
    for i in range(n_images):
        plt.imshow(np.reshape(test_images[i], [28, 28]), cmap='gray')
        plt.show()
        print("Model prediction:", preds[i])

if __name__ == '__main__':
    model = train()