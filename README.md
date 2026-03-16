# 小红书博主及笔记爬虫

爬取小红书博主主页信息及笔记详情的 Python 工具。

## 功能

- ✅ 获取博主主页信息（用户名、简介、粉丝数、小红书 ID、IP 地址等）
- ✅ 获取博主主页下的笔记列表（笔记链接、标题、点赞量、类型等）
- ✅ 获取每篇笔记的详情（内容、点赞量、收藏量、转发量等）
- ✅ 自动请求延迟，避免触发反爬机制
- ✅ 支持导出 JSON 格式结果

## 安装

```bash
cd /home/ubuntu/.openclaw/workspace/projects/xhs-crawler
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python xhs_crawler.py --url <博主主页 URL> --cookie <Cookie>
```

### 完整参数

```bash
python xhs_crawler.py \
    --url "https://www.xiaohongshu.com/user/profile/5d2b3f4e00000000120367f4" \
    --cookie "your_cookie_here" \
    --max-notes 50 \
    --delay 2.0 \
    --output results.json
```

### 参数说明

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--url` | ✅ | 博主主页 URL | - |
| `--cookie` | ✅ | 小红书 Cookie | - |
| `--max-notes` | ❌ | 最大获取笔记数量 | 50 |
| `--delay` | ❌ | 请求间隔秒数 | 2.0 |
| `--output` | ❌ | 输出文件路径 | 控制台输出 |

## 获取 Cookie

1. 打开浏览器，访问 [小红书](https://www.xiaohongshu.com)
2. 登录你的账号
3. 按 F12 打开开发者工具
4. 切换到 **Network** 标签
5. 刷新页面，点击任意请求
6. 在 **Request Headers** 中找到 `Cookie` 字段，复制完整内容

## 输出格式

```json
{
  "crawl_time": "2026-03-16T20:15:00.000000",
  "user_url": "https://www.xiaohongshu.com/user/profile/xxx",
  "blogger_info": {
    "user_id": "5d2b3f4e00000000120367f4",
    "nickname": "博主名称",
    "avatar": "头像 URL",
    "desc": "个人简介",
    "following_count": 100,
    "fans_count": 10000,
    "liked_count": 50000,
    "ip_location": "上海",
    "gender": 1,
    "location": "上海"
  },
  "notes": [
    {
      "note_id": "65f1a2b3c4d5e6f7a8b9c0d1",
      "title": "笔记标题",
      "desc": "笔记描述",
      "cover_url": "封面图 URL",
      "like_count": 1000,
      "collect_count": 500,
      "comment_count": 100,
      "type": "note",
      "url": "https://www.xiaohongshu.com/explore/xxx",
      "create_time": 1710600000
    }
  ],
  "note_details": [
    {
      "note_id": "65f1a2b3c4d5e6f7a8b9c0d1",
      "title": "笔记标题",
      "content": "笔记内容",
      "type": "note",
      "author": {
        "user_id": "xxx",
        "nickname": "作者名",
        "avatar": "头像 URL"
      },
      "stats": {
        "like_count": 1000,
        "collect_count": 500,
        "comment_count": 100,
        "share_count": 50
      },
      "images": ["图片 URL 1", "图片 URL 2"],
      "video_url": "",
      "create_time": 1710600000,
      "ip_location": "上海",
      "url": "https://www.xiaohongshu.com/explore/xxx"
    }
  ]
}
```

## 注意事项

1. **Cookie 有效期**：Cookie 会过期，如遇到"未登录"错误，请重新获取 Cookie
2. **请求频率**：建议保持 2 秒以上的请求间隔，避免触发反爬
3. **账号安全**：不要使用主账号进行高频爬取，建议使用小号
4. **法律合规**：请遵守小红书用户协议，仅用于个人学习研究

## 数据说明

### 可获取的数据

| 数据类型 | 来源 | 说明 |
|---------|------|------|
| 博主信息 | 博主主页 | 用户名、简介、粉丝数、获赞数、IP 属地等 |
| 笔记列表 | 博主主页 | 笔记 ID、标题、点赞量、类型、封面图 |
| 笔记详情 | 博主主页 | 基于列表数据构建，包含封面图 |

### 受限数据

由于小红书对笔记详情页做了严格的反爬保护（API 返回 406），以下数据**无法获取**：

| 数据类型 | 原因 | 替代方案 |
|---------|------|---------|
| 视频链接 | 详情页 API 受限 | 使用封面图作为视频预览 |
| 完整图片列表 | 详情页 API 受限 | 使用封面图（第一张图片） |
| 正文内容 | 详情页 API 受限 | 使用标题和描述（如果有） |
| 收藏量/评论量 | 详情页 API 受限 | 仅获取点赞量 |

### 输出格式

**视频笔记：**
```json
{
  "type": "video",
  "images": ["封面图 URL"],  // 视频预览图
  "video_url": ""  // 受限，为空
}
```

**图文笔记：**
```json
{
  "type": "note",
  "images": ["封面图 URL"],  // 第一张图片
  "video_url": ""
}
```

### 获取完整数据的方法

如果需要获取视频链接和完整图片列表，可以使用官方 MCP 服务：

1. 启动 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 服务
2. 使用 `xhs_client.py detail` 命令获取笔记详情

```bash
python skills/xiaohongshu-mcp/scripts/xhs_client.py detail <note_id> <xsec_token>
```

## 常见问题

### Q: 提示"用户未登录"怎么办？
A: Cookie 可能已过期或失效，请重新获取 Cookie。确保在登录状态下复制完整的 Cookie 字符串。

### Q: 爬取速度慢怎么办？
A: 可以通过 `--delay` 参数调整请求间隔，但建议不要低于 1 秒，否则可能触发反爬。

### Q: 可以爬取多少篇笔记？
A: 理论上无限制，但建议单次不超过 100 篇，避免账号风险。

## License

MIT
