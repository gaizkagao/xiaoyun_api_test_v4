#!/bin/bash
# ============================================================
# 小云云地接 - 接口自动化测试一键运行脚本
# 功能：运行测试 → 生成Allure报告 → 合并为可直接打开的单HTML文件
# 使用方式：在项目根目录下执行 ./run_test.sh
# ============================================================

# ---------- 颜色定义（让终端输出更清晰）----------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

# ---------- 路径定义 ----------
# 获取脚本所在目录（即项目根目录），确保无论从哪里执行都能正确找到文件
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="${PROJECT_DIR}/reports/allure-results"
REPORT_DIR="${PROJECT_DIR}/reports/allure-report"
ENV_FILE="${PROJECT_DIR}/reports/environment.properties"

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   小云云地接 - 接口自动化测试${NC}"
echo -e "${BLUE}   $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# ---------- 第一步：环境检查 ----------
echo -e "${YELLOW}[1/5] 检查运行环境...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到python3，请先安装Python3${NC}"
    exit 1
fi
echo "  ✓ Python3: $(python3 --version 2>&1)"

# 检查pytest
if ! python3 -m pytest --version &> /dev/null; then
    echo -e "${RED}错误：未找到pytest，正在自动安装依赖...${NC}"
    pip3 install -r "${PROJECT_DIR}/requirements.txt"
fi
echo "  ✓ Pytest: $(python3 -m pytest --version 2>&1 | head -1)"

# 检查allure命令行（非必须，没有也能用Python方式生成报告）
ALLURE_INSTALLED=false
if command -v allure &> /dev/null; then
    ALLURE_INSTALLED=true
    echo "  ✓ Allure: $(allure --version 2>&1)"
else
    echo -e "  ${YELLOW}! Allure命令行未安装（不影响测试运行，但无法生成标准报告）${NC}"
    echo -e "  ${YELLOW}  安装方式：brew install allure${NC}"
fi

# 检查allure-combine
COMBINE_INSTALLED=false
if python3 -c "import allure_combine" &> /dev/null; then
    COMBINE_INSTALLED=true
    echo "  ✓ allure-combine: 已安装"
else
    echo -e "  ${YELLOW}! allure-combine未安装，正在自动安装...${NC}"
    pip3 install allure-combine -q
    if python3 -c "import allure_combine" &> /dev/null; then
        COMBINE_INSTALLED=true
        echo "  ✓ allure-combine: 安装成功"
    else
        echo -e "  ${YELLOW}! allure-combine安装失败，将跳过单文件合并步骤${NC}"
    fi
fi

echo ""

# ---------- 第二步：清理旧数据 ----------
echo -e "${YELLOW}[2/5] 清理旧的测试数据...${NC}"
rm -rf "${RESULTS_DIR}" "${REPORT_DIR}"
mkdir -p "${RESULTS_DIR}"
echo "  ✓ 已清理旧数据"
echo ""

# ---------- 第三步：运行测试 ----------
echo -e "${YELLOW}[3/5] 开始运行测试用例...${NC}"
echo "------------------------------------------------------------"

cd "${PROJECT_DIR}"
python3 -m pytest -v --alluredir="${RESULTS_DIR}" 2>&1

# 保存pytest的退出码（0=全部通过，1=有失败）
PYTEST_EXIT_CODE=$?

echo "------------------------------------------------------------"
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo -e "  ${GREEN}✓ 测试执行完成，全部通过！${NC}"
else
    echo -e "  ${YELLOW}! 测试执行完成，存在失败用例（退出码: ${PYTEST_EXIT_CODE}）${NC}"
fi
echo ""

# ---------- 第四步：复制环境配置文件 ----------
echo -e "${YELLOW}[4/5] 生成Allure报告...${NC}"
if [ -f "${ENV_FILE}" ]; then
    cp "${ENV_FILE}" "${RESULTS_DIR}/"
    echo "  ✓ 已复制环境配置文件"
fi

# ---------- 第五步：生成报告 ----------
if [ "$ALLURE_INSTALLED" = true ]; then
    # 使用allure命令行生成标准HTML报告
    allure generate "${RESULTS_DIR}" -o "${REPORT_DIR}" --clean 2>&1
    echo "  ✓ Allure HTML报告已生成: ${REPORT_DIR}"

    # 合并为单文件
    if [ "$COMBINE_INSTALLED" = true ]; then
        echo ""
        echo -e "${YELLOW}[5/5] 合并为可直接打开的单HTML文件...${NC}"
        allure_combine "${REPORT_DIR}" 2>&1
        echo -e "  ${GREEN}✓ 单文件报告已生成: ${REPORT_DIR}/complete.html${NC}"
    else
        echo ""
        echo -e "${YELLOW}[5/5] 跳过合并步骤（allure-combine未安装）${NC}"
    fi
else
    echo -e "  ${YELLOW}! 跳过Allure报告生成（allure命令行未安装）${NC}"
    echo -e "  ${YELLOW}  测试结果数据已保存在: ${RESULTS_DIR}${NC}"
    echo -e "  ${YELLOW}  安装allure后可手动生成: allure serve ${RESULTS_DIR}${NC}"
fi

# ---------- 输出总结 ----------
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   执行完成！${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "  测试结果数据:  ${RESULTS_DIR}"

if [ "$ALLURE_INSTALLED" = true ]; then
    echo "  Allure报告目录: ${REPORT_DIR}"
    if [ "$COMBINE_INSTALLED" = true ] && [ -f "${REPORT_DIR}/complete.html" ]; then
        echo ""
        echo -e "  ${GREEN}>>> 双击打开此文件查看报告 <<<${NC}"
        echo -e "  ${GREEN}    ${REPORT_DIR}/complete.html${NC}"
        echo ""
        # Mac上自动用浏览器打开报告
        if [[ "$OSTYPE" == "darwin"* ]]; then
            read -p "  是否立即打开报告？(y/n): " OPEN_REPORT
            if [[ "$OPEN_REPORT" == "y" || "$OPEN_REPORT" == "Y" ]]; then
                open "${REPORT_DIR}/complete.html"
            fi
        fi
    fi
fi

echo ""
exit $PYTEST_EXIT_CODE
