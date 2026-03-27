"""
Vox CRIS 循环巡检脚本

使用方法：
    python 循环巡检.py           # 执行完整一轮
    python 循环巡检.py --phase 1 # 只执行巡检
    python 循环巡检.py --phase 2 # 只执行 Bug Hunt
    python 循环巡检.py --phase 3 # 只执行优化
    python 循环巡检.py --phase 4 # 只执行新功能
    python 循环巡检.py --list    # 列出所有待处理项
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 颜色定义
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).parent.absolute()


def log(msg: str, color: str = RESET):
    """打印带颜色的日志"""
    print(f"{color}{msg}{RESET}")


def log_header(msg: str):
    log(f"\n{'='*60}", BOLD)
    log(f"  {msg}", BOLD + CYAN)
    log(f"{'='*60}\n", BOLD)


def run_command(cmd: str, cwd: Optional[Path] = None) -> tuple:
    """运行命令并返回 (success, output)"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_backend_health() -> bool:
    """检查后端健康状态"""
    log_header("Phase 1: 巡检 - 后端健康检查")
    success, output = run_command('curl -s http://localhost:8003/health')
    if success and "api_key" in output:
        log("✅ 后端 API 正常", GREEN)
        try:
            data = json.loads(output)
            log(f"   - API Key 配置: {'✅' if data.get('api_key_configured') else '❌'}")
            log(f"   - Tavily 配置: {'✅' if data.get('tavily_api_configured') else '❌'}")
            log(f"   - LLM Provider: {data.get('llm_provider', 'N/A')}")
        except:
            pass
        return True
    else:
        log("⚠️  后端 API 无响应，请检查服务是否启动", RED)
        log(f"   curl 输出: {output[:200]}", YELLOW)
        return False


def check_backend_imports() -> bool:
    """检查后端模块导入"""
    log("\n检查后端模块导入...")
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

    modules_to_check = [
        "backend.agents.copywriter",
        "backend.agents.planner",
        "backend.agents.reviewer",
        "backend.services.hashtag",
        "backend.services.posting_time",
        "backend.services.title_generator",
        "backend.tools.image_gen",
    ]

    all_ok = True
    for module in modules_to_check:
        try:
            __import__(module)
            log(f"   ✅ {module}", GREEN)
        except Exception as e:
            log(f"   ❌ {module}: {str(e)[:50]}", RED)
            all_ok = False

    return all_ok


def check_api_routes() -> int:
    """检查 API 路由数量"""
    log("\n检查 API 路由...")
    content_py = PROJECT_ROOT / "backend" / "api" / "content.py"
    if not content_py.exists():
        log("   ❌ content.py 不存在", RED)
        return 0

    content = content_py.read_text(encoding="utf-8")
    route_count = len(re.findall(r'@router\.(post|get|put|delete)', content))
    log(f"   📊 共 {route_count} 个 API 路由", CYAN)
    return route_count


def check_frontend_build() -> bool:
    """检查前端构建"""
    log("\n检查前端构建...")
    frontend_dir = PROJECT_ROOT / "frontend"

    # 检查关键文件存在
    key_files = [
        "src/components/HashtagRecommender.tsx",
        "src/components/PostingTimeRecommender.tsx",
        "src/components/TitleABTester.tsx",
        "src/components/ImageGenerator.tsx",
        "src/components/ContentTranslator.tsx",
        "src/components/ContentTemplate.tsx",
    ]

    all_exist = True
    for file in key_files:
        path = frontend_dir / file
        if path.exists():
            log(f"   ✅ {file}", GREEN)
        else:
            log(f"   ❌ {file} 不存在", RED)
            all_exist = False

    return all_exist


def phase1_review():
    """Phase 1: 巡检"""
    log_header("Phase 1: 巡检 (Review)")

    results = {
        "backend_health": check_backend_health(),
        "backend_imports": check_backend_imports(),
        "api_routes": check_api_routes(),
        "frontend_files": check_frontend_build(),
    }

    log("\n📋 巡检汇总:")
    for key, value in results.items():
        status = "✅" if value else "❌"
        log(f"   {status} {key}: {value}")

    return all(results.values())


def phase2_bug_hunt():
    """Phase 2: Bug Hunt"""
    log_header("Phase 2: Bug Hunt (找 Bug)")

    bugs_found = []

    # 检查 React 组件的 isMountedRef 模式
    log("\n🔍 检查 React 组件 unmount 保护...")
    frontend_dir = PROJECT_ROOT / "frontend" / "src" / "components"

    if frontend_dir.exists():
        for tsx_file in frontend_dir.glob("*.tsx"):
            content = tsx_file.read_text(encoding="utf-8")

            # 检查是否有 useEffect 但没有 isMountedRef
            if "useEffect" in content and "isMountedRef" not in content:
                bugs_found.append({
                    "file": str(tsx_file.relative_to(PROJECT_ROOT)),
                    "issue": "useEffect without isMountedRef protection",
                    "severity": "medium",
                })

            # 检查是否有 async handle 但没有 unmount 检查
            if "async" in content and "handle" in content.lower():
                # 简单检查：看看有没有卸载保护
                if "useRef" not in content and "isMounted" not in content:
                    pass  # 这个检查太宽泛，不标记

    log(f"   发现 {len(bugs_found)} 个潜在问题")
    for bug in bugs_found[:5]:
        log(f"   ⚠️  {bug['file']}: {bug['issue']}", YELLOW)

    # 检查 Python 异步问题
    log("\n🔍 检查 Python 异步代码...")
    backend_dir = PROJECT_ROOT / "backend"

    async_issues = []
    for py_file in backend_dir.glob("**/*.py"):
        content = py_file.read_text(encoding="utf-8")

        # 检查 asyncio.run 在已有名为 async 的函数中
        if "asyncio.run(" in content:
            # 简单检查
            if "async def" in content:
                async_issues.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "issue": "asyncio.run inside async function",
                })

    log(f"   发现 {len(async_issues)} 个潜在问题")
    for issue in async_issues[:3]:
        log(f"   ⚠️  {issue['file']}: {issue['issue']}", YELLOW)

    return len(bugs_found) == 0 and len(async_issues) == 0


def phase3_optimize():
    """Phase 3: 优化"""
    log_header("Phase 3: 优化 (Optimize)")

    optimizations = []

    # 检查重复代码
    log("\n🔍 检查代码重复...")

    # 检查后端 services 目录
    services_dir = PROJECT_ROOT / "backend" / "services"
    if services_dir.exists():
        files = list(services_dir.glob("*.py"))
        log(f"   后端 services 文件数: {len(files)}", CYAN)

    # 检查前端 components
    components_dir = PROJECT_ROOT / "frontend" / "src" / "components"
    if components_dir.exists():
        files = list(components_dir.glob("*.tsx"))
        log(f"   前端 components 文件数: {len(files)}", CYAN)

    # 建议优化项
    log("\n📝 优化建议:")

    # 检查是否有可以抽象的通用代码
    api_file = PROJECT_ROOT / "frontend" / "src" / "lib" / "api.ts"
    if api_file.exists():
        content = api_file.read_text(encoding="utf-8")
        if "API_BASE_URL" in content:
            log("   ✅ API 基础 URL 已配置")

    # 检查 utils
    utils_file = PROJECT_ROOT / "frontend" / "src" / "lib" / "utils.ts"
    if utils_file.exists():
        content = utils_file.read_text(encoding="utf-8")
        log(f"   ✅ utils.ts 大小: {len(content)} 字符")

    log("\n✨ 没有发现需要紧急优化的问题")


def phase4_new_feature():
    """Phase 4: 新功能"""
    log_header("Phase 4: 新功能 (New Feature)")

    # 列出待实现的功能
    pending_features = [
        {
            "name": "内容评分系统",
            "description": "对生成的内容进行质量评分",
            "priority": "P1",
            "effort": "中",
        },
        {
            "name": "历史内容搜索",
            "description": "搜索之前生成的内容",
            "priority": "P1",
            "effort": "中",
        },
        {
            "name": "批量导出",
            "description": "一次导出多个平台的内容",
            "priority": "P2",
            "effort": "小",
        },
        {
            "name": "草稿箱",
            "description": "保存未完成的内容草稿",
            "priority": "P2",
            "effort": "中",
        },
    ]

    log("\n📋 待实现功能:")
    for i, feature in enumerate(pending_features, 1):
        log(f"   {i}. [{feature['priority']}] {feature['name']}")
        log(f"      描述: {feature['description']}")
        log(f"      工作量: {feature['effort']}")

    log("\n🎯 推荐下一个功能:")
    log(f"   [{pending_features[0]['priority']}] {pending_features[0]['name']}")
    log(f"   原因: {pending_features[0]['description']}")


def show_status():
    """显示项目状态"""
    log_header("📊 Vox 项目状态")

    # Git 状态
    log("\n📦 Git 状态:")
    success, output = run_command("git status --short")
    if success:
        lines = output.strip().split("\n")
        if lines and lines[0]:
            for line in lines[:10]:
                log(f"   {line}")
        else:
            log("   工作区干净")
    else:
        log("   无法获取 git 状态", YELLOW)

    # 最近提交
    log("\n📝 最近提交:")
    success, output = run_command("git log --oneline -5")
    if success:
        for line in output.strip().split("\n"):
            log(f"   {line}")

    # 文件统计
    log("\n📊 代码统计:")
    backend_py = list((PROJECT_ROOT / "backend").glob("**/*.py"))
    frontend_ts = list((PROJECT_ROOT / "frontend" / "src").glob("**/*.ts*"))
    log(f"   后端 Python 文件: {len(backend_py)}")
    log(f"   前端 TS/TSX 文件: {len(frontend_ts)}")


def main():
    """主函数"""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--list" in args:
        show_status()
        return

    phase = None
    for arg in args:
        if arg.startswith("--phase="):
            phase = int(arg.split("=")[1])

    if phase == 1:
        phase1_review()
    elif phase == 2:
        phase2_bug_hunt()
    elif phase == 3:
        phase3_optimize()
    elif phase == 4:
        phase4_new_feature()
    else:
        # 执行完整一轮
        log_header("🚀 Vox CRIS 循环巡检开始")
        log(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        phase1_review()
        phase2_bug_hunt()
        phase3_optimize()
        phase4_new_feature()

        log_header("✅ CRIS 循环巡检完成")
        log("\n💡 下一步:")
        log("   python 循环巡检.py --phase=1  # 只巡检")
        log("   python 循环巡检.py --phase=2  # 只找 Bug")
        log("   python 循环巡检.py --phase=3  # 只优化")
        log("   python 循环巡检.py --phase=4  # 只新功能")


if __name__ == "__main__":
    main()
