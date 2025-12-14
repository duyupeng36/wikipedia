#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess
import signal
import time
from multiprocessing import Event
import threading


def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description="启动并监控 npm 进程，退出时自动重启"
    )
    parser.add_argument("script", type=str, default="start", help="要运行的 npm 脚本名称，默认为 'start'")
    parser.add_argument("--restart", action="store_true", help="是否自动重启")
    parser.add_argument("--cwd", type=str, default=".", help="npm 项目目录，默认为当前目录")
    parser.add_argument("--max-restarts", type=int, default=-1, help="最大重启次数，-1 表示无限重启")
    args = parser.parse_args()
    return args


def run_npm_process(script, cwd, shutdown_event, restart_count):
    """
    运行 npm 进程
    """
    try:
        # 构建 npm 命令
        cmd = ["npm", "run", script]
        
        print(f"[INFO] 启动 npm: {' '.join(cmd)} (工作目录: {os.path.abspath(cwd)})")
        print(f"[INFO] 重启次数: {restart_count.value if hasattr(restart_count, 'value') else restart_count}")
        
        # 启动子进程
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 创建线程来读取输出
        def read_output():
            for line in iter(process.stdout.readline, ''):
                if shutdown_event.is_set():
                    break
                print(f"[npm] {line.strip()}")
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        # 等待进程结束或收到关闭信号
        while True:
            if shutdown_event.is_set():
                # 发送终止信号
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                break
            
            # 检查进程是否结束
            return_code = process.poll()
            if return_code is not None:
                print(f"[INFO] npm 进程退出，返回码: {return_code}")
                return return_code
            
            time.sleep(0.1)
            
    except Exception as e:
        print(f"[ERROR] 启动 npm 进程时出错: {e}")
        return -1


def monitor_process(script, cwd, restart_enabled, max_restarts):
    """
    监控并管理 npm 进程
    """
    shutdown_event = Event()
    
    # 设置信号处理
    def signal_handler(sig, frame):
        print(f"\n[INFO] 收到信号 {sig}，正在关闭...")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    restart_count = 0
    last_restart_time = 0
    min_restart_interval = 3  # 最小重启间隔（秒）
    
    try:
        while not shutdown_event.is_set():
            # 检查重启次数限制
            if restart_enabled and max_restarts >= 0 and restart_count >= max_restarts:
                print(f"[INFO] 达到最大重启次数限制 ({max_restarts})，停止重启")
                break
            
            # 确保重启间隔
            current_time = time.time()
            if current_time - last_restart_time < min_restart_interval:
                wait_time = min_restart_interval - (current_time - last_restart_time)
                print(f"[INFO] 等待 {wait_time:.1f} 秒后重启...")
                time.sleep(wait_time)
            
            # 记录重启次数
            restart_count += 1
            last_restart_time = time.time()
            
            # 运行 npm 进程
            return_code = run_npm_process(script, cwd, shutdown_event, restart_count)
            
            # 如果不启用重启，直接退出
            if not restart_enabled or shutdown_event.is_set():
                break
            
            # 根据返回码决定是否立即重启
            if return_code == 0:
                print("[INFO] npm 正常退出，等待 2 秒后重启...")
                time.sleep(2)
            else:
                print(f"[WARN] npm 异常退出 (code: {return_code})，立即重启...")
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断操作")
    except Exception as e:
        print(f"[ERROR] 监控进程出错: {e}")
    finally:
        if not shutdown_event.is_set():
            shutdown_event.set()
        print("[INFO] 监控进程已停止")


def main():
    args = parse_cmdline_args()
    
    print("=" * 60)
    print("npm 进程监控器")
    print("=" * 60)
    
    if args.restart:
        print(f"[INFO] 启用自动重启模式")
        if args.max_restarts >= 0:
            print(f"[INFO] 最大重启次数: {args.max_restarts}")
        else:
            print(f"[INFO] 重启次数: 无限")
    else:
        print(f"[INFO] 单次运行模式")
        args.max_restarts = 0
    
    print(f"[INFO] npm 脚本: {args.script}")
    print(f"[INFO] 工作目录: {os.path.abspath(args.cwd)}")
    print("-" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(args.cwd):
        print(f"[ERROR] 目录不存在: {args.cwd}")
        sys.exit(1)
    
    # 检查 package.json 是否存在
    package_json = os.path.join(args.cwd, "package.json")
    if not os.path.exists(package_json):
        print(f"[WARN] 未找到 package.json 在目录: {args.cwd}")
    
    # 启动监控进程
    monitor_process(
        script=args.script,
        cwd=args.cwd,
        restart_enabled=args.restart,
        max_restarts=args.max_restarts
    )


if __name__ == "__main__":
    main()