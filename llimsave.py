#!/usr/bin/env python
"""
To import into lldb:
(adapt to your source path)
`command script import /Users/10203633/dev/ScanKit/hue/scripts/llimsave.py`
`command script import llimsave.py`

To show the image:
`llimsave <image_name>`

To automatically load this script when running in xcode
1. Set a break point early in the program. I used `ScanPresenter.startCameraPreview`.
2. Right-click > Edit Breakpoint > Add Action
3. Ensure Action is set to "Debugger Command"
4. Add action "command script import <full path>/llimsave.py`
5. Check "Automatically continue after evaluating"

numpy and matplotlib are required to be installed for the python
used by LLDB/Clang. On macos you can use the `xcrun` command to use 
the correct python installation:
`xcrun python3 -m pip install numpy opencv-python`

TODO
1. Handle non-continuous images which are an ROI of another image. This shows up as a strange striped image.
3. Access member variables
4. Accept an image name as argument
5. Scale higher bit depths to U8 or use different output format
"""

import lldb

import numpy as np
import cv2
from pathlib import Path

def llimsave(debugger, command, exe_ctx, results, internal_dict):
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
    print(f'rows={rows}, cols={cols}')
    print(f'depth={depth}, total={total}, channels={num_channels}, elemSize={elem_size}, num_bytes={num_bytes}, isContinuous={isContinuous}')

    if depth == 0: # U8
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).uint8, copy=False)
    if depth == 1: # S8
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int16, copy=True)
    if depth == 2: # U16
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).uint16, copy=False)
    if depth == 3: # S16
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int16, copy=True)
    if depth == 4: # 32S
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).int32, copy=False)
    if depth == 5: # 32F
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).floats, copy=False)
    if depth == 6: # 64F
        img = np.array(data_ptr.GetPointeeData(0, num_bytes).double, copy=False)
    print(img.shape)

    img = img.reshape(rows, cols, num_channels)

    outpath = Path('/Users/10203633/dev/ScanKit/hue')/'debug_image.png'
    
    print(f'Writing image to {outpath.absolute()}')
    cv2.imwrite(outpath.absolute().__str__(), img)

    # to write out raw images
    # with open('/Users/10203633/src/hue/debug_image.arw', 'wb') as fo:
    #     fo.write(img)


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f llimsave.llimsave llimsave')
    print('The "llimsave" command has been added and is ready for use.')
