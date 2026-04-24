#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小云云地接 - 接口自动化测试一键运行脚本（Python版）

功能：运行测试 → 生成Allure报告 → 合并为可直接双击打开的单HTML文件
使用方式：python3 run_test.py

这个脚本是 run_test.sh 的Python版本，跨平台通用（Mac/Windows/Linux）。
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime


# ============================================================
# 路径配置
# ============================================================
# 获取当前脚本所在目录（即项目根目录）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# Allure原始结果数据目录
RESULTS_DIR = os.path.join(PROJECT_DIR, "reports", "allure-results")
# Allure生成的HTML报告目录
REPORT_DIR = os.path.join(PROJECT_DIR, "reports", "allure-report")
# 环境配置文件
ENV_FILE = os.path.join(PROJECT_DIR, "reports", "environment.properties")


# 添加配置项，允许指定运行的测试文件。默认运行所有测试文件
TEST_FILE = "testcases/test_query_clue_trip_list.py" 
# TEST_FILE = None


def print_header():
    """打印脚本头部信息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("")
    print("=" * 60)
    print("   小云云地接 - 接口自动化测试")
    print(f"   {now}")
    print("=" * 60)
    print("")


def check_command(cmd):
    """
    检查系统命令是否存在
    参数：cmd - 命令名称，如 'allure'
    返回：True/False
    """
    return shutil.which(cmd) is not None


def check_python_package(package_name):
    """
    检查Python包是否已安装
    参数：package_name - 包名，如 'allure_combine'
    返回：True/False
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name):
    """
    自动安装Python包
    参数：package_name - pip包名，如 'allure-combine'
    """
    print(f"  正在自动安装 {package_name}...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", package_name, "-q"],
        capture_output=True
    )


def step_check_env():
    """第一步：检查运行环境"""
    print("[1/5] 检查运行环境...")

    # 检查Python版本
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  ✓ Python: {py_version}")

    # 检查pytest
    if not check_python_package("pytest"):
        print("  ! pytest未安装，正在自动安装依赖...")
        req_file = os.path.join(PROJECT_DIR, "requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file, "-q"])
    print("  ✓ pytest: 已安装")

    # 检查allure命令行
    allure_ok = check_command("allure")
    if allure_ok:
        result = subprocess.run(["allure", "--version"], capture_output=True, text=True)
        print(f"  ✓ Allure命令行: {result.stdout.strip()}")
    else:
        print("  ! Allure命令行未安装（不影响测试运行）")
        print("    安装方式：brew install allure")

    # 检查allure-combine
    combine_ok = check_python_package("allure_combine")
    if not combine_ok:
        install_package("allure-combine")
        combine_ok = check_python_package("allure_combine")
    if combine_ok:
        print("  ✓ allure-combine: 已安装")
    else:
        print("  ! allure-combine安装失败，将跳过单文件合并步骤")

    print("")
    return allure_ok, combine_ok


def step_clean():
    """第二步：清理旧数据"""
    print("[2/5] 清理旧的测试数据...")

    # 删除旧的结果和报告目录
    if os.path.exists(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
    if os.path.exists(REPORT_DIR):
        shutil.rmtree(REPORT_DIR)

    # 重新创建结果目录
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("  ✓ 已清理旧数据")
    print("")


def step_run_tests():
    """第三步：运行测试用例"""
    print("[3/5] 开始运行测试用例...")
    print("-" * 60)

    # 如果 TEST_FILE 被设置，则只运行指定文件
    test_target = TEST_FILE if TEST_FILE else PROJECT_DIR
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", test_target, f"--alluredir={RESULTS_DIR}"],
        cwd=PROJECT_DIR
    )

    print("-" * 60)
    if result.returncode == 0:
        print("  ✓ 测试执行完成，全部通过！")
    else:
        print(f"  ! 测试执行完成，存在失败用例（退出码: {result.returncode}）")
    print("")

    return result.returncode


def step_generate_report(allure_ok):
    """第四步：生成Allure报告"""
    print("[4/5] 生成Allure报告...")

    # 复制环境配置文件到结果目录
    if os.path.exists(ENV_FILE):
        shutil.copy2(ENV_FILE, RESULTS_DIR)
        print("  ✓ 已复制环境配置文件")

    if not allure_ok:
        print("  ! 跳过报告生成（allure命令行未安装）")
        print(f"    测试结果数据已保存在: {RESULTS_DIR}")
        print(f"    安装allure后可手动生成: allure serve {RESULTS_DIR}")
        return False

    # 使用allure命令生成HTML报告
    subprocess.run(
        ["allure", "generate", RESULTS_DIR, "-o", REPORT_DIR, "--clean"],
        capture_output=True
    )
    print(f"  ✓ Allure HTML报告已生成: {REPORT_DIR}")
    print("")
    return True


def step_combine_report(combine_ok):
    """第五步：合并为单HTML文件"""
    print("[5/5] 合并为可直接打开的单HTML文件...")

    if not combine_ok:
        print("  ! 跳过合并步骤（allure-combine未安装）")
        return

    # 调用allure_combine合并报告
    subprocess.run(
        [sys.executable, "-m", "allure_combine.combine", REPORT_DIR],
        capture_output=True
    )

    complete_html = os.path.join(REPORT_DIR, "complete.html")
    if os.path.exists(complete_html):
        print(f"  ✓ 单文件报告已生成: {complete_html}")
    else:
        # 备选方式：直接调用allure_combine命令
        subprocess.run(["allure_combine", REPORT_DIR], capture_output=True)
        if os.path.exists(complete_html):
            print(f"  ✓ 单文件报告已生成: {complete_html}")
        else:
            print("  ! 合并失败，请手动执行: allure_combine reports/allure-report")


def print_summary(allure_ok, combine_ok, exit_code):
    """打印执行总结"""
    complete_html = os.path.join(REPORT_DIR, "complete.html")

    print("")
    print("=" * 60)
    print("   执行完成！")
    print("=" * 60)
    print("")
    print(f"  测试结果数据:  {RESULTS_DIR}")

    if allure_ok:
        print(f"  Allure报告目录: {REPORT_DIR}")

        if combine_ok and os.path.exists(complete_html):
            print("")
            print("  >>> 双击打开此文件查看报告 <<<")
            print(f"      {complete_html}")
            print("")

            # Mac和Windows上询问是否自动打开报告
            # Mac上询问是否自动打开
            # if sys.platform == "darwin":
            #     try:
            #         answer = input("  是否立即打开报告？(y/n): ").strip().lower()
            #         if answer == "y":
            #             subprocess.run(["open", complete_html])
            #     except (EOFError, KeyboardInterrupt):
            #         pass
            # # Windows上询问是否自动打开
            # elif sys.platform == "win32":
            #     try:
            #         answer = input("  是否立即打开报告？(y/n): ").strip().lower()
            #         if answer == "y":
            #             os.startfile(complete_html)
            #     except (EOFError, KeyboardInterrupt):
            #         pass

    print("")


def main():
    """主函数：串联所有步骤"""
    print_header()

    # 第一步：环境检查
    allure_ok, combine_ok = step_check_env()

    # 第二步：清理旧数据
    step_clean()

    # 第三步：运行测试
    exit_code = step_run_tests()

    # 第四步：生成Allure报告
    report_ok = step_generate_report(allure_ok)

    # 第五步：合并为单文件（仅在报告生成成功时执行）
    if report_ok:
        step_combine_report(combine_ok)

    # 打印总结
    print_summary(allure_ok, combine_ok, exit_code)

    # 返回pytest的退出码
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
