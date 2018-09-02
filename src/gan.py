import numpy as np
from keras.models import Input, Model
from keras.optimizers import Adam


class GAN:
    def __init__(self, create_generator_func, create_discriminator_func,
                 input_dim=2, noise_dim=2):

        self.input_dim = input_dim
        self.noise_dim = noise_dim
        self.discriminator = create_discriminator_func(input_dim)
        self._compile_models()
        self.generator = create_generator_func(noise_dim)
        self.discriminator.trainable = False
        self.combined_model = self._create_combined_model()
        self._compile_combined_model()
        self.generator.summary()
        self.discriminator.summary()

    def train(self, X, epochs, batch_size):
        half_batch_size = int(batch_size / 2)
        batches_per_epoch = 2 * int(X.shape[0] / batch_size)
        for i in range(epochs):
            permutation = np.random.choice(np.arange(X.shape[0]), X.shape[0],
                                           replace=False)
            X = X[permutation]
            generator_losses, discriminator_losses = [], []
            generator_accs, discriminator_accs = [], []
            for j in range(batches_per_epoch):
                noise = np.random.normal(0, 1, (half_batch_size, self.noise_dim))
                x_fake_batch = self.generator.predict(noise)
                x_real_batch = X[j*half_batch_size: (j+1)*half_batch_size]
                x_batch = np.concatenate([x_fake_batch, x_real_batch],
                                         axis=0)
                y_batch = np.concatenate([np.zeros(half_batch_size),
                                          np.ones(half_batch_size)])
                d_loss = self.discriminator.train_on_batch(x_batch, y_batch)
                new_noise = np.random.normal(0, 1, (half_batch_size, self.noise_dim))

                g_loss = self.combined_model.train_on_batch(
                    np.concatenate([noise, new_noise]),
                    0.95 * np.ones(batch_size))
                generator_losses.append(g_loss[0])
                discriminator_losses.append(d_loss[0])
                generator_accs.append(g_loss[1])
                discriminator_accs.append(d_loss[1])
            print(np.mean(generator_losses), ",", np.mean(discriminator_losses),
                  end=", ", sep='')
            print(np.mean(generator_accs), ",", np.mean(discriminator_accs),
                  sep="")

    def _create_combined_model(self):
        noise = Input(shape=(self.noise_dim,))
        fake_img = self.generator(noise)
        outputs = self.discriminator(fake_img)
        return Model(noise, outputs)

    def _compile_models(self):
        self.discriminator.compile(loss="binary_crossentropy",
                                   optimizer=Adam(2e-4, beta_1=.5),
                                   metrics=["accuracy"])

    def _compile_combined_model(self):
        self.combined_model.compile(loss="binary_crossentropy",
                                    optimizer=Adam(2e-4, beta_1=.5),
                                    metrics=["accuracy"])

