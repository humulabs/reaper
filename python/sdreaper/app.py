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

        # Lookup device name, create a short one if not found
        device_name = self.reaper.get_device_name(self.device_id)
        if device_name is None:
            device_name = 'tag-{}'.format(self.device_id[-5:])
            self.reaper.set_device_name(device_name, self.device_id)

        # Invoked when editing device name is complete
        def device_name_handler(new_name):
            device_id = self.reaper.get_device_id(new_name)

            # name not changed
            if device_id == self.device_id:
                self.status('-ready-')
                return True

            # name not being used yet
            if device_id is None:
                self.reaper.set_device_name(new_name, self.device_id)
                self.status('-ready-')
                return True

            # name already being used
            else:
                msg = ('Device Name "{}" already used for device "{}"\n' +
                       'Please choose another name.').format(new_name,
                                                             device_id)
                self.status(msg)
                return False

        # device name edit field
        self.device_name = edit_field('Device Name: ',
                                      device_name,
                                      device_name_handler)

        info_box = uw.LineBox(uw.Pile(
            [self.device_name] + [uw.Text(t) for t in info_text]))
        self._status = uw.Text('-ready-')
        self.debug_message = uw.Text('')

        footer = uw.Text(
            'r = run download | c = change device name | q  = exit')
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
            if key in ('q', 'Q'):
                raise uw.ExitMainLoop()
            elif key in ('r', 'R'):
                self.download()
                self.status('-ready-')
            elif key in ('c', 'C'):
                self.status('Enter new Device Name')
                self.device_name.edit_mode()

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


def edit_field(caption, edit_text, handler):
    edit = uw.Edit(caption, edit_text)
    ef = EditField(edit, handler)
    return uw.BoxAdapter(ef, height=1)


class EditField(uw.Filler):
    def __init__(self, edit, handler):
        super(EditField, self).__init__(edit)
        self.edit_widget = edit
        self.handler = handler
        self.text_widget = uw.Text('')
        self.value = self.edit_widget.edit_text
        self.text_mode()

    def edit_mode(self):
        self.original_widget = self.edit_widget

    def text_mode(self):
        self.text_widget.set_text(self.edit_widget.caption + self.value)
        self.original_widget = self.text_widget

    def keypress(self, size, key):
        if key == 'esc':
            self.text_mode()
            self.handler(self.value)

        elif key == 'enter':
            if self.edit_widget.edit_text != self.value:
                if self.handler(self.edit_widget.edit_text):
                    self.value = self.edit_widget.edit_text
                    self.text_mode()
        else:
            return super(EditField, self).keypress(size, key)


def increment_filename(filename):
    parts = filename.rsplit('-', 1)
    try:
        counter = int(parts[1])
    except:
        counter = 0
    return '{}-{}'.format(parts[0], counter + 1)
