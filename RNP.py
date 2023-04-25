# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18paMqS_nmi6vDBDw_zojoph1gOIyz2Wz
"""

# Commented out IPython magic to ensure Python compatibility.
import tensorflow_datasets as tfds
import tensorflow as tf
import os

#Extención a Tensor Board
# %load_ext tensorboard

#Versión de Tensorflow actual
print(tf.__version__)

#Descarga de los datasets
datasets, info = tfds.load(name='mnist', with_info=True, as_supervised=True)

#Separando datos de entrenamiento y prueba
mnist_train, mnist_test = datasets['train'], datasets['test']

#Estrataegia de distribución de los datos
strategy = tf.distribute.MirroredStrategy()

#Número de dispositivos
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

#Configurar la canalización de entrada

num_train_examples = info.splits['train'].num_examples
num_test_examples = info.splits['test'].num_examples

BUFFER_SIZE = 10000

BATCH_SIZE_PER_REPLICA = 64
BATCH_SIZE = BATCH_SIZE_PER_REPLICA * strategy.num_replicas_in_sync

#Normalizando las imágenes
def scale(image, label):
  image = tf.cast(image, tf.float32)
  image /= 255

  return image, label

#Mezclar los datos de entrenamiento y procesarlos por lotes
train_dataset = mnist_train.map(scale).cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE)
eval_dataset = mnist_test.map(scale).batch(BATCH_SIZE)

#Creación del modelo
with strategy.scope():
  model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(28, 28, 1)),
      tf.keras.layers.MaxPooling2D(),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.Dense(10)
  ])

  model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                optimizer=tf.keras.optimizers.Adam(),
                metrics=['accuracy'])

#Definir el directorio de puntos de control para almacenar los puntos de control.
checkpoint_dir = './training_checkpoints'
#Defina el nombre de los archivos de punto de control.
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

#Defina una función para disminuir la tasa de aprendizaje.
def decay(epoch):
  if epoch < 3:
    return 1e-3
  elif epoch >= 3 and epoch < 7:
    return 1e-4
  else:
    return 1e-5

#Defina una devolución de llamada para imprimir la tasa de aprendizaje al final de cada época.
class PrintLR(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs=None):
    print('\nLearning rate for epoch {} is {}'.format(epoch + 1,
                                                      model.optimizer.lr.numpy()))

#Junta todas las devoluciones de llamada.
callbacks = [
    tf.keras.callbacks.TensorBoard(log_dir='./logs'),
    tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix,
                                       save_weights_only=True),
    tf.keras.callbacks.LearningRateScheduler(decay),
    PrintLR()
]

#Entrenamiento del modelo

#Número de vueltas
EPOCHS = 12

model.fit(train_dataset, epochs=EPOCHS, callbacks=callbacks)

#Verifique el directorio de puntos de control.
ls: {checkpoint_dir}

#Para verificar qué tan bien funciona el modelo, cargue el último punto de control y llame a Model.evaluate en los datos de prueba
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

eval_loss, eval_acc = model.evaluate(eval_dataset)

print('Eval loss: {}, Eval accuracy: {}'.format(eval_loss, eval_acc))

# Commented out IPython magic to ensure Python compatibility.
#Para visualizar los datos anteriores
# %tensorboard --logdir=logs

ls -sh ./logs

#Guardando el modelo para exportar
path = 'saved_model/'

model.save(path, save_format='tf')

#cargar el modelo sin Strategy.scope
unreplicated_model = tf.keras.models.load_model(path)

unreplicated_model.compile(
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer=tf.keras.optimizers.Adam(),
    metrics=['accuracy'])

eval_loss, eval_acc = unreplicated_model.evaluate(eval_dataset)

print('Eval loss: {}, Eval Accuracy: {}'.format(eval_loss, eval_acc))

#Cargue el modelo con Strategy.scope
with strategy.scope():
  replicated_model = tf.keras.models.load_model(path)
  replicated_model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                           optimizer=tf.keras.optimizers.Adam(),
                           metrics=['accuracy'])

  eval_loss, eval_acc = replicated_model.evaluate(eval_dataset)
  print ('Eval loss: {}, Eval Accuracy: {}'.format(eval_loss, eval_acc))

#Exportar el modelo al explorador
model.save('numeros_conv_ad_do.h5')

#Convertirlo a tensorflow.js
!pip install tensorflowjs

!mkdir carpeta_salida

!tensorflowjs_converter --input_format keras numeros_conv_ad_do.h5 carpeta_salida