import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QFrame, QVBoxLayout , QSlider ,QComboBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.controller import Controller
from classes.CustomSignal import CustomSignal
from classes.frequencyViewer import FrequencyViewer
from classes.spectrogram import Spectrogram
from scipy.io import wavfile
import numpy as np
import sounddevice as sd
from classes.modesEnum import Mode

compile_qrc()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Equalizer')
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))
        self.isSpectrogramDisplayed = True

        self.showIcon = QIcon('icons_setup\icons\show.png')
        self.hideIcon = QIcon('icons_setup\icons\hide.png')

        self.spectrogramsFrame = self.findChild(QFrame, 'spectrogramsFrame')
        self.spectrogramDisplayButton = self.findChild(QPushButton, 'spectrogramDisplayButton')
        self.spectrogramDisplayButton.clicked.connect(self.toggleSpectrogramDisplay)
        self.current_signal = None
        
        self.isSpectrogramDisplayed = True

        self.showIcon = QIcon('icons_setup\icons\show.png')
        self.hideIcon = QIcon('icons_setup\icons\hide.png')
        
        ## browsing signal button
        self.browse_button = self.findChild(QPushButton, 'browseButton')
        self.browse_button.clicked.connect(self.upload_signal)
        
        ## initializing the viewers
        self.frequency_viewer = FrequencyViewer(scale="Linear")
        self.frequency_viewer.setBackground((30, 41, 59))
        self.frequency_viewer.getAxis('bottom').setPen('w')
        self.frequency_viewer.getAxis('left').setPen('w') 
        
        self.old_signal_spectrogram = Spectrogram(id = 1)
        self.old_signal_spectrogram.setBackground((30, 41, 59))
        self.old_signal_spectrogram.getAxis('bottom').setPen('w')
        self.old_signal_spectrogram.getAxis('left').setPen('w') 
        
        self.new_signal_spectrogram = Spectrogram(id = 2)
        self.new_signal_spectrogram.setBackground((30, 41, 59))
        self.new_signal_spectrogram.getAxis('bottom').setPen('w')
        self.new_signal_spectrogram.getAxis('left').setPen('w') 
        
        
        ## adding the frequency viwer 
        self.frequency_frame = self.findChild(QFrame, 'frequencyFrame')
        self.frequency_frame_layout = QVBoxLayout()
        self.frequency_frame.setLayout(self.frequency_frame_layout)
        self.frequency_frame_layout.addWidget(self.frequency_viewer)
        
        self.old_spectrogram_frame = self.findChild(QFrame, 'spectrogramGraph1Frame')
        self.old_spectrogram_frame_layout = QVBoxLayout()
        self.old_spectrogram_frame.setLayout(self.old_spectrogram_frame_layout)
        self.old_spectrogram_frame_layout.addWidget(self.old_signal_spectrogram)
        
        self.new_spectrogram_frame = self.findChild(QFrame, 'spectrogramGraph2Frame')
        self.new_spectrogram_frame_layout = QVBoxLayout()
        self.new_spectrogram_frame.setLayout(self.new_spectrogram_frame_layout)
        self.new_spectrogram_frame_layout.addWidget(self.new_signal_spectrogram)
        

        self.controller = Controller(frequency_viewer=self.frequency_viewer, old_signal_spectrogram=self.old_signal_spectrogram, new_signal_spectrogram=self.new_signal_spectrogram)
        
        #Initializing Animals Mode Sliders adn dictionary
        
        self.slider_values_map = [0 , 0, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
        self.all_freq_ranges = dict()
        self.all_freq_ranges['dolphin'] = [(10,300) , (1000,1700) , (1800,3400)]
        self.all_freq_ranges['eagle'] = [(2400,4500)] 
        self.all_freq_ranges['owl'] = [(300,600)] 
        self.all_freq_ranges['mouse'] = [(6000,16000)]
        
        # self.music_freq_ranges = dict()
        self.all_freq_ranges['piano'] = [(0,10), (250, 275), (505, 540), (780, 790),(1040, 1060), (1565, 1590), (1840, 1850),(2105, 2120), (2375, 2395), (2650, 2665), (2925, 2940), (3200, 3215), (3487,3491), (3770, 3780), (4345, 4355), (4638, 4656), (4900, 4980)]
        self.all_freq_ranges['violin'] = [(1020, 1060), (1520, 1600), (2560, 2640), (3080, 3180), (3590, 3720),(4110,4230),(4640,4650), (5140,5345)]
        self.all_freq_ranges['triangle'] = [(4600, 5000), (5170, 5250), (5350, 5550), (5600,22000)]
        self.all_freq_ranges['xilaphone'] = [(300,1000)]
        
        
        self.dolphin_sound_level_slider = self.findChild(QSlider , "verticalSlider_19")
        self.dolphin_sound_level_slider.setMaximum(9)
        self.dolphin_sound_level_slider.setMinimum(1)
        self.dolphin_sound_level_slider.setPageStep(1)
        self.dolphin_sound_level_slider.setValue(5)
        self.dolphin_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'dolphin'))
        
        self.eagle_sound_level_slider = self.findChild(QSlider , "verticalSlider_20")
        self.eagle_sound_level_slider.setMaximum(9)
        self.eagle_sound_level_slider.setMinimum(1)
        self.eagle_sound_level_slider.setPageStep(1)
        self.eagle_sound_level_slider.setValue(5)
        self.eagle_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'eagle'))
        
        self.owl_sound_level_slider = self.findChild(QSlider , "verticalSlider_21")
        self.owl_sound_level_slider.setMaximum(9)
        self.owl_sound_level_slider.setMinimum(1)
        self.owl_sound_level_slider.setPageStep(1)
        self.owl_sound_level_slider.setValue(5)
        self.owl_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'owl'))
        
        self.mouse_sound_level_slider = self.findChild(QSlider , "verticalSlider_22")
        self.mouse_sound_level_slider.setMaximum(9)
        self.mouse_sound_level_slider.setMinimum(1)
        self.mouse_sound_level_slider.setPageStep(1)        
        self.mouse_sound_level_slider.setValue(5)
        self.mouse_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'mouse'))
        
        # Initializing play button for sound before and after modification
        self.after_modifiy_play_sound_button = self.findChild(QPushButton , "soundAfterButton")
        self.after_modifiy_play_sound_button.pressed.connect(self.play_sound_after_modify)
        
        self.before_modifiy_play_sound_button = self.findChild(QPushButton , "soundBeforeButton")
        self.before_modifiy_play_sound_button.pressed.connect(self.play_sound_before_modify)
        
        # Initialize Selected Mode ComboBox
        self.selected_mode_combo_box = self.findChild(QComboBox  ,"modeComboBox")
        self.selected_mode_combo_box.currentIndexChanged.connect(self.changed_mode_effect)
    
        # Initialize scale type in frequency viewer
        self.frequency_viewer_scale = self.findChild(QComboBox , "comboBox")
        self.frequency_viewer_scale.currentIndexChanged.connect(self.changed_frequency_viewer_scale_effect)
        
    def upload_signal(self):
        '''
        handles loading the signal
        '''
        file_path, _ = QFileDialog.getOpenFileName(self,'Open File','', 'CSV Files (*.csv);;WAV Files (*.wav);;MP3 Files (*.mp3);;All Files (*)')
        if file_path.endswith('.csv'):
            pass
        elif file_path.endswith('.wav'):
            sample_rate, data_y = wavfile.read(file_path)
            data_x = np.linspace(0, len(data_y)/sample_rate, len(data_y))
            new_signal = CustomSignal(data_x, data_y , linear_frequency=[[], []])
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            print(sample_rate)
        elif file_path.endswith('.mp3'):
            pass

        else:
            self.show_error("the file extention must be a csv file")

    def toggleSpectrogramDisplay(self):
        if self.isSpectrogramDisplayed:
            self.spectrogramsFrame.hide()
            self.spectrogramDisplayButton.setIcon(self.showIcon)
        else:
            self.spectrogramsFrame.show()
            self.spectrogramDisplayButton.setIcon(self.hideIcon)
        self.isSpectrogramDisplayed = not self.isSpectrogramDisplayed
        
    def sound_level_slider_effect(self, slider_value, name):
        self.controller.equalizer.equalize( self.all_freq_ranges[name], factor = self.slider_values_map[slider_value])
        self.controller.set_current_signal(self.current_signal)
    
    # def animal_sound_level_slider_effect(self, slider_value, animal_name):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges[animal_name], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    

    # def dolphin_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['dolphin'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    
    # def eagle_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['eagle'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)

    # def mouse_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['mouse'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    
    # def owl_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['owl'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)


    
    def play_sound_before_modify(self):
        sd.play(self.current_signal.original_signal[1] , self.current_signal.signal_sampling_rate)
        sd.wait()
    
    def play_sound_after_modify(self):
        self.controller.equalizer.inverse()
        normalized_result_sound = self.current_signal.reconstructed_signal[1] / np.max(np.abs(self.current_signal.reconstructed_signal[1]))
        sd.play(normalized_result_sound , self.current_signal.signal_sampling_rate)
        sd.wait()

    def changed_mode_effect(self):
        self.controller.mode = self.selected_mode_combo_box.currentText()
    
    def changed_frequency_viewer_scale_effect(self):
        self.controller.frequency_viewer.view_scale = self.frequency_viewer_scale.currentText()
        self.controller.set_current_signal(self.current_signal)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())