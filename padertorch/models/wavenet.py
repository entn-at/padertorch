import torch

from padertorch.base import Model
from padertorch import modules
from padertorch.ops import mu_law_decode


class WaveNet(Model):
    def __init__(self, wavenet, sample_rate=16000, feature_key=0, audio_key=1):
        super().__init__()
        self.wavenet = wavenet
        self.sample_rate = sample_rate
        self.feature_key = feature_key
        self.audio_key = audio_key

    @classmethod
    def finalize_dogmatic_config(cls, config):
        config['wavenet']['factory'] = modules.WaveNet
        return config

    def forward(self, inputs):
        return self.wavenet(inputs[self.feature_key], inputs[self.audio_key])

    def review(self, inputs, outputs):
        predictions, targets = outputs
        ce = torch.nn.CrossEntropyLoss(reduction='none')(predictions, targets)
        summary = dict(
            loss=ce.mean(),
            scalars=dict(),
            histograms=dict(reconstruction_ce=ce),
            audios=dict(
                target=(inputs[self.audio_key][0], self.sample_rate),
                decode=(
                    mu_law_decode(
                        torch.argmax(outputs[0][0], dim=0),
                        mu_quantization=self.wavenet.n_out_channels),
                    self.sample_rate)
            ),
            images=dict()
        )
        return summary
