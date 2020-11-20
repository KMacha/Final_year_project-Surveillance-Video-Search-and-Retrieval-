import application.featureprocessing.offlineprocessing.previewvideo as preview

#inherits the PreviewVideo that had been made for the offline processing
class PreviewVideo(preview.PreviewVideo):

    def __init__(self,root_window,video_cap,start_frame_time,end_frame_time):
        super().__init__(root_window=root_window,video_cap=video_cap,
                        start_frame_time=start_frame_time,end_frame_time=end_frame_time)
        
        self.preview()
