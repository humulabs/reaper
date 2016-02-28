import os
import locale
import datetime
import time
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

    locale.setlocale(locale.LC_ALL, '')

    def __init__(self, reaper, rm_after_download=True, auto_run=False):
        self.rm_after_download = rm_after_download
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
        self.file_count = uw.Text('')
        self.file_list = self.reaper.ls()
        self.update_file_count()

        info_text = [
            'Device Id: {}'.format(self.device_id),
            'Port: {}'.format(self.reaper.conn.name),
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

        info_left = uw.Pile(
            [self.device_name] +
            [uw.Text(t) for t in info_text] +
            [self.file_count])

        self.clock = Clock('')

        info_right = uw.Pile([uw.Padding(self.clock, align='right', width=13)])

        info_box = uw.LineBox(uw.Columns([info_left, info_right]))

        self._status = uw.Text('-ready-')
        self.debug_message = uw.Text('')

        commands = [('r', 'run download'),
                    ('n', 'set device name'),
                    ('c', 'set device clock'),
                    ('q', 'exit')]

        footer = uw.Text(' | '.join(['{} = {}'.format(key, text)
                                    for key, text in commands]))

        self.footer = uw.AttrWrap(footer, 'footer')

        main_view = uw.Frame(uw.ListBox([info_box,
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
            elif key in ('c', 'C'):
                self.set_device_clock()
            elif key in ('n', 'N'):
                self.status('Enter new Device Name')
                self.device_name.edit_mode()

        self.loop = uw.MainLoop(main_view,
                                App.palette,
                                unhandled_input=keypress)
        if auto_run:
            def run(*args, **kwargs):
                self.set_device_clock()
                time.sleep(.5)
                self.download()
            self.loop.set_alarm_in(0.5, run)
        else:
            self.loop.set_alarm_in(0.5, self.set_device_clock)

        self.loop.set_alarm_in(1, self.clock.refresh)
        self.loop.run()

    def set_device_clock(self, *args, **kwargs):
        self.status('Setting device clock to current UTC time ...')
        self.reaper.set_time()
        dt = self.reaper.get_time()
        self.status('Device clock set to {}\n\n-ready-'.format(dt))

    def status(self, msg):
        self._status.set_text(msg)
        self.clock.refresh_once()
        self.loop.draw_screen()

    def update_file_count(self):
        if self.file_list is None:
            t = 'n/a'
        else:
            t = locale.format('%d', len(self.file_list), grouping=True)
        self.file_count.set_text('# of Files: {}'.format(t))

    def download(self):
        if self.file_list is None:
            self.get_file_list()
        total_size = sum([f['size'] for f in self.file_list])
        self.overall_progress.done = total_size if total_size != 0 else .001
        self.status('starting download ...')
        for f in list(self.file_list):
            if f['size'] > 0:
                self.file_progress.reset()
                self.file_progress.done = f['size']
                self.loop.draw_screen()

                def progress_fun(num_bytes, _):
                    self.file_progress.add_progress(num_bytes)
                    self.overall_progress.add_progress(num_bytes)
                    self.clock.refresh_once()
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

            # remove file
            if self.rm_after_download:
                self.reaper.rm(f['name'])
            self.file_list = self.file_list[1:]
            self.update_file_count()
        self.status('-ready-')

    def debug(self, m):
        self.debug_message.set_text(m)
        self.loop.draw_screen()


def edit_field(caption, edit_text, handler):
    edit = uw.Edit(caption, edit_text)
    ef = EditField(edit, handler)
    return uw.BoxAdapter(ef, height=1)


class Clock(uw.Text):
    def refresh_once(self):
        now = datetime.datetime.utcnow()
        self.set_text('{}\n{}'.format(
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S UTC')))

    def refresh(self, loop=None, data=None):
        self.refresh_once()
        loop.set_alarm_in(1, self.refresh)


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
