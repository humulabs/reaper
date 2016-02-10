import os
import urwid as uw
from urwid_timed_progress import TimedProgressBar

class App(object):

    palette = [
        ('normal',   'white', 'black', 'standout'),
        ('complete', 'white', 'dark magenta'),
        ('footer',   'white', 'dark gray'),
    ]

    # Using SI units: https://en.wikipedia.org/wiki/Kilobyte
    units = [
        ('B', 1),
        ('kB', 1000),
        ('MB', 1000000),
        ('GB', 1000000000),
    ]

    def __init__(self, reaper):
        self.reaper = reaper
        self.file_progress = TimedProgressBar('normal',
                                              'complete',
                                              label='Current File',
                                              label_width=13,
                                              units=App.units,
                                              done=.001)

        self.overall_progress = TimedProgressBar('normal',
                                                 'complete',
                                                 label='Overall',
                                                 label_width=13,
                                                 units=App.units,
                                                 done=.001)


        info = self.reaper.info()
        self.device_id = info['samd_id'][2:]

        info_text = [
            'Device Id: {}'.format(self.device_id),
            'SD Info: {} {} {} {} {}'.format(
                info['sd_mid'][2:],
                info['sd_oid'],
                info['sd_pnm'],
                info['sd_prv'],
                info['sd_mdt']),
            'SD Serial: {}'.format(info['sd_psn'][2:]),
            'SD Size: {:.2f} GB'.format(float(info['sd_size']) * 512 / 1e9),
        ]

        info_box = uw.LineBox(uw.Pile([uw.Text(t) for t in info_text]))
        self._status = uw.Text('-ready-')
        self.debug_message = uw.Text('')

        footer = uw.Text('r to run download | ESC or q to exit')
        self.footer = uw.AttrWrap(footer, 'footer')

        progress = uw.Frame(uw.ListBox([info_box,
                                        uw.Divider(),
                                        self.file_progress,
                                        uw.Divider(),
                                        uw.Divider(),
                                        self.overall_progress,
                                        uw.Divider(),
                                        uw.Divider(),
                                        self._status,
                                        uw.Divider(),
                                        self.debug_message,
                                        ]),
                            footer=self.footer)

        def keypress(key):
            if key in ('q', 'Q', 'esc'):
                raise uw.ExitMainLoop()
            elif key in ('r', 'R'):
                self.download()
                self.status('-ready-')

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
                self.file_progress.done = f['size']
                self.loop.draw_screen()

                def progress_fun(num_bytes, _):
                    self.file_progress.add_progress(num_bytes)
                    self.overall_progress.add_progress(num_bytes)
                    self.loop.draw_screen()

                data_dir = os.path.join(self.reaper.data_dir, self.device_id)

                sd_filename = f['name'].lstrip('/')
                local_filename = os.path.join(data_dir, sd_filename)
                dirname = os.path.dirname(local_filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                while os.path.exists(local_filename):
                    local_filename = increment_filename(local_filename)

                self.status('downloading {} to {} ...'.format(sd_filename,
                                                              local_filename))
                self.reaper.cp(sd_filename,
                               local_filename,
                               f['size'],
                               progress_fun)

    def debug(self, m):
        self.debug_message.set_text(m)
        self.loop.draw_screen()

def increment_filename(filename):
    parts = filename.rsplit('-', 1)
    try:
        counter = int(parts[1])
    except:
        counter = 0
    return '{}-{}'.format(parts[0], counter + 1)
