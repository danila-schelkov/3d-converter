from .gltf_property import GlTFProperty


class Animation(GlTFProperty):
    class AnimationSampler(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.input = None
            self.output = None

            self.interpolation = None  # Default: 'LINEAR'

    class Channel(GlTFProperty):
        class Target(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.path = None

                self.node = None

        def __init__(self):
            super().__init__()
            self.sampler = None
            self.target = self.Target()

    def __init__(self):
        super().__init__()
        self.channels = self.Channel()
        self.samplers = self.AnimationSampler()

        self.name = None

