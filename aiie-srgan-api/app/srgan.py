from tensorlayerx.nn import Module
import tensorlayerx as tlx
from tensorlayerx.nn import Conv2d, BatchNorm2d, SubpixelConv2d, Sequential

W_init = tlx.initializers.TruncatedNormal(stddev=0.02)
G_init = tlx.initializers.TruncatedNormal(mean=1.0, stddev=0.02)


class ResidualBlock(Module):
    def __init__(self):
        super(ResidualBlock, self).__init__()
        self.conv1 = Conv2d(
            out_channels=64,
            kernel_size=(3, 3),
            stride=(1, 1),
            act=None,
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
            b_init=None,
        )
        self.bn1 = BatchNorm2d(
            num_features=64,
            act=tlx.ReLU,
            gamma_init=G_init,
            data_format="channels_last",
        )
        self.conv2 = Conv2d(
            out_channels=64,
            kernel_size=(3, 3),
            stride=(1, 1),
            act=None,
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
            b_init=None,
        )
        self.bn2 = BatchNorm2d(
            num_features=64, act=None, gamma_init=G_init, data_format="channels_last"
        )

    def forward(self, x):
        z = self.conv1(x)
        z = self.bn1(z)
        z = self.conv2(z)
        z = self.bn2(z)
        x = x + z
        return x


class SRGAN_g(Module):
    """Generator in Photo-Realistic Single Image Super-Resolution Using a Generative Adversarial Network
    feature maps (n) and stride (s) feature maps (n) and stride (s)
    """

    def __init__(self):
        super(SRGAN_g, self).__init__()
        self.conv1 = Conv2d(
            out_channels=64,
            kernel_size=(3, 3),
            stride=(1, 1),
            act=tlx.ReLU,
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
        )
        self.residual_block = self.make_layer()
        self.conv2 = Conv2d(
            out_channels=64,
            kernel_size=(3, 3),
            stride=(1, 1),
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
            b_init=None,
        )
        self.bn1 = BatchNorm2d(
            num_features=64,
            act=None,
            gamma_init=G_init,
            data_format="channels_last",
        )
        self.conv3 = Conv2d(
            out_channels=256,
            kernel_size=(3, 3),
            stride=(1, 1),
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
        )
        self.subpiexlconv1 = SubpixelConv2d(
            data_format="channels_last", scale=2, act=tlx.ReLU
        )
        self.conv4 = Conv2d(
            out_channels=256,
            kernel_size=(3, 3),
            stride=(1, 1),
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
        )
        self.subpiexlconv2 = SubpixelConv2d(
            data_format="channels_last", scale=2, act=tlx.ReLU
        )
        self.conv5 = Conv2d(
            3,
            kernel_size=(1, 1),
            stride=(1, 1),
            act=tlx.Tanh,
            padding="SAME",
            W_init=W_init,
            data_format="channels_last",
        )

    def make_layer(self):
        layer_list = []
        for i in range(16):
            layer_list.append(ResidualBlock())
        return Sequential(layer_list)

    def forward(self, x):
        x = self.conv1(x)
        temp = x
        x = self.residual_block(x)
        x = self.conv2(x)
        x = self.bn1(x)
        x = x + temp
        x = self.conv3(x)
        x = self.subpiexlconv1(x)
        x = self.conv4(x)
        x = self.subpiexlconv2(x)
        x = self.conv5(x)

        return x
