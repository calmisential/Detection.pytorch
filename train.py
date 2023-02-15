import torch
import argparse


from trainer.ssd_train import SSDTrainer
from configs import get_cfg


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, required=True, help="experiment configure file name")
    parser.add_argument('--mode', type=str, required=True, help="train, test or predict")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    cfg, model_name = get_cfg(args.cfg)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    m = None
    if model_name == "ssd":
        m = SSDTrainer(cfg, device)

    if args.mode == "train":
        m.train()
    else:
        raise ValueError(f"不支持的模式：{args.mode}")


if __name__ == '__main__':
    main()