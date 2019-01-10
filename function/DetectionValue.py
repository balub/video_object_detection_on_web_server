class DetectionValue:
    def __init__(self):
        self.num_frames = 0
        self.display = 0
        self.output = 0
        self.output_path = "outputs/video.mp4"
        self.input_device = 0
        self.input_videos = "uploads/video.mp4"
        self.num_workers = 2
        self.queue_size = 5
        self.logger_debug = 0
        self.fullscreen = 0

    def get_num_frames(self):
        return self.num_frames

    def set_num_frames(self, num_frames):
        self.num_frames = num_frames

    def get_display(self):
        return self.display

    def set_display(self, display):
        self.display = display

    def get_output(self):
        return self.output

    def set_output(self, output):
        self.output = output

    def get_output_path(self):
        return self.output_path

    def set_output_path(self, output_path):
        self.output_path = output_path

    def get_input_device(self):
        return self.input_device

    def set_input_device(self, input_device):
        self.input_device = input_device

    def get_input_videos(self):
        return self.input_videos

    def set_input_videos(self, input_videos):
        self.input_videos = input_videos

    def get_num_workers(self):
        return self.num_workers

    def set_num_workers(self, num_workers):
        self.num_workers = num_workers

    def get_queue_size(self):
        return self.queue_size

    def set_queue_size(self, queue_size):
        self.queue_size = queue_size

    def get_logger_debug(self):
        return self.logger_debug

    def set_logger_debug(self, logger_debug):
        self.logger_debug = logger_debug

    def get_fullscreen(self):
        return self.fullscreen

    def set_fullscreen(self, fullscreen):
        self.fullscreen = fullscreen