import torch
import time

def main():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    
    if not torch.cuda.is_available():
        print("CUDA 不可用！请确认你安装的是支持 CUDA 的 PyTorch 版本。")
        return

    # 输出 GPU 数量及名称
    num_devices = torch.cuda.device_count()
    print("Detected GPU count:", num_devices)
    for i in range(num_devices):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

    # 在 GPU 上创建一个张量，并进行简单运算测试
    device = torch.device("cuda")
    print("\n开始测试 GPU 计算性能...")
    # 创建一个随机张量，并进行一次矩阵乘法
    a = torch.rand((2000, 2000), device=device)
    b = torch.rand((2000, 2000), device=device)

    torch.cuda.synchronize()  # 确保之前操作完成
    start = time.time()
    c = torch.matmul(a, b)
    torch.cuda.synchronize()  # 等待运算完成
    elapsed = time.time() - start

    print(f"矩阵乘法耗时: {elapsed:.6f} 秒")
    print("运算结果张量大小:", c.size())
    # 显示前 5 个元素
    print("结果张量（展平后前 5 个元素）:", c.view(-1)[:5])

if __name__ == "__main__":
    main()
