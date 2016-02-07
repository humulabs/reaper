import os
import urwid as uw
from urwid_timed_progress import TimedProgressBar

class App(object):

    palette = [
        ('normal',   'white', 'black', 'standout'),
        ('complete', 'white', 'dark magenta'),
    ]

    def __init__(self, reaper):
        self.reaper = reaper
        self.file_progress = TimedProgressBar('normal',
                                              'complete',
                                              label='Current File',
                                              label_width=13,
                                              units='Bytes')

        self.overall_progress = TimedProgressBar('normal',
                                                 'complete',
                                                 label='Overall',
                                                 label_width=13,
                                                 units='Bytes')

        self._status = uw.Text('-ready-')
        self.debug_message = uw.Text('')

        footer = uw.Text('r to run, ESC or q to exit')

        progress = uw.Frame(uw.ListBox([self.file_progress,
                                        uw.Divider(),
                                        self.overall_progress,
                                        uw.Divider(),
                                        uw.Divider(),
                                        self._status,
                                        uw.Divider(),
                                        self.debug_message,
                                        ]),
                            footer=footer)

        def keypress(key):
            if key in ('q', 'Q', 'esc'):
                raise uw.ExitMainLoop()
            elif key in ('r', 'R'):
                self.download()

        self.loop = uw.MainLoop(progress,
                                App.palette,
                                unhandled_input=keypress)
        self.loop.run()

    def status(self, msg):
        self._status.set_text(msg)
        self.loop.draw_screen()

    def download(self):
        self.status('listing files on SD card ...')
        files = self.reaper.ls()
        self.overall_progress.done = sum([f['size'] for f in files])
        self.status('starting download ...')
        for f in files:
            if f['size'] > 0:
                self.file_progress.reset()
                self.status('downloading {} ...'.format(f['name']))
                self.file_progress.done = f['size']
                self.loop.draw_screen()

                def progress_fun(num_bytes, _):
                    self.file_progress.add_progress(num_bytes)
                    self.overall_progress.add_progress(num_bytes)
                    self.loop.draw_screen()

                data_dir = 'data'

                sd_filename = f['name'].lstrip('/')
                local_filename = os.path.join(data_dir, sd_filename)
                dirname = os.path.dirname(local_filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                self.reaper.cp(sd_filename,
                               local_filename,
                               f['size'],
                               progress_fun)

    def debug(self, m):
        self.debug_message.set_text(m)
        self.loop.draw_screen()

