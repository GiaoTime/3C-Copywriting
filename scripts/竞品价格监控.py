#!/usr/bin/env python3
"""
竞品价格监控脚本
用于自动收集竞品价格信息，支持京东、天猫、拼多多平台
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

class PriceMonitor:
    """价格监控类"""
    
    def __init__(self, product_name: str, competitors: List[Dict]):
        """
        初始化价格监控
        
        Args:
            product_name: 产品名称
            competitors: 竞品列表，每个竞品包含name和url
        """
        self.product_name = product_name
        self.competitors = competitors
        self.results = []
        
    def fetch_jd_price(self, url: str) -> Optional[float]:
        """获取京东价格"""
        try:
            # 模拟浏览器请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析价格（简化示例，实际需要根据页面结构调整）
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 京东价格选择器示例
            price_selectors = [
                '.price.J-p-100000000000',  # 京东价格class
                'span.p-price',  # 另一种价格class
                'div.price'  # 通用价格div
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    # 提取数字
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text)
                    if price_match:
                        price = float(price_match.group().replace(',', ''))
                        return price
            
            return None
            
        except Exception as e:
            print(f"获取京东价格失败: {e}")
            return None
    
    def fetch_tmall_price(self, url: str) -> Optional[float]:
        """获取天猫价格"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 天猫价格选择器
            price_selectors = [
                '.tm-price',  # 天猫价格class
                'span.ui-price',  # 另一种价格class
                'div.tb-rmb-num'  # 淘宝价格
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text)
                    if price_match:
                        price = float(price_match.group().replace(',', ''))
                        return price
            
            return None
            
        except Exception as e:
            print(f"获取天猫价格失败: {e}")
            return None
    
    def monitor_prices(self) -> List[Dict]:
        """监控所有竞品价格"""
        results = []
        
        for competitor in self.competitors:
            print(f"正在监控: {competitor['name']}")
            
            price = None
            if 'jd.com' in competitor['url']:
                price = self.fetch_jd_price(competitor['url'])
            elif 'tmall.com' in competitor['url'] or 'taobao.com' in competitor['url']:
                price = self.fetch_tmall_price(competitor['url'])
            else:
                print(f"不支持的平台: {competitor['url']}")
            
            result = {
                'name': competitor['name'],
                'url': competitor['url'],
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'platform': '京东' if 'jd.com' in competitor['url'] else '天猫' if 'tmall.com' in competitor['url'] else '其他'
            }
            
            results.append(result)
            
            # 避免请求过快
            time.sleep(1)
        
        self.results = results
        return results
    
    def save_results(self, filename: str = None):
        """保存监控结果"""
        if filename is None:
            filename = f"price_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'product': self.product_name,
            'monitor_time': datetime.now().isoformat(),
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {filename}")
        return filename
    
    def generate_report(self) -> str:
        """生成价格监控报告"""
        if not self.results:
            return "暂无监控数据"
        
        report_lines = [
            f"# 价格监控报告 - {self.product_name}",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 竞品价格对比",
            "",
            "| 竞品名称 | 平台 | 价格(元) | 监控时间 |",
            "|----------|------|----------|----------|",
        ]
        
        for result in self.results:
            price_str = f"{result['price']:.2f}" if result['price'] else "获取失败"
            report_lines.append(f"| {result['name']} | {result['platform']} | {price_str} | {result['timestamp'][:19]} |")
        
        report_lines.extend([
            "",
            "## 价格分析",
            "",
            "### 价格区间",
            f"- 最高价: {max(r['price'] for r in self.results if r['price']):.2f}元",
            f"- 最低价: {min(r['price'] for r in self.results if r['price']):.2f}元",
            f"- 平均价: {sum(r['price'] for r in self.results if r['price'])/len([r for r in self.results if r['price']]):.2f}元",
            "",
            "### 监控建议",
            "1. 定期监控价格变化趋势",
            "2. 关注促销活动时间节点",
            "3. 对比不同平台价格差异",
            "4. 分析价格与销量的关系",
        ])
        
        return "\n".join(report_lines)


def main():
    """示例使用"""
    # 示例竞品数据
    competitors = [
        {
            'name': 'iPhone 16 Pro 256GB',
            'url': 'https://item.jd.com/100000000000.html'  # 示例URL
        },
        {
            'name': '三星 Galaxy S24 Ultra',
            'url': 'https://detail.tmall.com/item.htm?id=6000000000000'  # 示例URL
        },
        {
            'name': '小米14 Ultra',
            'url': 'https://item.jd.com/200000000000.html'  # 示例URL
        }
    ]
    
    # 创建监控器
    monitor = PriceMonitor(
        product_name='iPhone 16 Pro',
        competitors=competitors
    )
    
    # 执行监控
    print("开始价格监控...")
    results = monitor.monitor_prices()
    
    # 保存结果
    monitor.save_results()
    
    # 生成报告
    report = monitor.generate_report()
    print("\n" + report)
    
    # 保存报告
    report_filename = f"price_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_filename}")


if __name__ == '__main__':
    main()