import time
import torch

from configs import get_cfg
from models import SSD, CenterNet, YoloV3, Yolo7
from predict import ssd_decode, centernet_decode, yolov3_decode, yolo7_decode

# 权重文件位置
WEIGHTS = "saves/yolov7_weights.pth"
# ckpt有没有子级key，本项目保存的模型的state_dict()在checkpoint的"model" key下
SUBKEY = ""

# 测试图片路径的列表
IMAGE_PATHS = ["test/000000000471.jpg"]
# 配置文件路径
CONFIG = "configs/yolo7.py"

# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--cfg', type=str, required=True, help="experiment configure file name")
#     args = parser.parse_args()
#     return args


def detect_images(cfg, model_class, decode_fn, device):
    """
    检测多张图片中的目标
    :param cfg: 配置信息
    :param model_class:  网络模型的类名
    :param decode_fn: 解码函数名
    :param device: 设备
    :return:
    """
    model = model_class(cfg).to(device)
    ckpt = torch.load(WEIGHTS, map_location=device)
    if SUBKEY == "":
        model.load_state_dict(ckpt)
    elif SUBKEY == "model":
        model.load_state_dict(ckpt["model"])
    else:
        raise ValueError(f"Unsupported SUBKEY: {SUBKEY}")
    print(f"Loaded weights: {WEIGHTS}")
    for img in IMAGE_PATHS:
        decode_fn(cfg, model, img, print_on=True, save_result=True, device=device)


def main():
    t0 = time.time()
    cfg, model_name = get_cfg(CONFIG)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if model_name == "ssd":
        detect_images(cfg, SSD, ssd_decode.detect_one_image, device)
    elif model_name == "centernet":
        detect_images(cfg, CenterNet, centernet_decode.detect_one_image, device)
    elif model_name == "yolov3":
        detect_images(cfg, YoloV3, yolov3_decode.detect_one_image, device)
    elif model_name == "yolo7":
        detect_images(cfg, Yolo7, yolo7_decode.detect_one_image, device)

    print(f"Total time: {(time.time() - t0):.2f}s")


if __name__ == '__main__':
    main()
