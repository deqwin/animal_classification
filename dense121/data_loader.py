#encoding=utf-8

import tensorflow as tf

import cv2
import numpy as np
from keras import backend as K
from keras.utils import np_utils

from PIL import Image

# 读取 tfrecords 数据
def read_and_decode(filename):
  # 读入流中
  filename_queue = tf.train.string_input_producer([filename])

  # 创建 reader，从文件队列中读入一个序列化的样本
  reader = tf.TFRecordReader()
  _, serialized_example = reader.read(filename_queue)
  # get feature from serialized example
  # 解析符号化的样本
  features = tf.parse_single_example(
    serialized_example,
    features={
      'label': tf.FixedLenFeature([], tf.int64),
      'img_raw': tf.FixedLenFeature([], tf.string)
    }
  )
  
  img = features['img_raw']
  img = tf.decode_raw(img, tf.uint8)
  img = tf.reshape(img, [224, 224, 3])
  #img = tf.cast(img, tf.float32) * (1. / 255) - 0.5
  label = tf.cast(features['label'], tf.int32)

  return img, label


def load_data(img_rows=224, img_cols=224):
  Train_img, Train_label = read_and_decode("../resources/tfrecordsResult/train.tfrecords")
  Test_img, Test_label = read_and_decode("../resources/tfrecordsResult/test.tfrecords")
  #Train_img, Train_label = read_and_decode("OriginalData/Animals_50class_UseSMOTE/tfrecordsResult/train.tfrecords")
  #Test_img, Test_label = read_and_decode("OriginalData/Animals_50class_UseSMOTE/tfrecordsResult/test.tfrecords")
  #Train_img, Train_label = read_and_decode("OriginalData/Dog_120class_UseSmote/tfrecordsResult/train.tfrecords")
  #Test_img, Test_label = read_and_decode("OriginalData/Dog_120class_UseSmote/tfrecordsResult/test.tfrecords")

  Train_img_batch, Train_label_batch = \
    tf.train.shuffle_batch([Train_img, Train_label], batch_size=24000, capacity=4000, min_after_dequeue=2000)

  with tf.Session() as sess_train:
    sess_train.run(tf.global_variables_initializer())
    threads_train = tf.train.start_queue_runners(sess=sess_train)
    Train_val, Train_lab = sess_train.run([Train_img_batch, Train_label_batch])
    sess_train.close()


  Test_img_batch, Test_label_batch = \
    tf.train.shuffle_batch([Test_img, Test_label], batch_size=4800, capacity=2000, min_after_dequeue=1000)

  with tf.Session() as sess_test:
    sess_test.run(tf.global_variables_initializer())
    threads_test = tf.train.start_queue_runners(sess=sess_test)
    Test_val, Test_lab = sess_test.run([Test_img_batch, Test_label_batch])
    sess_test.close()


  nb_train_samples = 24000  # 14400 training samples
  nb_test_samples = 4800
  num_classes = 120

  Y_train = np_utils.to_categorical(Train_lab[:nb_train_samples], num_classes)
  Y_test = np_utils.to_categorical(Test_lab[:nb_test_samples], num_classes)


  if K.image_dim_ordering() == 'th':
    X_train = np.array([cv2.resize(img.transpose(1,2,0), (img_rows,img_cols)).transpose(2,0,1) for img in Train_val[:nb_train_samples,:,:,:]])
    X_test = np.array([cv2.resize(img.transpose(1,2,0), (img_rows,img_cols)).transpose(2,0,1) for img in Test_val[:nb_test_samples,:,:,:]])
  else:
    X_train = np.array([cv2.resize(img, (img_rows,img_cols)) for img in Train_val[:nb_train_samples,:,:,:]])
    X_test = np.array([cv2.resize(img, (img_rows, img_cols)) for img in Test_val[:nb_train_samples, :, :, :]])


  print(X_train.shape, Y_train.shape)
  print(X_test.shape, Y_test.shape)
  return X_train, Y_train, X_test, Y_test