import cv2
import numpy as np
import torch


def read_image(image_path, mode='rgb'):
    """
    使用opencv读取图像
    :param image_path: 图像文件路径
    :param mode: 格式，'rgb', 'bgr', 'gray'
    :return: numpy.ndarray, dtype=np.uint8, shape=(h, w, c)
    """

    assert mode in ['rgb', 'bgr', 'gray'], "mode must be one of 'rgb', 'bgr', 'gray'"
    image_array = cv2.imread(image_path, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    if mode == "rgb":
        return cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    elif mode == 'gray':
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        gray = np.expand_dims(gray, axis=-1)
        return gray
    else:
        return image_array


def letter_box(image, size):
    """
    resize图片的同时保持宽高比不变
    :param image: numpy.ndarray
    :param size: list or tuple (h, w)
    :return:
    """
    h, w, _ = image.shape
    H, W = size
    scale = min(H / h, W / w)
    new_h, new_w = int(h * scale), int(w * scale)
    image = cv2.resize(src=image, dsize=(new_w, new_h), interpolation=cv2.INTER_NEAREST)
    top = (H - new_h) // 2     # 上边需要填充的像素数量
    bottom = H - new_h - top   # 下边需要填充的像素数量
    left = (W - new_w) // 2    # 左边需要填充的像素数量
    right = W - new_w - left   # 右边需要填充的像素数量
    new_image = cv2.copyMakeBorder(image, top, bottom, left, right, borderType=cv2.BORDER_CONSTANT,
                                   value=(128, 128, 128))
    return new_image, scale, [top, bottom, left, right]


def reverse_letter_box(h, w, input_size, boxes, xywh=True):
    """
    letter_box的逆变换
    :param h: 输入网络的图片的原始高度
    :param w: 输入网络的图片的原始宽度
    :param input_size: 网络的固定输入图片大小
    :param boxes: Tensor, shape: (..., 4(cx, cy, w, h))
    :param xywh: Bool, True：boxes是(cx, cy, w, h)格式, False: boxes是(xmin, ymin, xmax, ymax)格式
    :return: Tensor, shape: (..., 4(xmin, ymin, xmax, ymax))
    """
    # 转换为(xmin, ymin, xmax, ymax)格式
    if xywh:
        new_boxes = torch.cat((boxes[..., 0:2] - boxes[..., 2:4] / 2, boxes[..., 0:2] + boxes[..., 2:4] / 2), dim=-1)
    else:
        new_boxes = boxes.clone()
    new_boxes *= input_size

    scale = max(h / input_size, w / input_size)
    # 获取padding值
    top = (input_size - h / scale) // 2
    left = (input_size - w / scale) // 2
    # 减去padding值，就是相对于原始图片的原点位置
    new_boxes[..., 0] -= left
    new_boxes[..., 2] -= left
    new_boxes[..., 1] -= top
    new_boxes[..., 3] -= top
    # 缩放到原图尺寸
    new_boxes *= scale
    return new_boxes