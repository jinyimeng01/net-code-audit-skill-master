#!/usr/bin/env python3
"""
.NET 组件漏洞扫描器
支持 packages.config, .csproj PackageReference, DLL 文件的依赖提取和漏洞检测
支持按目录层级分组输出
"""

import re
import os
import sys
import json
import yaml
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Dependency:
    """依赖信息"""
    package_id: str
    version: str
    source: str
    module: str = ""

    @property
    def coordinate(self) -> str:
        return f"{self.package_id}:{self.version}"


@dataclass
class Vulnerability:
    """漏洞信息"""
    name: str
    severity: str
    function: str
    description: str
    pattern: str
    matched_dependency: Optional[Dependency] = None


@dataclass
class ModuleResult:
    """单个模块的扫描结果"""
    module_path: str
    dependencies: List[Dependency] = field(default_factory=list)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)

    @property
    def severity_count(self) -> Dict[str, int]:
        count = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for v in self.vulnerabilities:
            count[v.severity] = count.get(v.severity, 0) + 1
        return count


@dataclass
class ScanResult:
    """扫描结果"""
    scan_target: str
    modules: Dict[str, ModuleResult] = field(default_factory=dict)

    @property
    def total_dependencies(self) -> int:
        return sum(len(m.dependencies) for m in self.modules.values())

    @property
    def total_vulnerabilities(self) -> int:
        return sum(len(m.vulnerabilities) for m in self.modules.values())

    @property
    def severity_count(self) -> Dict[str, int]:
        count = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for m in self.modules.values():
            for severity, c in m.severity_count.items():
                count[severity] += c
        return count

    def to_dict(self) -> dict:
        return {
            "scan_target": self.scan_target,
            "total_dependencies": self.total_dependencies,
            "total_vulnerabilities": self.total_vulnerabilities,
            "severity_count": self.severity_count,
            "modules": {
                path: {
                    "dependencies": [
                        {"coordinate": d.coordinate, "source": d.source}
                        for d in m.dependencies
                    ],
                    "vulnerabilities": [
                        {
                            "name": v.name,
                            "severity": v.severity,
                            "affected_component": v.function,
                            "description": v.description,
                            "matched_dependency": v.matched_dependency.coordinate if v.matched_dependency else None
                        }
                        for v in m.vulnerabilities
                    ]
                }
                for path, m in self.modules.items()
            }
        }


def get_module_path(file_path: str, base_path: str, group_depth: int = 2) -> str:
    try:
        rel_path = Path(file_path).relative_to(base_path)
        parts = rel_path.parts

        for i, part in enumerate(parts):
            if part in ('bin', 'obj', 'packages', 'node_modules', 'wwwroot'):
                return str(Path(*parts[:i])) if i > 0 else parts[0]

        if len(parts) > group_depth:
            return str(Path(*parts[:group_depth]))
        elif len(parts) > 1:
            return str(Path(*parts[:-1]))
        else:
            return str(rel_path.parent) if rel_path.parent != Path('.') else '.'
    except ValueError:
        return Path(file_path).parent.name


def extract_from_packages_config(config_path: str) -> List[Dependency]:
    """从 packages.config 提取依赖"""
    dependencies = []
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()

        ns = ''
        if root.tag.startswith('{'):
            ns = root.tag.split('}')[0] + '}'

        for pkg in root.findall(f'{ns}package'):
            pkg_id = pkg.get('id', '')
            version = pkg.get('version', '')

            if pkg_id and version:
                dependencies.append(Dependency(
                    package_id=pkg_id,
                    version=version,
                    source=config_path
                ))
    except Exception as e:
        print(f"[ERROR] 解析 packages.config 失败: {e}", file=sys.stderr)

    return dependencies


def extract_from_csproj(csproj_path: str) -> List[Dependency]:
    """从 .csproj 提取 PackageReference"""
    dependencies = []
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()

        ns = ''
        if root.tag.startswith('{'):
            ns = root.tag.split('}')[0] + '}'

        for item_group in root.iter(f'{ns}ItemGroup'):
            for pkg_ref in item_group.findall(f'{ns}PackageReference'):
                pkg_id = pkg_ref.get('Include', '')
                version = pkg_ref.get('Version', '')

                if not version:
                    ver_elem = pkg_ref.find(f'{ns}Version')
                    if ver_elem is not None:
                        version = ver_elem.text or ''

                if pkg_id and version:
                    dependencies.append(Dependency(
                        package_id=pkg_id,
                        version=version,
                        source=csproj_path
                    ))

        for prop_group in root.iter(f'{ns}PropertyGroup'):
            target_fw = prop_group.find(f'{ns}TargetFramework')
            if target_fw is not None and target_fw.text:
                pass
    except Exception as e:
        print(f"[ERROR] 解析 .csproj 失败: {e}", file=sys.stderr)

    return dependencies


def extract_from_dll(dll_path: str) -> List[Dependency]:
    """从 DLL 文件名提取依赖信息"""
    dependencies = []
    try:
        dll_name = Path(dll_path).stem
        match = re.match(r'^(.+?)\.(\d+\.\d+\.\d+(?:\.\d+)?)$', dll_name)
        if match:
            dependencies.append(Dependency(
                package_id=match.group(1),
                version=match.group(2),
                source=dll_path
            ))
        else:
            match = re.match(r'^(.+?)-(\d+\.\d+\.\d+(?:\.\d+)?)$', dll_name)
            if match:
                dependencies.append(Dependency(
                    package_id=match.group(1),
                    version=match.group(2),
                    source=dll_path
                ))
    except Exception as e:
        print(f"[WARN] 解析 DLL 文件名失败 {dll_path}: {e}", file=sys.stderr)

    return dependencies


def load_rules(rules_path: str) -> Dict:
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] 加载规则文件失败: {e}", file=sys.stderr)
        return {'rules': {}}


def scan_vulnerabilities(dependencies: List[Dependency], rules: Dict) -> List[Vulnerability]:
    vulnerabilities = []
    rules_data = rules.get('rules', {})

    for severity, rule_list in rules_data.items():
        if not isinstance(rule_list, list):
            continue

        for rule in rule_list:
            pattern = rule.get('pattern', '')
            if not pattern:
                continue

            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                continue

            for dep in dependencies:
                check_str = f"{dep.package_id}:{dep.version}"
                if regex.search(check_str):
                    vuln = Vulnerability(
                        name=rule.get('name', 'Unknown'),
                        severity=severity,
                        function=rule.get('function', ''),
                        description=rule.get('description', ''),
                        pattern=pattern,
                        matched_dependency=dep
                    )
                    vulnerabilities.append(vuln)

    return vulnerabilities


def scan_target(target_path: str, rules_path: str, group_depth: int = 2) -> ScanResult:
    result = ScanResult(scan_target=target_path)
    path = Path(target_path)
    rules = load_rules(rules_path)

    module_deps: Dict[str, List[Dependency]] = defaultdict(list)

    if path.is_file():
        module = '.'
        deps = []
        if path.name == 'packages.config':
            deps = extract_from_packages_config(str(path))
        elif path.suffix in ('.csproj',):
            deps = extract_from_csproj(str(path))
        elif path.suffix == '.dll':
            deps = extract_from_dll(str(path))

        for dep in deps:
            dep.module = module
        module_deps[module] = deps

    elif path.is_dir():
        base_path = str(path)

        for pkg_config in path.rglob('packages.config'):
            module = get_module_path(str(pkg_config), base_path, group_depth)
            deps = extract_from_packages_config(str(pkg_config))
            for dep in deps:
                dep.module = module
            module_deps[module].extend(deps)

        for csproj in path.rglob('*.csproj'):
            module = get_module_path(str(csproj), base_path, group_depth)
            deps = extract_from_csproj(str(csproj))
            for dep in deps:
                dep.module = module
            module_deps[module].extend(deps)

        for dll in path.rglob('*.dll'):
            module = get_module_path(str(dll), base_path, group_depth)
            deps = extract_from_dll(str(dll))
            for dep in deps:
                dep.module = module
            module_deps[module].extend(deps)

    for module, deps in module_deps.items():
        if deps:
            vulns = scan_vulnerabilities(deps, rules)
            result.modules[module] = ModuleResult(
                module_path=module,
                dependencies=deps,
                vulnerabilities=vulns
            )

    return result


def get_relative_source(source: str, scan_target: str) -> str:
    try:
        source_path = Path(source)
        target_path = Path(scan_target)
        if target_path.is_file():
            target_path = target_path.parent
        rel_path = source_path.relative_to(target_path)
        return str(rel_path)
    except ValueError:
        return Path(source).name


def format_markdown_report(result: ScanResult, show_deps: bool = True) -> str:
    lines = [
        f"# .NET 组件漏洞扫描报告",
        f"",
        f"**扫描目标**: `{result.scan_target}`",
        f"",
        f"## 扫描概览",
        f"",
        f"| 指标 | 数量 |",
        f"|------|------|",
        f"| 模块数量 | {len(result.modules)} |",
        f"| 依赖总数 | {result.total_dependencies} |",
        f"| 漏洞总数 | {result.total_vulnerabilities} |",
    ]

    severity_count = result.severity_count
    lines.extend([
        f"| Critical | {severity_count['critical']} |",
        f"| High | {severity_count['high']} |",
        f"| Medium | {severity_count['medium']} |",
        f"| Low | {severity_count['low']} |",
        f"",
    ])

    if len(result.modules) > 1:
        lines.append("## 模块风险摘要")
        lines.append("")
        lines.append("| 模块 | 依赖数 | Critical | High | Medium | Low | 总漏洞 |")
        lines.append("|------|--------|----------|------|--------|-----|--------|")

        sorted_modules = sorted(
            result.modules.items(),
            key=lambda x: (x[1].severity_count['critical'], x[1].severity_count['high'], len(x[1].vulnerabilities)),
            reverse=True
        )

        for module_path, module in sorted_modules:
            sc = module.severity_count
            total_vulns = len(module.vulnerabilities)
            lines.append(
                f"| `{module_path}` | {len(module.dependencies)} | "
                f"{sc['critical']} | {sc['high']} | {sc['medium']} | {sc['low']} | {total_vulns} |"
            )
        lines.append("")

    if result.total_vulnerabilities > 0:
        lines.append("## 漏洞详情（按模块分组）")
        lines.append("")

        sorted_modules = sorted(
            result.modules.items(),
            key=lambda x: (x[1].severity_count['critical'], x[1].severity_count['high']),
            reverse=True
        )

        for module_path, module in sorted_modules:
            if not module.vulnerabilities:
                continue

            lines.append(f"### {module_path}")
            lines.append("")

            for severity in ['critical', 'high', 'medium', 'low']:
                vulns = [v for v in module.vulnerabilities if v.severity == severity]
                if not vulns:
                    continue

                severity_label = {
                    'critical': 'Critical',
                    'high': 'High',
                    'medium': 'Medium',
                    'low': 'Low'
                }[severity]

                lines.append(f"#### {severity_label}")
                lines.append("")
                lines.append("| 组件 | 版本 | 来源文件 | 漏洞名称 | 描述 |")
                lines.append("|------|------|----------|----------|------|")

                seen = set()
                for v in vulns:
                    if v.matched_dependency:
                        key = (v.matched_dependency.package_id, v.matched_dependency.version, v.name)
                        if key in seen:
                            continue
                        seen.add(key)
                        desc = v.description
                        source_file = get_relative_source(v.matched_dependency.source, result.scan_target)
                        lines.append(
                            f"| {v.matched_dependency.package_id} | {v.matched_dependency.version} | "
                            f"{source_file} | {v.name} | {desc} |"
                        )
                lines.append("")

    else:
        lines.append("## 扫描结果")
        lines.append("")
        lines.append("未发现已知漏洞")
        lines.append("")

    if show_deps and result.total_dependencies > 0:
        lines.append("## 依赖列表（按模块分组）")
        lines.append("")

        for module_path, module in sorted(result.modules.items()):
            if not module.dependencies:
                continue

            lines.append(f"### {module_path}")
            lines.append("")
            lines.append("| 组件 | 版本 |")
            lines.append("|------|------|")

            seen = set()
            for dep in sorted(module.dependencies, key=lambda x: x.package_id):
                key = (dep.package_id, dep.version)
                if key in seen:
                    continue
                seen.add(key)
                lines.append(f"| {dep.package_id} | {dep.version} |")

            lines.append("")

    return "\n".join(lines)


def get_output_path(target_path: str, ext: str = 'md') -> Tuple[str, str]:
    from datetime import datetime

    path = Path(target_path)

    if path.is_file():
        project_name = path.parent.name
    else:
        project_name = path.name

    project_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', project_name)

    output_dir = os.path.join(f"{project_name}_audit", "vuln_report")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{project_name}_vuln_report_{timestamp}.{ext}"

    return output_dir, os.path.join(output_dir, filename)


def main():
    parser = argparse.ArgumentParser(description='.NET 组件漏洞扫描器（支持按模块分组）')
    parser.add_argument('target', help='扫描目标 (packages.config, .csproj, DLL 文件或目录)')
    parser.add_argument('--rules', '-r', required=True, help='漏洞规则文件路径')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='markdown', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--depth', '-d', type=int, default=2, help='模块分组深度 (默认: 2)')
    parser.add_argument('--no-deps', action='store_true', help='不显示依赖列表')
    parser.add_argument('--no-save', action='store_true', help='不保存文件，仅输出到终端')

    args = parser.parse_args()

    if not os.path.exists(args.target):
        print(f"[ERROR] 目标不存在: {args.target}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.rules):
        print(f"[ERROR] 规则文件不存在: {args.rules}", file=sys.stderr)
        sys.exit(1)

    result = scan_target(args.target, args.rules, args.depth)

    ext = 'json' if args.format == 'json' else 'md'
    if args.format == 'json':
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        output = format_markdown_report(result, show_deps=not args.no_deps)

    if args.no_save:
        print(output)
    elif args.output:
        output_path = args.output
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[INFO] 报告已保存到: {output_path}")
    else:
        output_dir, output_path = get_output_path(args.target, ext)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"[INFO] 创建输出目录: {output_dir}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"[INFO] 报告已保存到: {output_path}")

        print(f"\n扫描摘要:")
        print(f"   模块数量: {len(result.modules)}")
        print(f"   依赖总数: {result.total_dependencies}")
        print(f"   漏洞总数: {result.total_vulnerabilities}")
        sc = result.severity_count
        if sc['critical'] > 0:
            print(f"   Critical: {sc['critical']}")
        if sc['high'] > 0:
            print(f"   High: {sc['high']}")
        if sc['medium'] > 0:
            print(f"   Medium: {sc['medium']}")
        if sc['low'] > 0:
            print(f"   Low: {sc['low']}")


if __name__ == '__main__':
    main()
