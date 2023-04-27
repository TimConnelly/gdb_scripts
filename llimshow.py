#!/usr/bin/env python
"""
To import into lldb:
(adapt to your source path)
`command script import /path/to/llimshow.py`
`command script import llimshow.py`

To show the image:
`llimshow <image_name>`

numpy and matplotlib are required to be installed for the python install
used by LLDB/Clang. On macos you can use the `xcrun` command to
xcrun python3 -m pip install numpy matplotlib

TODO 
1. Handle non-continuous images
2. Figure out why plot window hangs
    - https://stackoverflow.com/questions/41295819/how-do-i-use-pyplot-to-display-data-when-a-breakpoint-is-hit-in-lldb
3. Access member variables
"""

import lldb

import matplotlib.pyplot as plt
import numpy as np


def llimshow(debugger, command, exe_ctx, results, internal_dict):
    # mat = lldb.frame.FindVariable(command)
    print(f"showing {command}")
    mat = exe_ctx.GetFrame().FindVariable(command)

    rows = int(mat.GetChildMemberWithName("rows").GetValue())
    cols = int(mat.GetChildMemberWithName("cols").GetValue())
    num_channels = int(mat.EvaluateExpression("channels()").value)
    elem_size = int(mat.EvaluateExpression("elemSize()").value)
    depth = int(mat.EvaluateExpression("depth()").value)
    total = int(mat.EvaluateExpression("total()").value)
    isContinuous = mat.EvaluateExpression("isContinuous()").value
    data_ptr = mat.GetChildMemberWithName("data")
    num_bytes = total*elem_size  #rows*cols*elem_size
    img = np.zeros(total)
    print(f'depth={depth}, total={total}, channels={num_channels}, elemSize={elem_size}, num_bytes={num_bytes}, isContinuous={isContinuous}')

    if depth == 0: # U8
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).uint8, copy=True)
    if depth == 1: # S8
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int16, copy=True)
    if depth == 2: # U16
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).uint16, copy=True)
    if depth == 3: # S16
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int16, copy=True)
    if depth == 4: # 32S
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int32, copy=True)
    if depth == 5: # 32F
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).floats, copy=False)
    if depth == 6: # 64F
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).double, copy=True)
    print(img.shape)

    img = img.reshape(rows, cols, num_channels)

    plt.imshow(img)
    plt.show()


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f llimshow.llimshow llimshow')
    print('The "llimshow" command has been added and is ready for use.')
