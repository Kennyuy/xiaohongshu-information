#!/usr/bin/env python3
"""
Xiaohongshu Blogger & Notes Crawler (网页解析版)
爬取小红书博主主页信息及笔记详情

Usage:
    python xhs_crawler.py --url <博主主页 URL> --cookie <Cookie>
    python xhs_crawler.py --url <博主主页 URL> --cookie <Cookie> --output results.json

Note: 由于小红书反爬机制，视频链接和完整图片列表需要从笔记详情页获取，
      但详情页数据受到保护。当前版本从博主主页获取基础数据：
      - 视频笔记：提供封面图（视频预览）
      - 图文笔记：提供封面图（第一张图片）
"""

import argparse
import json
import re
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any


class XHSCrawler:
    """小红书爬虫类（网页解析版）"""
    
    def __init__(self, cookie: str, delay: float = 2.0):
        self.cookie = cookie
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Cookie': cookie,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xiaohongshu.com/',
        })
        self.base_url = "https://www.xiaohongshu.com"
        
    def _random_delay(self, min_delay: float = None, max_delay: float = None):
        if min_delay is None:
            min_delay = self.delay * 0.5
        if max_delay is None:
            max_delay = self.delay * 1.5
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def _extract_user_id(self, url: str) -> Optional[str]:
        patterns = [r'/user/profile/([a-zA-Z0-9]+)', r'user_id=([a-zA-Z0-9]+)']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_initial_state(self, url: str) -> Optional[Dict]:
        try:
            self._random_delay()
            resp = self.session.get(url, timeout=30)
            if resp.status_code != 200:
                return None
            html = resp.text
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});?</script>', html, re.DOTALL)
            if not match:
                return None
            data_str = match.group(1).replace('undefined', 'null')
            return json.loads(data_str)
        except Exception:
            return None
    
    def get_blogger_info(self, user_url: str) -> Optional[Dict[str, Any]]:
        user_id = self._extract_user_id(user_url)
        if not user_id:
            return None
        
        data = self._get_initial_state(user_url)
        if not data:
            return None
        
        try:
            user_page_data = data.get('user', {}).get('userPageData', {})
            basic_info = user_page_data.get('basicInfo', {})
            interactions = user_page_data.get('interactions', [])
            
            fans_count, following_count, liked_count = 0, 0, 0
            for interaction in interactions:
                count_str = str(interaction.get('count', '0'))
                if '万' in count_str:
                    count = float(count_str.replace('万', '')) * 10000
                elif '亿' in count_str:
                    count = float(count_str.replace('亿', '')) * 100000000
                else:
                    count = int(count_str.replace(',', '')) if count_str else 0
                
                if interaction.get('type') == 'fans':
                    fans_count = count
                elif interaction.get('type') == 'follows':
                    following_count = count
                elif interaction.get('type') == 'interaction':
                    liked_count = count
            
            return {
                'user_id': user_id,
                'nickname': basic_info.get('nickname', ''),
                'avatar': basic_info.get('images', ''),
                'desc': basic_info.get('desc', ''),
                'following_count': following_count,
                'fans_count': fans_count,
                'liked_count': liked_count,
                'ip_location': basic_info.get('ipLocation', ''),
                'gender': basic_info.get('gender', 0),
                'red_id': basic_info.get('redId', ''),
            }
        except Exception:
            return None
    
    def get_blogger_notes(self, user_url: str, max_notes: int = 50) -> List[Dict[str, Any]]:
        user_id = self._extract_user_id(user_url)
        if not user_id:
            return []
        
        data = self._get_initial_state(user_url)
        if not data:
            return []
        
        try:
            notes_data = data.get('user', {}).get('notes', [])
            all_notes = []
            for note_item in notes_data:
                if isinstance(note_item, list):
                    all_notes.extend(note_item)
                elif isinstance(note_item, dict):
                    all_notes.append(note_item)
            
            notes = []
            for note in all_notes[:max_notes]:
                if not isinstance(note, dict):
                    continue
                note_card = note.get('noteCard', {})
                interact_info = note_card.get('interactInfo', {})
                cover = note_card.get('cover', {})
                
                # 获取封面图 URL（优先使用 urlDefault）
                cover_url = cover.get('urlDefault') or cover.get('url')
                if not cover_url and cover.get('infoList'):
                    for img in cover.get('infoList', []):
                        if img.get('url'):
                            cover_url = img['url']
                            break
                
                # 解析点赞数
                liked_count_str = str(interact_info.get('likedCount', '0'))
                if liked_count_str.endswith('+'):
                    liked_count_str = liked_count_str[:-1]
                if '万' in liked_count_str:
                    liked_count = int(float(liked_count_str.replace('万', '')) * 10000)
                elif '亿' in liked_count_str:
                    liked_count = int(float(liked_count_str.replace('亿', '')) * 100000000)
                else:
                    try:
                        liked_count = int(liked_count_str.replace(',', '')) if liked_count_str else 0
                    except ValueError:
                        liked_count = 0
                
                note_type = note_card.get('type', 'note')
                
                notes.append({
                    'note_id': note.get('id', ''),
                    'title': note_card.get('displayTitle', note_card.get('title', '')),
                    'desc': note_card.get('desc', ''),
                    'cover_url': cover_url,
                    'like_count': liked_count,
                    'type': 'video' if note_type == 'video' else 'note',
                    'url': f"{self.base_url}/explore/{note.get('id', '')}",
                    'xsec_token': note_card.get('xsecToken', ''),
                })
            
            return notes
        except Exception:
            return []
    
    def crawl_all(self, user_url: str, max_notes: int = 50) -> Dict[str, Any]:
        print("=" * 60)
        print("🦞 小红书爬虫开始工作")
        print("=" * 60)
        
        result = {
            'crawl_time': datetime.now().isoformat(),
            'user_url': user_url,
            'blogger_info': None,
            'notes': [],
            'note_details': [],
        }
        
        # 1. 获取博主信息
        blogger_info = self.get_blogger_info(user_url)
        if not blogger_info:
            print("❌ 获取博主信息失败，终止爬取")
            return result
        result['blogger_info'] = blogger_info
        print(f"✅ 获取博主信息成功：{blogger_info['nickname']} (粉丝：{blogger_info['fans_count']})")
        
        # 2. 获取笔记列表
        notes_list = self.get_blogger_notes(user_url, max_notes)
        if not notes_list:
            print("⚠️ 未获取到笔记列表")
            return result
        result['notes'] = notes_list
        print(f"✅ 共获取 {len(notes_list)} 篇笔记")
        
        # 3. 构建笔记详情
        # 注意：由于小红书反爬，视频链接和完整图片列表无法从详情页获取
        # 视频笔记：images 包含封面图（视频预览）
        # 图文笔记：images 包含封面图（第一张图片）
        print(f"\n📖 整理笔记数据...")
        print("⚠️  注：详情页数据受限，视频笔记提供封面图，图文笔记提供封面图")
        
        for i, note in enumerate(notes_list, 1):
            # 构建媒体列表
            images = []
            if note['cover_url']:
                images.append(note['cover_url'])
            
            detail = {
                'note_id': note['note_id'],
                'title': note['title'],
                'content': note['desc'],
                'type': note['type'],
                'author': {
                    'user_id': blogger_info['user_id'],
                    'nickname': blogger_info['nickname'],
                    'avatar': blogger_info['avatar'],
                },
                'stats': {
                    'like_count': note['like_count'],
                    'collect_count': 0,
                    'comment_count': 0,
                    'share_count': 0,
                },
                'images': images,  # 视频=封面预览，图文=第一张图片
                'video_url': '',  # 详情页受限，无法获取
                'ip_location': blogger_info['ip_location'],
                'url': note['url'],
            }
            result['note_details'].append(detail)
            
            # 输出信息
            if note['type'] == 'video':
                print(f"   ✓ [{i}/{len(notes_list)}] 📹 {note['title'][:35]}... (封面图：{'有' if note['cover_url'] else '无'})")
            else:
                print(f"   ✓ [{i}/{len(notes_list)}] 📝 {note['title'][:35]}... (图片：{len(images)} 张)")
        
        print("\n" + "=" * 60)
        print(f"✅ 爬取完成！共获取 {len(result['note_details'])} 篇笔记")
        print("=" * 60)
        
        return result


def main():
    parser = argparse.ArgumentParser(description='小红书博主及笔记爬虫')
    parser.add_argument('--url', required=True, help='博主主页 URL')
    parser.add_argument('--cookie', required=True, help='小红书 Cookie')
    parser.add_argument('--max-notes', type=int, default=50, help='最大获取笔记数量')
    parser.add_argument('--delay', type=float, default=2.0, help='请求间隔秒数')
    parser.add_argument('--output', help='输出文件路径 (JSON 格式)')
    
    args = parser.parse_args()
    
    crawler = XHSCrawler(cookie=args.cookie, delay=args.delay)
    result = crawler.crawl_all(args.url, args.max_notes)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📁 结果已保存到：{args.output}")
    else:
        print("\n📊 爬取结果预览:")
        output = json.dumps(result, ensure_ascii=False, indent=2)
        print(output[:3000])
        if len(output) > 3000:
            print("... (内容已截断，请使用 --output 参数保存到文件)")


if __name__ == '__main__':
    main()
