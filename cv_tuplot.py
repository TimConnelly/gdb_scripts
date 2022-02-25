"""
A text version of the GDB plotting script.

No GUI necessary. Using the plotext module, this
plots data directly in the terminal.
"""

import gdb
import plotext as plt

import struct


def chunker(seq, size):
    return (seq[pos:pos+size] for pos in range(0,len(seq), size))


class cv_tuplot(gdb.Command):
    """Plot an OpenCV Mat as a 1D plot"""

    def __init__(self):
        super(cv_tuplot, self).__init__('cv_tuplot', 
                                      gdb.COMMAND_SUPPORT,
                                      gdb.COMPLETE_SYMBOL)
    
    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        val = gdb.parse_and_eval(args[0])
        if str(val.type.strip_typedefs()) == 'IplImage *':
            gdb.write('IplImage type not supported\n', gdb.STDERR)
            return
            # img_info = self.get_iplimage_info(val)
        else:
            img_info = self.get_cvmat_info(val)
        
        if img_info:
            self.show_plot(*img_info)

        self.dont_repeat()

    def get_cvmat_info(self, val):
        flags = val['flags']
        depth = flags & 7
        channels = 1 + (flags >> 3) & 63;
        if depth == 0:
            cv_type_name = 'CV_8U'
            data_symbol = 'B'
        elif depth == 1:
            cv_type_name = 'CV_8S'
            data_symbol = 'b'
        elif depth == 2:
            cv_type_name = 'CV_16U'
            data_symbol = 'H'
        elif depth == 3:
            cv_type_name = 'CV_16S'
            data_symbol = 'h'
        elif depth == 4:
            cv_type_name = 'CV_32S'
            data_symbol = 'i'
        elif depth == 5:
            cv_type_name = 'CV_32F'
            data_symbol = 'f'
        elif depth == 6:
            cv_type_name = 'CV_64F'
            data_symbol = 'd'
        else:
            gdb.write('Unsupported cv::Mat depth\n', gdb.STDERR)
            return

        rows = val['rows']
        cols = val['cols']

        line_step = val['step']['p'][0]

        gdb.write(cv_type_name + ' with ' + str(channels) + ' channels, ' +
                  str(rows) + ' rows and ' +  str(cols) +' cols\n')

        data_address = str(val['data']).encode('utf-8').split()[0]
        data_address = int(data_address, 16)

        return (cols, rows, channels, line_step, data_address, data_symbol)
    
    @staticmethod
    def show_plot(width, height, num_channels, stride, data_address, data_symbol):
        """
        Copies the image to TBD and plots it
        """
        width = int(width)
        height = int(height)
        num_channels = int(num_channels)
        stride = int(stride)
        data_address = int(data_address)

        inferiors = gdb.inferiors()
        memory_data = inferiors[0].read_memory(data_address, stride*height)

        # Calculate the memory padding to change to the next image line.
        # Either due to memory alignment or a ROI.
        if data_symbol in ('b', 'B'):
            elem_size = 1
        elif data_symbol in ('h', 'H'):
            elem_size = 2
        elif data_symbol in ('i', 'f'):
            elem_size = 4
        elif data_symbol == 'd':
            elem_size = 8
        padding = stride - width * num_channels * elem_size

        image_data = []
        if num_channels == 1:
            mode = 'L'
            fmt = '%d%s%dx' % (width, data_symbol, padding)
            for line in chunker(memory_data, stride):
                image_data.extend(struct.unpack(fmt, line))
        else:
            gdb.write('Only 1 channel images are supported\n', gdb.STDERR)
            return
        
        plt.clc()
        plt.plot(image_data)
        plt.show()

cv_tuplot()
